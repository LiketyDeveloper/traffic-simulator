from PySide6.QtCore import QObject, QPoint, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent

from .constants import CELL_SIZE, GRID_DIM
from .utils import cellToScenePos, scenePosToCell


class World(QGraphicsScene):
    onWorldCellClicked = Signal(object)

    def __init__(
        self,
        parent: QObject | None = None,
        background_color: QColor = QColor("#ffffff"),
        grid_color: QColor = QColor("#e0e0e0"),
        tick_ms: int = 50,
    ) -> None:
        super().__init__(parent)

        self.background_color = background_color
        self.grid_color = grid_color

        size = GRID_DIM * CELL_SIZE
        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

    def get(self, at: QPoint, types: type | tuple[type] = object):
        return [
            entity
            for entity in self.items(cellToScenePos(at), Qt.ItemSelectionMode.IntersectsItemBoundingRect)
            if isinstance(entity, types)
        ]

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent, /) -> None:
        cell = scenePosToCell(event.scenePos())
        self.onWorldCellClicked.emit(cell)

        return super().mousePressEvent(event)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, self.background_color)

        painter.setPen(QPen(self.grid_color, 0.4))

        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        first_left = left - (left % CELL_SIZE)
        first_top = top - (top % CELL_SIZE)

        for x in range(first_left, right, CELL_SIZE):
            painter.drawLine(x, top, x, bottom)

        for y in range(first_top, bottom, CELL_SIZE):
            painter.drawLine(left, y, right, y)
