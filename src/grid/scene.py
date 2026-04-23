import math
from PySide6.QtCore import QObject, QPoint, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene

from .objects import GridObject


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

        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

    def pos_to_cell(self, scene_pos: QPointF) -> QPoint:
        return QPoint(
            math.floor(scene_pos.x() / self.cell_size),
            math.floor(scene_pos.y() / self.cell_size),
        )

    def snap_to_cell(self, scene_pos: QPointF):
        return QPointF(
            round(scene_pos.x() / self.cell_size) * self.cell_size,
            round(scene_pos.y() / self.cell_size) * self.cell_size,
        )

    def add_item(self, item: GridObject, grid_pos: QPoint) -> None:
        super().addItem(item)

        x = grid_pos.x() * self.cell_size
        y = grid_pos.y() * self.cell_size

        item.setPos(x, y)
        item.refresh()

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, self.clear_color)

        painter.setPen(QPen(self.grid_color, 0.4))

        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        # Align to grid
        first_left = left - (left % self.cell_size)
        first_top = top - (top % self.cell_size)

        # Vertical lines
        for x in range(first_left, right, self.cell_size):
            painter.drawLine(x, top, x, bottom)

        # Horizontal lines
        for y in range(first_top, bottom, self.cell_size):
            painter.drawLine(left, y, right, y)
