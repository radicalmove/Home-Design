from __future__ import annotations

from .model import Room


def layout_bounds(rooms: list[Room]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for room in rooms:
        layout = room.layout
        if layout.get("type") == "polygon":
            for x, y in layout.get("points", []):
                xs.append(float(x))
                ys.append(float(y))
        else:
            x = float(layout.get("x", 0))
            y = float(layout.get("y", 0))
            xs.extend([x, x + float(layout.get("width", 0))])
            ys.extend([y, y + float(layout.get("depth", 0))])
    return min(xs), min(ys), max(xs), max(ys)


def layout_size(rooms: list[Room]) -> tuple[float, float]:
    min_x, min_y, max_x, max_y = layout_bounds(rooms)
    return max_x - min_x, max_y - min_y
