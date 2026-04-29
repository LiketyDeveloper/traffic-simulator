import json
from dataclasses import dataclass
from typing import Any, Callable

from PySide6.QtCore import QPoint

from src.database import eventDb
from src.entities import (
    BaseEntity,
    Crossing,
    CrossRoad,
    Pedestrian,
    Sign,
    StraightRoad,
    TrafficLight,
)
from src.types import Direction, Orientation, SignType
from src.world import World


@dataclass
class Serializer[T: BaseEntity]:
    serialize: Callable[[T], dict]
    deserialize: Callable[[dict[str, Any]], T]


SERIALIZERS: dict[type[BaseEntity], Serializer] = {
    StraightRoad: Serializer(
        lambda e: {"direction": e.direction.name},
        lambda d: StraightRoad(Direction[d.get("direction", "N")]),
    ),
    CrossRoad: Serializer(lambda e: {}, lambda d: CrossRoad()),
    TrafficLight: Serializer(lambda e: {}, lambda d: TrafficLight()),
    Pedestrian: Serializer(lambda e: {}, lambda d: Pedestrian()),
    Sign: Serializer(
        lambda e: {"type": e.type.name},
        lambda d: Sign(SignType[d.get("type", "BLOCK")]),
    ),
    Crossing: Serializer(
        lambda e: {"orientation": e.orientation.name},
        lambda d: Crossing(Orientation[d.get("orientation", "HORIZONTAL")]),
    ),
}


CLASS_MAP: dict[str, type[BaseEntity]] = {cls.__name__: cls for cls in SERIALIZERS}


def serializeEntity(entity: BaseEntity) -> dict:
    serializer = SERIALIZERS.get(type(entity))
    if not serializer:
        raise ValueError(f"No serializer for {type(entity).__name__}")

    return {
        "type": type(entity).__name__,
        "x": entity.cell.x(),
        "y": entity.cell.y(),
        "data": serializer.serialize(entity),
    }


def deserializeEntity(entityData: dict[str, Any]) -> BaseEntity:
    cls = CLASS_MAP[entityData["type"]]
    serializer = SERIALIZERS.get(cls)

    if not serializer:
        raise ValueError(f"No deserializer for {cls.__name__}")

    obj = serializer.deserialize(entityData.get("data", {}))
    obj.setCell(QPoint(entityData["x"], entityData["y"]))

    return obj


def saveWorld(scene: World, path: str) -> None:
    entities = [
        serializeEntity(entity)
        for entity in scene.items()
        if isinstance(entity, BaseEntity)
    ]

    with open(path, "w", encoding="utf-8") as f:
        json.dump({"entities": entities}, f, indent=2)

    eventDb.log(f"Saved {len(entities)} entities to {path!r}")


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
        worldData = json.load(f)

    world.clear()

    entities = worldData["entities"]
    entities.sort(key=lambda i: LOAD_PRIORITY.get(i["type"], 100))

    for entity in entities:
        world.addItem(deserializeEntity(entity))

    eventDb.log(f"Loaded {len(entities)} entities to {path!r}")
