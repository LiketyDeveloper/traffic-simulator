import math
from PySide6.QtCore import QPoint, QPointF

from .constants import CELL_SIZE, MEDIA_PATH


def getMediaPath(media_name: str) -> str:
    return str(MEDIA_PATH / media_name)


def find_instance[T](of: type[T] | tuple[type[T], ...], in_: list) -> T | None:
    return next((obj for obj in in_ if isinstance(obj, of)), None)


def scenePosToCell(pos: QPoint | QPointF):
    return QPoint(
        math.floor(pos.x() / CELL_SIZE),
        math.floor(pos.y() / CELL_SIZE),
    )

def snapScenePosToCell(pos: QPoint | QPointF):
    return QPoint(
        round(pos.x() / CELL_SIZE),
        round(pos.y() / CELL_SIZE),
    )

def cellToScenePos(cell: QPoint):
    return QPoint(
        cell.x() * CELL_SIZE,
        cell.y() * CELL_SIZE,
    )
