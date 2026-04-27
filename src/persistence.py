from dataclasses import dataclass
import json
from typing import Any
from PySide6.QtCore import QPoint

from src.entities import (
    BaseEntity,
    StraightRoad,
    CrossRoad,
    TrafficLight,
    Pedestrian,
    Crossing,
    Sign,
)
from src.world import World
from src.types import Direction, SignType, Orientation

CLASS_MAP = {
    cls.__name__: cls
    for cls in (
        StraightRoad,
        CrossRoad,
        TrafficLight,
        Pedestrian,
        Crossing,
        Sign,
    )
}


def serializeEntity(entity: BaseEntity) -> dict:
    data = {
        "type": type(entity).__name__,
        "x": entity.cell.x(),
        "y": entity.cell.y(),
        "data": {},
    }

    if isinstance(entity, StraightRoad):
        data["data"]["direction"] = entity.direction.name

    elif isinstance(entity, Sign):
        data["data"]["type"] = entity.type.name

    elif isinstance(entity, Crossing):
        data["data"]["orientation"] = entity.orientation.name

    return data


def deserializeEntity(entityData: dict[str, Any]) -> BaseEntity:
    cls = CLASS_MAP[entityData["type"]]
    data = entityData.get("data", {})

    if cls is StraightRoad:
        direction = Direction[data.get("direction", "N")]
        obj = StraightRoad(direction)

    elif cls is CrossRoad:
        obj = CrossRoad()

    elif cls is TrafficLight:
        obj = TrafficLight()

    elif cls is Sign:
        obj = Sign(SignType[data["type"]])

    elif cls is Crossing:
        obj = Crossing()
        if "orientation" in data:
            obj.orientation = Orientation[data["orientation"]]

    else:
        obj = cls()

    obj.setCell(QPoint(entityData["x"], entityData["y"]))

    return obj


def saveWorld(scene: World, path: str) -> None:
    entities = [
        serializeEntity(entity)
        for entity in scene.items()
        if isinstance(entity, BaseEntity)
    ]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2)


LOAD_PRIORITY: dict[str, int] = {
    "StraightRoad": 0,
    "CrossRoad": 0,
    "Crossing": 1,
    "TrafficLight": 2,
    "Sign": 3,
    "Pedestrian": 4,
    "Car": 5,
}


def loadWorld(world: World, path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        entities = json.load(f)

    world.clear()

    entities.sort(key=lambda i: LOAD_PRIORITY.get(i["type"], 100))

    for item in entities:
        obj = deserializeEntity(item)
        world.addItem(obj)
