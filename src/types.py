from enum import Enum
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from src.entities import BaseEntity


type EntityFactory = Callable[[], "BaseEntity"]


class Direction(Enum):
    N = 0
    S = 1
    W = 2
    E = 3


class Orientation(Enum):
    VERTICAL = 0
    HORIZONTAL = 1


class TLState(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2


class TLMode(Enum):
    TIME = 0
    TRANSPORT = 1


class SignType(Enum):
    BLOCK = 0
    STOP = 1
    START = 2


class TurnType(Enum):
    FORWARD = 0
    RIGHT = 1
    UTURN = 2
    LEFT = 3
