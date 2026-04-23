from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING
from PySide6.QtCore import QPoint, QPointF
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem

from src.utils import find_instance, get_media_path

if TYPE_CHECKING:
    from .scene import GridScene


class ZValues:
    Road = 0
    Crossing = 5
    Pedestrian = 10
    Car = 15
    Sign = 20
    TrafficLight = 25


class GridObject(QGraphicsPixmapItem):
    def __init__(
        self,
        persistent: bool = True,
    ):
        super().__init__()

        flags = (
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        self.setFlags(flags)

        self.persistent = persistent
        self.cell: QPoint | None = None

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            return self.process_position_change(value)
        return super().itemChange(change, value)

    def process_position_change(self, value: QPoint | QPointF) -> QPoint | QPointF:
        new_cell = self.scene.pos_to_cell(value)

        if self.scene is None:
            return value

        if self.cell == new_cell:
            return self.pos()

        if not self.validate_placement(new_cell):
            if self.cell is None:
                self.scene.removeItem(self)
            return self.pos()

        if self.cell is not None:
            self.scene.grid.remove_at(self.cell, self)

        self.scene.grid.append_to(new_cell, self)
        self.cell = new_cell

        return self.scene.cell_to_pos(self.cell)

    def validate_placement(self, new_cell: QPoint) -> bool:
        return True

    @property
    def scene(self) -> "GridScene":
        return super().scene()  # type: ignore

    def refresh(self) -> None:
        self.setPixmap(self.get_pixmap())

    def get_pixmap(self) -> QPixmap:
        raise NotImplementedError()

    def serialize(self) -> dict:
        return {}

    @classmethod
    def deserialize(cls, data: dict) -> GridObject:
        return cls(**data)


class Direction(StrEnum):
    N = "vertical"
    S = "bottom"
    W = "left"
    E = "right"


class Car(GridObject):
    def __init__(self, direction: Direction = Direction.N) -> None:
        super().__init__(persistent=False)

        self.direction = direction
        self.setZValue(ZValues.Car)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"C{self.direction}"))

    def serialize(self) -> dict:
        return {"direction": self.direction.name}

    @classmethod
    def deserialize(cls, data: dict) -> Car:
        direction = Direction[data["direction"]]
        return cls(direction)

    def validate_placement(self, new_cell: QPoint) -> bool:
        road = find_instance(of=Road, in_=self.scene.grid.get_at(new_cell))
        return bool(road)


DIR2ROT: dict[Direction, int] = {
    Direction.N: 0,
    Direction.S: 180,
    Direction.W: -90,
    Direction.E: 90,
}


class Road(GridObject):
    def __init__(self, direction: Direction = Direction.N) -> None:
        super().__init__()

        self.direction: Direction = direction
        self.setZValue(ZValues.Road)

    def get_pixmap(self) -> QPixmap:
        pm = QPixmap(get_media_path(f"Rvertical"))
        return pm.transformed(QTransform().rotate(DIR2ROT.get(self.direction, 0)))

    def serialize(self) -> dict:
        return {"direction": self.direction.name}

    @classmethod
    def deserialize(cls, data: dict) -> Road:
        direction = Direction[data["direction"]]
        return cls(direction)


class Crossroad(GridObject):
    def __init__(self) -> None:
        super().__init__()

        self.setZValue(ZValues.Road)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"Rcrossroads"))


class TrafficLightState(StrEnum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


class TrafficLight(GridObject):
    def __init__(self, state: TrafficLightState = TrafficLightState.RED) -> None:
        super().__init__()

        self.state: TrafficLightState = state
        self.setZValue(ZValues.TrafficLight)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"TL{self.state}"))

    def validate_placement(self, new_cell: QPoint) -> bool:
        near_crossroad = find_instance(
            of=Crossroad, in_=self.scene.grid.find_near(new_cell, 1)
        )
        on_road = find_instance(of=Road, in_=self.scene.grid.get_at(new_cell))
        return bool(near_crossroad) and bool(on_road)


class Pedestrian(GridObject):
    def __init__(self) -> None:
        super().__init__()

        self.setZValue(ZValues.Pedestrian)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"Pedestrain"))

    def validate_placement(self, new_cell: QPoint) -> bool:
        near_road = find_instance(of=Road, in_=self.scene.grid.find_near(new_cell, 1))
        on_road = find_instance(of=Road, in_=self.scene.grid.get_at(new_cell))
        return bool(near_road) and not bool(on_road)


class Orientation(StrEnum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class Crossing(GridObject):
    def __init__(self, orientation: Orientation = Orientation.VERTICAL) -> None:
        super().__init__()

        self.orientation = orientation
        self.setZValue(ZValues.Crossing)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"Z{self.orientation}"))

    def serialize(self) -> dict:
        return {"orientation": self.orientation.name}

    @classmethod
    def deserialize(cls, data: dict) -> Crossing:
        orientation = Orientation[data["orientation"]]
        return cls(orientation)

    def validate_placement(self, new_cell: QPoint) -> bool:
        road = find_instance(of=Road, in_=self.scene.grid.get_at(new_cell))
        return bool(road)


class SignType(StrEnum):
    BLOCK = "Block"
    STOP = "Stop"
    START = "Start"


class Sign(GridObject):
    def __init__(self, sign_type: SignType = SignType.BLOCK) -> None:
        super().__init__()

        self.sign_type = sign_type
        self.setZValue(ZValues.Sign)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"{self.sign_type}"))

    def validate_placement(self, new_cell: QPoint) -> bool:
        road = find_instance(of=Road, in_=self.scene.grid.get_at(new_cell))
        return bool(road)

    def serialize(self) -> dict:
        return {"sign_type": self.sign_type.name}

    @classmethod
    def deserialize(cls, data: dict) -> Sign:
        sign_type = SignType[data["sign_type"]]
        return cls(sign_type)
