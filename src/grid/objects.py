from __future__ import annotations

from typing import TYPE_CHECKING, Any
import uuid

from PySide6.QtCore import QPoint, QPointF
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem

from src.utils import find_instance, get_media_path
from .defs import DIR2OFFSET, Direction, Orientation, TLMode, TLState, SignType, DIR2ROT

if TYPE_CHECKING:
    from .scene import GridScene, SpatialGrid


class ZValues:
    Road = 0
    Crossing = 5
    Pedestrian = 10
    Car = 15
    Sign = 20
    TrafficLight = 25


def sprite_prop():
    private = f"__{uuid.uuid4()}"

    def getter(self):
        return getattr(self, private)

    def setter(self, value):
        setattr(self, private, value)
        if self.scene() is not None:
            self.refresh_sprite()

    return property(getter, setter)  # type: ignore


class GridObject(QGraphicsPixmapItem):
    def __init__(
        self,
        is_persistent: bool = True,
    ):
        super().__init__()

        flags = (
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        self.setFlags(flags)

        self.is_persistent = is_persistent
        self.cell: QPoint | None = None

    @property
    def grid_scene(self) -> "GridScene":
        return super().scene()  # type: ignore

    @property
    def spatial_grid(self) -> "SpatialGrid":
        return self.grid_scene.grid

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            return self.process_position_change(value)
        return super().itemChange(change, value)

    def process_position_change(self, value: QPoint | QPointF) -> QPoint | QPointF:
        if self.grid_scene is None:
            return value

        new_cell = self.grid_scene.scene_pos_to_cell(value)

        if self.cell == new_cell:
            return self.pos()

        if not self.validate_placement(new_cell):
            if self.cell is None:
                self.grid_scene.removeItem(self)
            return self.pos()

        if self.cell is not None:
            self.spatial_grid.remove_at(self.cell, self)

        self.spatial_grid.append_to(new_cell, self)
        self.cell = new_cell

        return self.grid_scene.cell_to_scene_pos(self.cell)

    def validate_placement(self, new_cell: QPoint) -> bool:
        return True

    def refresh_sprite(self) -> None:
        self.setPixmap(self.get_pixmap())

    def tick(self, dt: float) -> None:
        pass

    def get_pixmap(self) -> QPixmap:
        raise NotImplementedError()

    def serialize(self) -> dict:
        return {}

    @classmethod
    def deserialize(cls, data: dict) -> GridObject:
        return cls(**data)


class Car(GridObject):
    direction = sprite_prop()

    def __init__(self, direction: Direction = Direction.N) -> None:
        super().__init__(is_persistent=False)

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
        is_on_road = bool(
            find_instance(of=(Road, Crossroad), in_=self.spatial_grid.get_at(new_cell))
        )
        return is_on_road


class Road(GridObject):
    direction = sprite_prop()

    def __init__(self, direction: Direction = Direction.N) -> None:
        super().__init__()

        self.direction = direction
        self.setZValue(ZValues.Road)

    def get_pixmap(self) -> QPixmap:
        pm = QPixmap(get_media_path(f"Rvertical"))
        return pm.transformed(QTransform().rotate(DIR2ROT.get(self.direction, 0)))

    def validate_placement(self, new_cell: QPoint) -> bool:
        is_on_road = bool(
            find_instance(of=(Road, Crossroad), in_=self.spatial_grid.get_at(new_cell))
        )
        return not is_on_road

    def get_next_cell(self) -> QPoint | None:
        if not self.cell:
            return None

        return self.cell + DIR2OFFSET[self.direction]

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

    def validate_placement(self, new_cell: QPoint) -> bool:
        is_on_road = bool(
            find_instance(of=(Road, Crossroad), in_=self.spatial_grid.get_at(new_cell))
        )
        return not is_on_road


class TrafficLight(GridObject):
    STATE_DURATION = 5.0

    state = sprite_prop()

    def __init__(self, state: TLState = TLState.RED) -> None:
        super().__init__()

        self.state = state
        self.mode: TLMode = TLMode.TIME

        self.setZValue(ZValues.TrafficLight)

        self.elapsed: float = 0.0

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"TL{self.state}"))

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
        if self.cell is None:
            return
        neighbors = self.spatial_grid.get_neighbors(self.cell)
        target = TLState.GREEN if find_instance(of=Car, in_=neighbors) else TLState.RED
        if self.state != target:
            self.state = target
            self.elapsed = 0.0

    def validate_placement(self, new_cell: QPoint) -> bool:
        road = find_instance(of=Road, in_=self.spatial_grid.get_at(new_cell))
        if not road:
            return False

        road_next_cell = road.get_next_cell()
        if not road_next_cell:
            return False

        return bool(
            find_instance(of=Crossroad, in_=self.spatial_grid.get_at(road_next_cell))
        )


class Pedestrian(GridObject):
    def __init__(self) -> None:
        super().__init__()

        self.setZValue(ZValues.Pedestrian)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"Pedestrain"))

    def validate_placement(self, new_cell: QPoint) -> bool:
        near_crossing = bool(
            find_instance(of=Crossing, in_=self.spatial_grid.get_neighbors(new_cell))
        )
        on_road = bool(find_instance(of=Road, in_=self.spatial_grid.get_at(new_cell)))
        return near_crossing and not on_road


class Crossing(GridObject):
    orientation = sprite_prop()

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
        on_road = bool(find_instance(of=Road, in_=self.spatial_grid.get_at(new_cell)))
        return on_road


class Sign(GridObject):
    sign_type = sprite_prop()

    def __init__(self, sign_type: SignType = SignType.BLOCK) -> None:
        super().__init__()

        self.sign_type = sign_type
        self.setZValue(ZValues.Sign)

    def get_pixmap(self) -> QPixmap:
        return QPixmap(get_media_path(f"{self.sign_type}"))

    def validate_placement(self, new_cell: QPoint) -> bool:
        on_road = bool(
            find_instance(of=(Road, Crossroad), in_=self.spatial_grid.get_at(new_cell))
        )
        return on_road

    def serialize(self) -> dict:
        return {"sign_type": self.sign_type.name}

    @classmethod
    def deserialize(cls, data: dict) -> Sign:
        sign_type = SignType[data["sign_type"]]
        return cls(sign_type)
