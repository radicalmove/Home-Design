from __future__ import annotations

import math
from typing import Any

from .model import HouseModel


CHRISTCHURCH_LOCATION = {
    "name": "Christchurch, New Zealand",
    "latitude": -43.53333,
    "longitude": 172.63333,
    "timezone": "Pacific/Auckland",
}

YEAR_POINTS = [
    {"index": 0, "month": 6, "day": 21, "label": "Winter Jun"},
    {"index": 1, "month": 7, "day": 14, "label": "Winter Jul"},
    {"index": 2, "month": 8, "day": 6, "label": "Winter Aug"},
    {"index": 3, "month": 8, "day": 29, "label": "Late Winter Aug"},
    {"index": 4, "month": 9, "day": 21, "label": "Spring Sep"},
    {"index": 5, "month": 10, "day": 14, "label": "Spring Oct"},
    {"index": 6, "month": 11, "day": 6, "label": "Spring Nov"},
    {"index": 7, "month": 11, "day": 29, "label": "Late Spring Nov"},
    {"index": 8, "month": 12, "day": 21, "label": "Summer Dec"},
    {"index": 9, "month": 1, "day": 14, "label": "Summer Jan"},
    {"index": 10, "month": 2, "day": 6, "label": "Summer Feb"},
    {"index": 11, "month": 2, "day": 28, "label": "Late Summer Feb"},
    {"index": 12, "month": 3, "day": 21, "label": "Autumn Mar"},
    {"index": 13, "month": 4, "day": 14, "label": "Autumn Apr"},
    {"index": 14, "month": 5, "day": 7, "label": "Autumn May"},
    {"index": 15, "month": 5, "day": 30, "label": "Late Autumn May"},
]

LIGHT_ENTRY_FEATURE_IDS = {
    "sunroom_wraparound_glazing",
    "sunroom_front_double_doors",
    "lounge_north_left_window",
    "lounge_north_right_window",
    "deck_door_group",
    "deck_side_dining_window",
    "dining_west_window",
    "entrance_deck_slider",
    "laundry_north_window",
    "laundry_east_window",
    "toilet_frosted_window",
    "master_street_window",
    "master_rear_high_window",
    "master_sunroom_window",
    "office_se_window",
    "bathroom_se_window",
    "bedroom2_se_window",
    "sunroom_lounge_slider",
    "bedroom2_entrance_internal_window",
}

BORROWED_LIGHT_BETWEEN = {
    "master_sunroom_window": ["sunroom", "master_bedroom"],
}

DEFAULT_PLAN_RIGHT_BEARING_DEGREES = 52.5
DEFAULT_NORTH_ARROW_DEGREES_CLOCKWISE_FROM_PLAN_UP = 37.5
OVERLAP_TOLERANCE_PX = 6.0
MIN_SPLIT_SEGMENT_PX = 4.0


def build_sunlight_config(model: HouseModel) -> dict[str, Any]:
    compass = model.raw.get("orientation", {}).get("compass", {})
    return {
        "location": CHRISTCHURCH_LOCATION,
        "orientation": {
            "plan_right_bearing_degrees": float(
                compass.get("plan_right_bearing_degrees", DEFAULT_PLAN_RIGHT_BEARING_DEGREES)
            ),
            "north_arrow_degrees_clockwise_from_plan_up": float(
                compass.get(
                    "north_arrow_degrees_clockwise_from_plan_up",
                    DEFAULT_NORTH_ARROW_DEGREES_CLOCKWISE_FROM_PLAN_UP,
                )
            ),
            "confidence": str(compass.get("confidence", "unknown")),
        },
        "year_points": YEAR_POINTS,
        "time_slider": {"start_minutes": 240, "end_minutes": 1320, "step_minutes": 30},
        "light_entries": _light_entries(model),
        "rooms": _rooms(model),
    }


def _light_entries(model: HouseModel) -> list[dict[str, Any]]:
    entries = []
    room_centers = _room_centers(model)
    internal_opening_lines = _internal_opening_centerlines(model, room_centers)
    for feature in model.raw.get("current_structure", {}).get("features", []):
        feature_id = str(feature.get("id", ""))
        if feature_id not in LIGHT_ENTRY_FEATURE_IDS:
            continue
        centerlines = _geometry_centerlines(feature.get("display_px", {}))
        if not centerlines:
            continue
        scope = _light_entry_scope(feature, room_centers)
        line_items = []
        if scope["kind"] == "external":
            centerlines = [
                split_line
                for centerline in centerlines
                for split_line in _split_centerline_for_internal_overlaps(centerline, internal_opening_lines)
            ]
        for x1, y1, x2, y2 in centerlines:
            line: dict[str, Any] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            if isinstance(scope["room"], str) and scope["room"] in room_centers:
                line["admit_direction"] = _line_normal_toward_room(x1, y1, x2, y2, room_centers[scope["room"]])
            if isinstance(scope["between"], list):
                room_directions = [
                    {"room": adjoining_room, **_line_normal_toward_room(x1, y1, x2, y2, room_centers[adjoining_room])}
                    for adjoining_room in scope["between"]
                    if isinstance(adjoining_room, str) and adjoining_room in room_centers
                ]
                if room_directions:
                    line["room_directions"] = room_directions
            line_items.append(line)
        entries.append(
            {
                "id": feature_id,
                "kind": scope["kind"],
                "type": str(feature.get("type", "unknown")),
                "room": scope["room"],
                "between": scope["between"],
                "centerlines": line_items,
            }
        )
    return entries


def _light_entry_scope(feature: dict[str, Any], room_centers: dict[str, tuple[float, float]]) -> dict[str, Any]:
    feature_id = str(feature.get("id", ""))
    borrowed_between = BORROWED_LIGHT_BETWEEN.get(feature_id)
    if borrowed_between:
        return {"kind": "internal", "room": None, "between": borrowed_between}

    room_id = feature.get("room")
    between = feature.get("between")
    if isinstance(between, list):
        interior_rooms = [room for room in between if isinstance(room, str) and room in room_centers]
        if len(interior_rooms) >= 2:
            return {"kind": "internal", "room": None, "between": between}
        if len(interior_rooms) == 1:
            return {"kind": "external", "room": interior_rooms[0], "between": between}

    return {"kind": "external", "room": room_id, "between": between}


def _rooms(model: HouseModel) -> list[dict[str, Any]]:
    rooms = []
    for space in model.raw.get("current_structure", {}).get("spaces", []):
        geometry = space.get("display_px", {})
        if geometry.get("type") not in {"rect", "polygon", "multi_polygon"}:
            continue
        rooms.append(
            {
                "id": str(space.get("id", "")),
                "category": str(space.get("category", "")),
                "geometry": geometry,
                "center": _geometry_center(geometry),
            }
        )
    return rooms


def _internal_opening_centerlines(
    model: HouseModel,
    room_centers: dict[str, tuple[float, float]],
) -> list[tuple[float, float, float, float]]:
    centerlines = []
    for feature in model.raw.get("current_structure", {}).get("features", []):
        if _light_entry_scope(feature, room_centers)["kind"] != "internal":
            continue
        centerlines.extend(_geometry_centerlines(feature.get("display_px", {})))
    return centerlines


def _room_centers(model: HouseModel) -> dict[str, tuple[float, float]]:
    centers = {}
    for space in model.raw.get("current_structure", {}).get("spaces", []):
        space_id = str(space.get("id", ""))
        center = _geometry_center(space.get("display_px", {}))
        if center:
            centers[space_id] = center
    return centers


def _geometry_centerlines(geometry: dict[str, Any]) -> list[tuple[float, float, float, float]]:
    if geometry.get("type") == "multi_polygon":
        return [_centerline(points) for points in geometry.get("polygons", []) if points]
    if geometry.get("type") == "polygon":
        points = geometry.get("points", [])
        return [_centerline(points)] if points else []
    if geometry.get("type") == "rect":
        x = float(geometry["x"])
        y = float(geometry["y"])
        width = float(geometry["width"])
        height = float(geometry["height"])
        if height >= width:
            return [(x + width / 2, y, x + width / 2, y + height)]
        return [(x, y + height / 2, x + width, y + height / 2)]
    return []


def _centerline(points: list[list[float]]) -> tuple[float, float, float, float]:
    if len(points) == 4:
        long_axis = _thin_quad_centerline(points)
        if long_axis:
            return long_axis
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    if max_y - min_y >= max_x - min_x:
        x = (min_x + max_x) / 2
        return x, min_y, x, max_y
    y = (min_y + max_y) / 2
    return min_x, y, max_x, y


def _split_centerline_for_internal_overlaps(
    centerline: tuple[float, float, float, float],
    internal_lines: list[tuple[float, float, float, float]],
) -> list[tuple[float, float, float, float]]:
    segments = [centerline]
    for internal_line in internal_lines:
        next_segments = []
        for segment in segments:
            next_segments.extend(_split_single_centerline(segment, internal_line))
        segments = next_segments
    return segments


def _split_single_centerline(
    line: tuple[float, float, float, float],
    blocker: tuple[float, float, float, float],
) -> list[tuple[float, float, float, float]]:
    x1, y1, x2, y2 = line
    bx1, by1, bx2, by2 = blocker
    if _is_vertical(x1, y1, x2, y2) and _is_vertical(bx1, by1, bx2, by2):
        if abs(x1 - bx1) > OVERLAP_TOLERANCE_PX:
            return [line]
        pieces = _subtract_range((min(y1, y2), max(y1, y2)), (min(by1, by2), max(by1, by2)))
        return [(x1, start, x1, end) for start, end in pieces]
    if _is_horizontal(x1, y1, x2, y2) and _is_horizontal(bx1, by1, bx2, by2):
        if abs(y1 - by1) > OVERLAP_TOLERANCE_PX:
            return [line]
        pieces = _subtract_range((min(x1, x2), max(x1, x2)), (min(bx1, bx2), max(bx1, bx2)))
        return [(start, y1, end, y1) for start, end in pieces]
    return [line]


def _subtract_range(
    original: tuple[float, float],
    blocker: tuple[float, float],
) -> list[tuple[float, float]]:
    start, end = original
    block_start, block_end = blocker
    overlap_start = max(start, block_start)
    overlap_end = min(end, block_end)
    if overlap_end <= overlap_start:
        return [original]
    pieces = [(start, overlap_start), (overlap_end, end)]
    return [(piece_start, piece_end) for piece_start, piece_end in pieces if piece_end - piece_start >= MIN_SPLIT_SEGMENT_PX]


def _is_vertical(x1: float, y1: float, x2: float, y2: float) -> bool:
    return abs(x2 - x1) <= OVERLAP_TOLERANCE_PX and abs(y2 - y1) > OVERLAP_TOLERANCE_PX


def _is_horizontal(x1: float, y1: float, x2: float, y2: float) -> bool:
    return abs(y2 - y1) <= OVERLAP_TOLERANCE_PX and abs(x2 - x1) > OVERLAP_TOLERANCE_PX


def _thin_quad_centerline(points: list[list[float]]) -> tuple[float, float, float, float] | None:
    edges: list[tuple[float, tuple[float, float]]] = []
    for index, start in enumerate(points):
        end = points[(index + 1) % len(points)]
        x1, y1 = float(start[0]), float(start[1])
        x2, y2 = float(end[0]), float(end[1])
        length = math.hypot(x2 - x1, y2 - y1)
        midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
        edges.append((length, midpoint))

    shortest = sorted(edges, key=lambda edge: edge[0])[:2]
    longest = sorted(edges, key=lambda edge: edge[0])[-1][0]
    if not shortest or longest < 1 or longest / max(shortest[-1][0], 0.1) < 1.4:
        return None
    (x1, y1), (x2, y2) = shortest[0][1], shortest[1][1]
    return x1, y1, x2, y2


def _geometry_center(geometry: dict[str, Any]) -> tuple[float, float] | None:
    if geometry.get("type") == "rect":
        x = float(geometry["x"])
        y = float(geometry["y"])
        return x + float(geometry["width"]) / 2, y + float(geometry["height"]) / 2
    if geometry.get("type") == "polygon":
        return _points_center(geometry.get("points", []))
    if geometry.get("type") == "multi_polygon":
        centers = [_points_center(points) for points in geometry.get("polygons", [])]
        centers = [center for center in centers if center]
        if centers:
            return (
                sum(center[0] for center in centers) / len(centers),
                sum(center[1] for center in centers) / len(centers),
            )
    return None


def _points_center(points: list[list[float]]) -> tuple[float, float] | None:
    if not points:
        return None
    return (
        sum(float(point[0]) for point in points) / len(points),
        sum(float(point[1]) for point in points) / len(points),
    )


def _line_normal_toward_room(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    room_center: tuple[float, float],
) -> dict[str, float]:
    dx = x2 - x1
    dy = y2 - y1
    line_length = math.hypot(dx, dy)
    if line_length == 0:
        return {"x": 0.0, "y": 0.0}

    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    to_room_x = room_center[0] - mid_x
    to_room_y = room_center[1] - mid_y
    to_room_length = math.hypot(to_room_x, to_room_y)
    if to_room_length == 0:
        return {"x": 0.0, "y": 0.0}

    normals = [(-dy / line_length, dx / line_length), (dy / line_length, -dx / line_length)]
    target_x = to_room_x / to_room_length
    target_y = to_room_y / to_room_length
    normal_x, normal_y = max(normals, key=lambda normal: normal[0] * target_x + normal[1] * target_y)
    return {"x": round(normal_x, 4), "y": round(normal_y, 4)}
