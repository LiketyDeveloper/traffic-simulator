import math
from PySide6.QtCore import QPoint, QPointF

from src.types import Direction, TurnType

from src.constants import CELL_SIZE, CLOCKWISE, DIR2OFFSET, MEDIA_PATH


def getMediaPath(media_name: str) -> str:
    return str(MEDIA_PATH / media_name)


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


def getDirectionFromOffset(offset: QPoint) -> Direction:
    for direction, dir_offset in DIR2OFFSET.items():
        if offset == dir_offset:
            return direction
    return Direction.N


def rotateDirection(direction: Direction, turn: TurnType) -> Direction:
    delta = {
        TurnType.FORWARD: 0,
        TurnType.RIGHT: 1,
        TurnType.UTURN: 2,
        TurnType.LEFT: -1,
    }
    return CLOCKWISE[(CLOCKWISE.index(direction) + delta[turn]) % 4]


def expandCrossroadPaths(enterDirection: Direction) -> dict[TurnType, list[QPoint]]:
    fwd = DIR2OFFSET[enterDirection]
    back = DIR2OFFSET[rotateDirection(enterDirection, TurnType.UTURN)]
    left = DIR2OFFSET[rotateDirection(enterDirection, TurnType.LEFT)]
    right = DIR2OFFSET[rotateDirection(enterDirection, TurnType.RIGHT)]

    fwd_p1 = fwd
    fwd_p2 = fwd_p1 + fwd
    fwd_p3 = fwd_p2 + fwd

    left_p1 = fwd
    left_p2 = left_p1 + fwd
    left_p3 = left_p2 + left
    left_p4 = left_p3 + left

    right_p1 = fwd
    right_p2 = right_p1 + right

    uturn_p1 = fwd
    uturn_p2 = uturn_p1 + left
    uturn_p3 = uturn_p2 + back

    return {
        TurnType.FORWARD: [fwd_p1, fwd_p2, fwd_p3],
        TurnType.LEFT: [left_p1, left_p2, left_p3, left_p4],
        TurnType.RIGHT: [right_p1, right_p2],
        TurnType.UTURN: [uturn_p1, uturn_p2, uturn_p3],
    }
