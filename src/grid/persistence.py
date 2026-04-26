import json
from PySide6.QtCore import QPoint, QPointF

from .scene import GridScene
from .objects import (
    Car,
    Road,
    Crossroad,
    TrafficLight,
    Pedestrian,
    Crossing,
    Sign,
    GridObject,
)

CLASS_MAP = {
    cls.__name__: cls
    for cls in (
        Car,
        Road,
        Crossroad,
        TrafficLight,
        Pedestrian,
        Crossing,
        Sign,
    )
}


def serialize_item(scene: GridScene, item: GridObject) -> dict:
    cell = scene.scene_pos_to_cell(item.pos())
    return {
        "type": item.__class__.__name__,
        "x": cell.x(),
        "y": cell.y(),
        "data": item.serialize(),
    }


def save_scene(scene: GridScene, path: str) -> None:
    items = []

    for item in scene.items():
        if isinstance(item, GridObject) and item.is_persistent:
            items.append(serialize_item(scene, item))

    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


LOAD_PRIORITY: dict[str, int] = {
    "Road": 0,
    "Crossroad": 0,
    "Crossing": 1,
    "TrafficLight": 2,
    "Sign": 3,
    "Pedestrian": 4,
    "Car": 5,
}


def load_scene(scene: GridScene, path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)

    scene.clear()

    items.sort(key=lambda i: LOAD_PRIORITY.get(i["type"], 100))

    for item in items:
        cls = CLASS_MAP[item["type"]]
        obj = cls.deserialize(item["data"])

        scene.add_item(obj, QPoint(item["x"], item["y"]))
