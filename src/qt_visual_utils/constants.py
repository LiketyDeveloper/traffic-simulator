from pathlib import Path

from PySide6.QtCore import QPoint

from qt_visual_utils.types import Direction

SRC_PATH = Path(__file__).parent.parent
BASE_PATH = SRC_PATH.parent
MEDIA_PATH = BASE_PATH / "media"

CELL_SIZE = 35
GRID_DIM = 50


class ZIndexes:
    Road = 0
    Crossing = 5
    Pedestrian = 10
    Car = 15
    Sign = 20
    TrafficLight = 25


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

CLOCKWISE = [Direction.N, Direction.E, Direction.S, Direction.W]
