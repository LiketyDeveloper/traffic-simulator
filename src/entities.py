from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsSceneMouseEvent,
)

from src.utils import getMediaPath, scenePosToCell, cellToScenePos, snapScenePosToCell
from src.constants import DIR2ROT, ZIndexes
from src.types import Direction, SignType, TLMode, TLState

if TYPE_CHECKING:
    from world import World


class BaseEntity(QGraphicsPixmapItem):
    def __init__(self, z_index: int = 0) -> None:
        super().__init__()

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

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

        self.setCell(cell)

    def setCell(self, cell: QPoint) -> None:
        self.cell = cell

        print(cell)
        self.setPos(cellToScenePos(cell))

    def validatePlacement(self, cell: QPoint, world: "World") -> bool:
        existing_items = world.get(cell, types=type(self))
        return len(existing_items) == 0


class Road(BaseEntity):
    def __init__(self, z_index: int = 0) -> None:
        super().__init__(ZIndexes.Road)


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

        self.elapsed: float = 0.0

    @property
    def state(self) -> TLState:
        return self._state

    @state.setter
    def state(self, state: TLState) -> None:
        self._state = state

        pm = QPixmap(getMediaPath(self.STATE2IMG[self.state]))
        self.setPixmap(pm)

    def _flip(self) -> None:
        self.state = TLState.RED if self.state == TLState.GREEN else TLState.GREEN
        self.elapsed = 0.0

    def tick(self, dt: float) -> None:
        if self.mode == TLMode.TIME:
            self._tick_time(dt)
        elif self.mode == TLMode.TRANSPORT:
            self._tick_transport()

    def _tick_time(self, dt: float) -> None:
        self.elapsed += dt
        if self.elapsed >= self.STATE_DURATION:
            self._flip()

    def _tick_transport(self) -> None:
        pass


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
