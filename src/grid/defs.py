from enum import StrEnum

from PySide6.QtCore import QPoint


class Direction(StrEnum):
    N = "vertical"
    S = "bottom"
    W = "left"
    E = "right"

class Orientation(StrEnum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class TLState(StrEnum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"

class TLMode(StrEnum):
    TIME = "time"
    TRANSPORT = "transport"


class SignType(StrEnum):
    BLOCK = "Block"
    STOP = "Stop"
    START = "Start"


DIR2ROT: dict[Direction, int] = {
    Direction.N: 0,
    Direction.S: 180,
    Direction.W: -90,
    Direction.E: 90,
}

DIR2OFFSET: dict[Direction, QPoint] = {
    Direction.N: QPoint(0, -1),
    Direction.S: QPoint(0, 1),
    Direction.W: QPoint(-1, 0),
    Direction.E: QPoint(1, 0),
}
