from enum import StrEnum
from typing import TYPE_CHECKING
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem

from src.utils import get_media_path

if TYPE_CHECKING:
    from src.grid import GridScene


class GridObject(QGraphicsPixmapItem):
    def __init__(self, movable: bool = False):
        super().__init__()

        flags = (
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        if movable:
            flags |= QGraphicsItem.GraphicsItemFlag.ItemIsMovable

        self.setFlags(flags)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            return self.scene().snap_to_cell(value)
        return super().itemChange(change, value)

    def scene(self) -> "GridScene":
        return super().scene()  # type: ignore

    def refresh(self) -> None:
        self.setPixmap(self.get_pixmap())

    def get_pixmap(self) -> QPixmap:
        raise NotImplementedError()


class Direction(StrEnum):
    N = "vertical"
    S = "bottom"
    W = "left"
    E = "right"


class Car(GridObject):
    def __init__(self, direction: Direction = Direction.N) -> None:
        super().__init__(movable=True)

        self.direction = direction

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"C{self.direction}"))


DIR2ROT: dict[Direction, int] = {
    Direction.N: 0,
    Direction.S: 180,
    Direction.W: -90,
    Direction.E: 90,
}


class Road(GridObject):
    def __init__(self, direction: Direction = Direction.N) -> None:
        super().__init__(movable=False)

        self.direction: Direction = direction

    def get_pixmap(self) -> QPixmap:
        pm = QPixmap(get_media_path(f"Rvertical"))
        pm.transformed(QTransform().rotate(DIR2ROT.get(self.direction, 0)))

        return pm


class Crossroad(GridObject):
    def __init__(self) -> None:
        super().__init__(movable=False)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"Rcrossroads"))


class TrafficLightState(StrEnum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


class TrafficLight(GridObject):
    def __init__(self, state: TrafficLightState = TrafficLightState.RED) -> None:
        super().__init__(movable=False)

        self.state: TrafficLightState = state

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"TL{self.state}"))


class Pedestrian(GridObject):
    def __init__(self) -> None:
        super().__init__(movable=False)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"Pedestrian"))


class Orientation(StrEnum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class Crossing(GridObject):
    def __init__(
        self, orientation: Orientation = Orientation.VERTICAL
    ) -> None:
        super().__init__(movable=False)

        self.orientation = orientation

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"Z{self.orientation}"))


class SignType(StrEnum):
    BLOCK = "Block"
    STOP = "Stop"
    START = "Start"


class Sign(GridObject):
    def __init__(self, sign_type: SignType = SignType.BLOCK) -> None:
        super().__init__(movable=False)

        self.sign_type = sign_type

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"{self.sign_type}"))
