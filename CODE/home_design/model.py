from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    category: str
    dimensions_m: dict[str, float | None]
    confidence: str
    notes: list[str]
    layout: dict[str, Any]


@dataclass(frozen=True)
class HouseModel:
    raw: dict[str, Any]
    units: str
    rooms: list[Room]

    def room(self, room_id: str) -> Room:
        for room in self.rooms:
            if room.id == room_id:
                return room
        raise KeyError(f"Unknown room id: {room_id}")

    def raw_room(self, room_id: str) -> dict[str, Any]:
        for room in self.raw.get("rooms", []):
            if room.get("id") == room_id:
                return room
        raise KeyError(f"Unknown room id: {room_id}")


def load_model(path: str | Path) -> HouseModel:
    raw = json.loads(Path(path).read_text())
    rooms = [
        Room(
            id=item["id"],
            name=item["name"],
            category=item.get("category", "living"),
            dimensions_m=item.get("dimensions_m", {}),
            confidence=item.get("confidence", "unknown"),
            notes=item.get("notes", []),
            layout=item.get("layout", {}),
        )
        for item in raw.get("rooms", [])
    ]
    return HouseModel(raw=raw, units=raw["units"], rooms=rooms)
