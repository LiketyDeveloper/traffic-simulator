from typing import TYPE_CHECKING
from PySide6.QtCore import QObject, QPoint, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent

from src.constants import CELL_SIZE, DIR2OFFSET, GRID_DIM
from src.utils import cellToScenePos, scenePosToCell

from src.entities import BaseEntity


class World(QGraphicsScene):
    onWorldCellClicked = Signal(object)

    def __init__(
        self,
        parent: QObject | None = None,
        backgroundColor: QColor = QColor("#ffffff"),
        gridColor: QColor = QColor("#e0e0e0"),
        tickMs: int = 50,
    ) -> None:
        super().__init__(parent)

        self.backgroundColor = backgroundColor
        self.gridColor = gridColor

        size = GRID_DIM * CELL_SIZE
        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

    def get[T: BaseEntity](
        self, at: QPoint, types: type[T] | tuple[type[T]] = BaseEntity
    ) -> list[T]:
        return [
            entity
            for entity in self.items(
                cellToScenePos(at) + QPoint(CELL_SIZE // 2, CELL_SIZE // 2),
                Qt.ItemSelectionMode.IntersectsItemBoundingRect,
            )
            if isinstance(entity, types) and entity.cell == at
        ]

    def getNeighbors[T: BaseEntity](
        self, at: QPoint, types: type[T] | tuple[type[T]] = BaseEntity
    ) -> list[T]:
        neighbors = []
        for _, offset in DIR2OFFSET.items():
            neighbors.extend(self.get(at + offset, types))

        return neighbors

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent, /) -> None:
        cell = scenePosToCell(event.scenePos())
        self.onWorldCellClicked.emit(cell)

        return super().mousePressEvent(event)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, self.backgroundColor)

        painter.setPen(QPen(self.gridColor, 0.4))

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
