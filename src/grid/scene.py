import math
from PySide6.QtCore import QObject, QPoint, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene

from .objects import GridObject


class Grid[T]:
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

    def find_near(
        self,
        pos: QPoint,
        distance: int = 3,
    ) -> list[T]:
        cx, cy = self._to_index(pos)
        size = len(self.grid)

        results: list[T] = []

        for y in range(max(0, cy - distance), min(size, cy + distance + 1)):
            for x in range(max(0, cx - distance), min(size, cx + distance + 1)):
                results.extend(self.grid[y][x])

        return results

    def _to_index(self, pos: QPoint) -> tuple[int, int]:
        x = pos.x() + self.offset.x()
        y = pos.y() + self.offset.y()
        return x, y


class GridScene(QGraphicsScene):
    def __init__(
        self,
        parent: QObject | None = None,
        clear_color: QColor = QColor("#ffffff"),
        grid_color: QColor = QColor("#e0e0e0"),
        cell_size: int = 35,
        grid_size: int = 50,
    ) -> None:
        super().__init__(parent)

        self.clear_color = clear_color
        self.grid_color = grid_color
        self.cell_size = cell_size
        self.grid_size = grid_size

        size = self.grid_size * self.cell_size

        self.grid: Grid[GridObject] = Grid(self.grid_size)

        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

    def pos_to_cell(self, scene_pos: QPoint | QPointF) -> QPoint:
        return QPoint(
            math.floor(scene_pos.x() / self.cell_size),
            math.floor(scene_pos.y() / self.cell_size),
        )

    def cell_to_pos(self, cell: QPoint) -> QPoint:
        return QPoint(
            cell.x() * self.cell_size,
            cell.y() * self.cell_size,
        )

    def add_item(self, item: GridObject, grid_pos: QPoint) -> None:
        super().addItem(item)

        pos = grid_pos * self.cell_size

        item.setPos(pos)
        item.refresh()

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, self.clear_color)

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
