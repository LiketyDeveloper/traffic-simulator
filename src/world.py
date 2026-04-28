import random
from functools import lru_cache

from PySide6.QtCore import QObject, QPoint, QRectF, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent

from src.constants import CELL_SIZE, DIR2OFFSET, GRID_DIM
from src.entities import BaseEntity, CrossRoad, Road, StraightRoad
from src.utils import expandCrossroadPaths, scenePosToCell


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

        self.simTimer = QTimer(self)
        self.simTimer.setInterval(tickMs)
        self.simTimer.timeout.connect(self.onTick)
        self.simTimer.start()

    def entities[T: BaseEntity](self, types: type[T] | tuple[type[T]]) -> list[T]:
        return [e for e in self.items() if isinstance(e, types)]

    def get[T: BaseEntity](
        self, at: QPoint, types: type[T] | tuple[type[T]] = BaseEntity
    ) -> list[T]:
        return [e for e in self.entities(types) if e.cell == at]

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

    def onTick(self) -> None:
        for entity in self.items():
            if isinstance(entity, BaseEntity):
                entity.tick(self.simTimer.interval() / 1000)

    def generateRandomPath(
        self, start: StraightRoad, maxLength: int = 60
    ) -> list[Road]:
        path: list[Road] = [start]
        current = start

        for _ in range(maxLength):
            ahead = self.get(current.getCellOffset(1), Road)

            if not ahead:
                break
            ahead = ahead[0]

            if isinstance(ahead, StraightRoad):
                if current.direction != ahead.direction:
                    break

                path.append(ahead)
                current = ahead
                continue
            if isinstance(ahead, CrossRoad):
                expandedPaths = list(expandCrossroadPaths(current.direction).items())
                random.shuffle(expandedPaths)

                for turnType, pathSteps in expandedPaths:
                    dst = self.get(current.cell + pathSteps[-1], StraightRoad)
                    if not dst or not dst[0].canBePassed():
                        continue

                    for stepOffset in pathSteps:
                        road = self.get(current.cell + stepOffset, Road)
                        if not road:
                            break  # if gap in path then abort turn
                        path.append(road[0])

                    current = dst[0]
                    break

        return path

    @lru_cache(maxsize=32)
    def getEntrances(self) -> list[StraightRoad]:
        entrances: list[StraightRoad] = []

        for road in self.entities(StraightRoad):
            behindRoads = self.get(road.getCellOffset(-1), Road)

            if len(behindRoads) == 0:
                entrances.append(road)

        return entrances
