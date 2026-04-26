import math
import time

from PySide6.QtCore import QObject, QPoint, QPointF, QRectF, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene

from .defs import DIR2OFFSET
from .objects import GridObject


class SpatialGrid[T]:
    def __init__(self, size: int) -> None:
        self.offset = QPoint(size // 2, size // 2)
        self.grid: list[list[list[T]]] = [
            [[] for _ in range(size)] for _ in range(size)
        ]

    def get_at(self, pos: QPoint) -> list[T]:
        x, y = self._to_index(pos)
        return self.grid[y][x]

    def append_to(self, pos: QPoint, obj: T) -> None:
        self.get_at(pos).append(obj)

    def remove_at(self, pos: QPoint, obj: T) -> None:
        try:
            self.get_at(pos).remove(obj)
        except ValueError:
            pass

    def get_neighbors(self, pos: QPoint) -> list[T]:
        neighbors = []
        for _, offset in DIR2OFFSET.items():
            neighbors.extend(self.get_at(pos + offset))

        return neighbors

    def _to_index(self, pos: QPoint) -> tuple[int, int]:
        x = pos.x() + self.offset.x()
        y = pos.y() + self.offset.y()
        return x, y


class GridScene(QGraphicsScene):
    def __init__(
        self,
        parent: QObject | None = None,
        background_color: QColor = QColor("#ffffff"),
        grid_color: QColor = QColor("#e0e0e0"),
        cell_size: int = 35,
        grid_dim: int = 50,
        tick_ms: int = 50,
    ) -> None:
        super().__init__(parent)

        self.background_color = background_color
        self.grid_color = grid_color
        self.cell_size = cell_size
        self.grid_dim = grid_dim

        size = self.grid_dim * self.cell_size

        self.grid: SpatialGrid[GridObject] = SpatialGrid(self.grid_dim)

        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(tick_ms)
        self.sim_timer.timeout.connect(self.on_tick)
        self.sim_timer.start()

    def scene_pos_to_cell(self, scene_pos: QPoint | QPointF) -> QPoint:
        return QPoint(
            math.floor(scene_pos.x() / self.cell_size),
            math.floor(scene_pos.y() / self.cell_size),
        )

    def cell_to_scene_pos(self, cell: QPoint) -> QPoint:
        return QPoint(
            cell.x() * self.cell_size,
            cell.y() * self.cell_size,
        )

    def add_item(self, item: GridObject, grid_pos: QPoint) -> None:
        super().addItem(item)

        pos = grid_pos * self.cell_size

        item.setPos(pos)
        item.refresh_sprite()

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, self.background_color)

        painter.setPen(QPen(self.grid_color, 0.4))

        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        first_left = left - (left % self.cell_size)
        first_top = top - (top % self.cell_size)

        for x in range(first_left, right, self.cell_size):
            painter.drawLine(x, top, x, bottom)

        for y in range(first_top, bottom, self.cell_size):
            painter.drawLine(left, y, right, y)

    def on_tick(self) -> None:
        dt = self.sim_timer.interval() / 1000

        for item in self.items():
            if isinstance(item, GridObject):
                item.tick(dt)

    def get_items[T](self, cls: type[T] | list[type[T]]) -> list[T]:
        return [obj for obj in self.items() if isinstance(obj, cls)] # type: ignore
