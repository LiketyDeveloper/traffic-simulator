from __future__ import annotations

import random
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsSceneMouseEvent,
)

from src.constants import DIR2OFFSET, DIR2ROT, ZIndexes
from src.database import eventDb
from src.types import Direction, Orientation, SignType, TLMode, TLState
from src.utils import (
    cellToScenePos,
    getDirectionFromOffset,
    getMediaPath,
    scenePosToCell,
    snapScenePosToCell,
)

if TYPE_CHECKING:
    from world import World


class BaseEntity(QGraphicsPixmapItem):
    def __init__(self, z_index: int = 0, movable: bool = True) -> None:
        super().__init__()

        flags = QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        if movable:
            flags |= QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        self.setFlags(flags)

        self.setZValue(z_index)
        self.cell = scenePosToCell(self.pos())

    @property
    def world(self) -> "World":
        return self.scene()  # type: ignore

    def tick(self, dt: float) -> None:
        pass

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        cell = snapScenePosToCell(self.pos())

        if cell == self.cell or not self.validatePlacement(cell, self.world):
            self.setCell(self.cell)
            return
        eventDb.log(
            f"Move {type(self).__name__} from ({self.cell.x()}, {self.cell.y()}) to ({cell.x()}, {cell.y()})"
        )

        self.setCell(cell)

    def setCell(self, cell: QPoint) -> None:
        self.cell = cell

        self.setPos(cellToScenePos(cell))

    def validatePlacement(self, cell: QPoint, world: "World") -> bool:
        existingItems = world.get(cell, types=type(self))
        return len(existingItems) == 0


class Car(BaseEntity):
    DIR2IMG = {
        Direction.N: "{}vertical",
        Direction.S: "{}bottom",
        Direction.E: "{}right",
        Direction.W: "{}left",
    }

    def __init__(self, path: list[Road] | None = None, speed: float = 3) -> None:
        super().__init__(ZIndexes.Car, movable=False)

        self.color = random.choice(["C", "BC"])
        self.direction = Direction.N

        self.speed = speed
        self.path = path or []

    @property
    def path(self) -> list[Road]:
        return self._path

    @path.setter
    def path(self, path: list[Road]) -> None:
        self._path = path
        self.pathIndex = 0
        self.progress = 0.0

        if not path:
            return

        first = path[self.pathIndex]
        if isinstance(first, StraightRoad):
            self.direction = first.direction
        self.setCell(first.cell)
        self.pathIndex = 1

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction) -> None:
        self._direction = direction

        pm = QPixmap(getMediaPath(self.DIR2IMG[self.direction].format(self.color)))
        self.setPixmap(pm)

    @property
    def finished(self) -> bool:
        return self.pathIndex >= len(self.path)

    def shouldStop(self) -> bool:
        if self.finished:
            return False

        next_road = self.path[self.pathIndex]
        next_cell = next_road.cell

        if not next_road.canBePassed():
            return True

        cars_ahead = self.world.get(next_cell, Car)
        if cars_ahead:
            return True

        tls = self.world.get(self.cell, TrafficLight)
        for tl in tls:
            if tl.state == TLState.RED:
                return True

        return False

    def tick(self, dt: float) -> None:
        if self.finished:
            self.world.removeItem(self)
            return

        if self.shouldStop():
            return

        self.progress += self.speed * dt
        if self.progress >= 1:
            next_road = self.path[self.pathIndex]
            self.direction = getDirectionFromOffset(next_road.cell - self.cell)
            self.progress -= 1
            self.setCell(next_road.cell)
            self.pathIndex += 1


class Road(BaseEntity):
    def __init__(self, z_index: int = 0) -> None:
        super().__init__(ZIndexes.Road)

    def canBePassed(self) -> bool:
        sign = self.world.get(self.cell, Sign)
        if sign:
            if sign[0].type in (SignType.BLOCK, SignType.STOP):
                return False
        return True

    def validatePlacement(self, cell: QPoint, world: "World") -> bool:
        onRoad = len(world.get(cell, types=Road)) > 0
        return not onRoad


class StraightRoad(Road):
    def __init__(self, direction: Direction = Direction.N) -> None:
        super().__init__()

        self.direction = direction

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction) -> None:
        self._direction = direction

        pm = QPixmap(getMediaPath("Rvertical"))
        pm = pm.transformed(QTransform().rotate(DIR2ROT[self.direction]))

        self.setPixmap(pm)

    def getCellOffset(self, offset: int = 1) -> QPoint:
        return self.cell + DIR2OFFSET[self.direction] * offset


class CrossRoad(Road):
    def __init__(self, direction: Direction = Direction.N) -> None:
        super().__init__()
        self.setPixmap(QPixmap(getMediaPath("Rcrossroads")))


class TrafficLight(BaseEntity):
    STATE_DURATION = 5.0

    STATE2IMG = {
        TLState.GREEN: "TLgreen",
        TLState.YELLOW: "TLyellow",
        TLState.RED: "TLred",
    }

    def __init__(self, state: TLState = TLState.RED) -> None:
        super().__init__(ZIndexes.TrafficLight)

        self.state = state
        self.mode: TLMode = TLMode.TIME

    @property
    def state(self) -> TLState:
        return self._state

    @state.setter
    def state(self, state: TLState) -> None:
        self._state = state
        self.elapsed: float = 0.0

        pm = QPixmap(getMediaPath(self.STATE2IMG[self.state]))
        self.setPixmap(pm)

    def flip(self) -> None:
        self.state = TLState.RED if self.state == TLState.GREEN else TLState.GREEN
        self.elapsed = 0

    def tick(self, dt: float) -> None:
        match self.mode:
            case TLMode.TIME:
                self.tickTime(dt)
            case TLMode.TRANSPORT:
                self.tickTransport()
            case TLMode.ALARM:
                self.tickAlarm()

    def tickTime(self, dt: float) -> None:
        self.elapsed += dt
        if self.elapsed >= self.STATE_DURATION:
            self.flip()

    def tickTransport(self) -> None:
        road = self.world.get(self.cell, StraightRoad)
        if not road:
            return
        road = road[0]

        carNearby = self.world.get(self.cell, Car)
        carNearby.extend(self.world.get(road.getCellOffset(-1), Car))

        target = TLState.GREEN if len(carNearby) > 0 else TLState.RED

        if self.state != target:
            self.state = target
            self.elapsed = 0

    def tickAlarm(self) -> None:
        self.state = TLState.YELLOW

    def validatePlacement(self, cell: QPoint, world: "World") -> bool:
        straightRoads = world.get(cell, StraightRoad)
        if not straightRoads:
            return False

        nxtCell = straightRoads[0].getCellOffset(1)
        crossroadOnNxt = len(world.get(nxtCell, CrossRoad)) > 0
        return super().validatePlacement(cell, world) and crossroadOnNxt


class Pedestrian(BaseEntity):
    def __init__(self, interval: int = 5) -> None:
        super().__init__(ZIndexes.Pedestrian)

        self.setPixmap(QPixmap(getMediaPath(f"Pedestrain")))

    def validatePlacement(self, cell: QPoint, world: "World") -> bool:
        nextToCrossing = len(world.getNeighbors(cell, Crossing)) > 0
        onRoad = len(world.get(cell, Road)) > 0
        return super().validatePlacement(cell, world) and nextToCrossing and not onRoad


class Crossing(BaseEntity):
    ORNT2IMG = {
        Orientation.HORIZONTAL: "Zhorizontal",
        Orientation.VERTICAL: "Zvertical",
    }

    def __init__(self, orientation: Orientation = Orientation.VERTICAL) -> None:
        super().__init__()

        self.orientation = orientation

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @orientation.setter
    def orientation(self, orientation: Orientation) -> None:
        self._orientation = orientation
        pm = QPixmap(getMediaPath(self.ORNT2IMG[self.orientation]))
        self.setPixmap(pm)

    def validatePlacement(self, cell: QPoint, world: "World") -> bool:
        onStraightRoad = len(world.get(cell, StraightRoad)) > 0
        return super().validatePlacement(cell, world) and onStraightRoad


class Sign(BaseEntity):
    TYPE2IMG = {SignType.BLOCK: "Block", SignType.START: "Start", SignType.STOP: "Stop"}

    def __init__(self, type: SignType = SignType.BLOCK) -> None:
        super().__init__(ZIndexes.Sign)

        self.type = type

    @property
    def type(self) -> SignType:
        return self._type

    @type.setter
    def type(self, type: SignType) -> None:
        self._type = type

        pm = QPixmap(getMediaPath(self.TYPE2IMG[self.type]))
        self.setPixmap(pm)

    def validatePlacement(self, cell: QPoint, world: "World") -> bool:
        onRoad = len(world.get(cell, Road)) > 0
        return super().validatePlacement(cell, world) and onRoad
