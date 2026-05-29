from __future__ import annotations

import json
import re
from html import escape
from typing import Any

from .model import HouseModel


THREE_VERSION = "0.160.0"

MATERIALS = {
    "vinyl_plank": {"kind": "floor", "color": "#9a8067", "roughness": 0.78, "pattern": "planks"},
    "carpet": {"kind": "floor", "color": "#b8ab98", "roughness": 0.96, "pattern": "carpet"},
    "tile": {"kind": "floor", "color": "#d7dee0", "roughness": 0.62, "pattern": "tile"},
    "timber_floor": {"kind": "floor", "color": "#d2b58d", "roughness": 0.78, "pattern": "planks"},
    "wet_tile": {"kind": "floor", "color": "#d7dee0", "roughness": 0.62, "pattern": "tile"},
    "painted_wall": {"kind": "wall", "color": "#eee9df", "roughness": 0.86},
    "white_frame": {"kind": "trim", "color": "#f8f6ef", "roughness": 0.52},
    "glazing": {"kind": "transparent", "color": "#b8d8e6", "opacity": 0.28},
    "navy_cabinet": {"kind": "fixture", "color": "#1c3043", "roughness": 0.55},
    "white_counter": {"kind": "fixture", "color": "#f1eee7", "roughness": 0.48},
    "wood_furniture": {"kind": "fixture", "color": "#9f7042", "roughness": 0.68},
    "dark_sofa": {"kind": "fixture", "color": "#26282d", "roughness": 0.9},
    "storage_color": {"kind": "fixture", "color": "#667a60", "roughness": 0.84},
    "appliance_white": {"kind": "fixture", "color": "#e8e5dd", "roughness": 0.44},
    "deck_timber": {"kind": "site", "color": "#9a6438", "roughness": 0.72, "pattern": "deck"},
    "paver_concrete": {"kind": "site", "color": "#c9c4b8", "roughness": 0.9},
    "lawn": {"kind": "site", "color": "#78a85f", "roughness": 1.0},
}

CARPET_ROOM_IDS = {
    "lounge",
    "sunroom",
    "hallway",
    "master_bedroom",
    "office",
    "bedroom_2",
}
VINYL_ROOM_IDS = {"kitchen_dining", "entrance", "laundry", "toilet"}
TILE_ROOM_IDS = {"bathroom"}
PIXEL_TO_METRE = 0.81 / 22.0
REFERENCE_PIXEL_ORIGIN = {"x": 518.0, "y": 314.0}
GLAZING_TYPES = {"window", "window_group", "slider", "sliding_door", "door_group"}
CURATED_WALL_PATHS = [
    ("sunroom_glazing_frame", "interior", "M536 486 V452 H552 L597 408 V360 H667.1 V380.4 M667.1 462.6 V486"),
    ("lounge_exterior", "exterior", "M657.2 358 H762.8"),
    ("lounge_sunroom_wall", "exterior", "M659.1 358 V380.4 M659.1 462.6 V485"),
    ("master_sunroom_old_external_wall", "exterior", "M518 485 H608"),
    ("hallway_north_wall", "exterior", "M608 485 H634 M654.4 485 H667.1"),
    ("lounge_hallway_wall", "interior", "M659.1 488.5 H701.5 M723.5 488.5 H760.9"),
    ("kitchen_east_wall", "exterior", "M758.8 358 V302.3 H833 V498.5"),
    ("entrance_deck_wall", "thin-exterior", "M834.3 496 H841.9 M881.8 496 H940"),
    ("kitchen_entrance_return_wall", "thin-interior", "M834.3 496 V502.8 H803.7"),
    ("private_rooms_south_wall", "exterior", "M518 610 H940"),
    ("bedroom2_east_wall", "interior", "M890 518.5 V610"),
    ("master_west_wall", "exterior", "M518 485 V610"),
    ("dining_west_external_wall", "exterior", "M758.8 302.3 V358"),
    ("kitchen_lounge_nub", "interior", "M760.9 358 V370.8"),
    ("lounge_kitchen_divider", "interior", "M760.9 395 V493"),
    ("hallway_south_wall", "interior", "M608 523 H657 M679 523 H688 M722 523 H758"),
    ("hallway_kitchen_door_wall", "interior", "M760.9 515 V523"),
    ("bedroom2_north_wall", "interior", "M758 523 H762 M784 523 H890"),
    ("master_office_wall", "interior", "M608 485 V494 M608 516 V610"),
    ("office_bathroom_wall", "interior", "M688 520.5 V610"),
    ("bathroom_bedroom2_wall", "interior", "M758 523 V610"),
    ("entrance_laundry_wall", "interior", "M890 496 V504"),
    ("laundry_toilet_wall", "thin-interior", "M890 580 H896 M912 580 H940"),
    ("kitchen_entrance_door_wall", "interior", "M803.7 496 V499.6 M803.7 519.4 V523"),
    ("laundry_toilet_exterior", "exterior", "M940 496 V610"),
]
WALL_CLASS_SPECS = {
    "exterior": {"height": 2.35, "thickness": 0.16},
    "interior": {"height": 2.35, "thickness": 0.1},
    "thin-exterior": {"height": 2.35, "thickness": 0.08},
    "thin-interior": {"height": 2.35, "thickness": 0.07},
}
WALL_PATH_TOKEN_RE = re.compile(r"[MLHVZ]|-?\d+(?:\.\d+)?")
OPENING_GAP_TYPES = {"window", "window_group", "slider", "sliding_door", "door_group", "door"}
OPENING_WALL_PROXIMITY_M = 0.14
OPENING_GAP_MARGIN_M = 0.015
MIN_OPENING_OVERLAP_M = 0.08
MIN_WALL_PIECE_LENGTH_M = 0.08
START_CAMERA = {
    "position": {"x": 17.1, "y": 1.7, "z": 4.7},
    "look_at": {"x": 10.45, "y": 1.38, "z": 3.65},
}
PHOTO_FIXTURE_SPECS = [
    {
        "id": "kitchen_dark_cabinet_run",
        "room": "kitchen_dining",
        "material": "navy_cabinet",
        "height": 1.25,
        "display_px": {"type": "rect", "x": 744, "y": 320, "width": 18, "height": 168},
        "evidence_photo_paths": ["OUTPUT/jpeg_photos/Inside-Kitchen-Looking-NW-2.jpg"],
    },
    {
        "id": "kitchen_counter_sink",
        "room": "kitchen_dining",
        "material": "white_counter",
        "height": 0.92,
        "display_px": {"type": "rect", "x": 802, "y": 342, "width": 18, "height": 70},
        "evidence_photo_paths": ["OUTPUT/jpeg_photos/Inside-Kitchen-Looking-NW-2.jpg"],
    },
    {
        "id": "dining_table",
        "room": "kitchen_dining",
        "material": "wood_furniture",
        "height": 0.74,
        "display_px": {"type": "rect", "x": 774, "y": 386, "width": 36, "height": 64},
        "evidence_photo_paths": ["OUTPUT/jpeg_photos/Inside-Kitchen-Looking-NW-2.jpg"],
    },
    {
        "id": "lounge_sofa",
        "room": "lounge",
        "material": "dark_sofa",
        "height": 0.78,
        "display_px": {"type": "rect", "x": 682, "y": 430, "width": 52, "height": 42},
        "evidence_photo_paths": ["OUTPUT/jpeg_photos/Inside-Lounge-Looking-NE.jpg"],
    },
    {
        "id": "sunroom_play_tables",
        "room": "sunroom",
        "material": "white_counter",
        "height": 0.74,
        "display_px": {"type": "rect", "x": 548, "y": 438, "width": 74, "height": 38},
        "evidence_photo_paths": ["OUTPUT/jpeg_photos/Inside-Sunroom-Looking-NW.jpg"],
    },
    {
        "id": "sunroom_storage_shelves",
        "room": "sunroom",
        "material": "storage_color",
        "height": 1.6,
        "display_px": {"type": "rect", "x": 614, "y": 394, "width": 24, "height": 78},
        "evidence_photo_paths": ["OUTPUT/jpeg_photos/Inside-Sunroom-Looking-NW.jpg"],
    },
    {
        "id": "laundry_appliance_pair",
        "room": "laundry",
        "material": "appliance_white",
        "height": 0.88,
        "display_px": {"type": "rect", "x": 900, "y": 536, "width": 34, "height": 34},
        "evidence_photo_paths": ["OUTPUT/jpeg_photos/Inside-Entrance-Looking-NE.jpg"],
    },
]


def _room_material(room_id: str, category: str) -> str:
    if room_id in TILE_ROOM_IDS:
        return "tile"
    if room_id in VINYL_ROOM_IDS:
        return "vinyl_plank"
    if room_id in CARPET_ROOM_IDS:
        return "carpet"
    if category == "wet":
        return "tile"
    return "vinyl_plank"


def _room_geometry(layout: dict[str, Any]) -> dict[str, Any] | None:
    if layout.get("type") == "rect":
        return {
            "type": "rect",
            "x": float(layout["x"]),
            "z": float(layout["y"]),
            "width": float(layout["width"]),
            "depth": float(layout["depth"]),
        }
    if layout.get("type") == "polygon":
        return {
            "type": "polygon",
            "points": [
                {"x": float(point[0]), "z": float(point[1])}
                for point in layout.get("points", [])
            ],
        }
    return None


def _room_config(model: HouseModel) -> tuple[list[dict[str, Any]], list[str]]:
    rooms: list[dict[str, Any]] = []
    warnings: list[str] = []
    traced_spaces = _current_space_lookup(model)
    for room in model.rooms:
        geometry = None
        geometry_source = "room.layout"
        traced_space = traced_spaces.get(room.id)
        if traced_space is not None:
            geometry = _scene_geometry_from_display_px(traced_space)
            geometry_source = "current_structure.spaces.display_px"
        if geometry is None:
            geometry = _room_geometry(room.layout)
        if geometry is None:
            warnings.append(f"Skipping room without 3D layout: {room.id}")
            continue
        rooms.append(
            {
                "id": room.id,
                "name": room.name,
                "category": room.category,
                "confidence": room.confidence,
                "geometry": geometry,
                "geometry_source": geometry_source,
                "height": float(room.dimensions_m.get("height") or 2.4),
                "floor_material": _room_material(room.id, room.category),
                "wall_material": "painted_wall",
                "notes": room.notes,
            }
        )
    return rooms, warnings


def _scene_point_from_px(point: list[float] | tuple[float, float]) -> dict[str, float]:
    return {
        "x": (float(point[0]) - REFERENCE_PIXEL_ORIGIN["x"]) * PIXEL_TO_METRE,
        "z": (float(point[1]) - REFERENCE_PIXEL_ORIGIN["y"]) * PIXEL_TO_METRE,
    }


def _scene_geometry_from_display_px(display_px: dict[str, Any]) -> dict[str, Any] | None:
    geometry_type = display_px.get("type")
    if geometry_type == "rect":
        origin = _scene_point_from_px([display_px["x"], display_px["y"]])
        return {
            "type": "rect",
            "x": origin["x"],
            "z": origin["z"],
            "width": float(display_px["width"]) * PIXEL_TO_METRE,
            "depth": float(display_px["height"]) * PIXEL_TO_METRE,
        }
    if geometry_type == "polygon":
        return {
            "type": "polygon",
            "points": [_scene_point_from_px(point) for point in display_px.get("points", [])],
        }
    if geometry_type == "multi_polygon":
        return {
            "type": "multi_polygon",
            "polygons": [
                [_scene_point_from_px(point) for point in polygon]
                for polygon in display_px.get("polygons", [])
            ],
        }
    return None


def _wall_path_segments(path_data: str) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    tokens = WALL_PATH_TOKEN_RE.findall(path_data)
    segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
    command = ""
    current: tuple[float, float] | None = None
    subpath_start: tuple[float, float] | None = None
    index = 0
    commands = {"M", "L", "H", "V", "Z"}

    while index < len(tokens):
        token = tokens[index]
        if token in commands:
            command = token
            index += 1
        if command == "M":
            current = (float(tokens[index]), float(tokens[index + 1]))
            subpath_start = current
            index += 2
            command = "L"
            continue
        if command == "L" and current is not None:
            next_point = (float(tokens[index]), float(tokens[index + 1]))
            if next_point != current:
                segments.append((current, next_point))
            current = next_point
            index += 2
            continue
        if command == "H" and current is not None:
            next_point = (float(tokens[index]), current[1])
            if next_point != current:
                segments.append((current, next_point))
            current = next_point
            index += 1
            continue
        if command == "V" and current is not None:
            next_point = (current[0], float(tokens[index]))
            if next_point != current:
                segments.append((current, next_point))
            current = next_point
            index += 1
            continue
        if command == "Z" and current is not None and subpath_start is not None:
            if current != subpath_start:
                segments.append((current, subpath_start))
            current = subpath_start
            command = ""
            continue
        raise ValueError(f"Unsupported wall path near token {token!r}: {path_data}")

    return segments


def _bounds_from_scene_points(points: list[dict[str, float]]) -> dict[str, float] | None:
    if not points:
        return None
    return {
        "min_x": min(point["x"] for point in points),
        "max_x": max(point["x"] for point in points),
        "min_z": min(point["z"] for point in points),
        "max_z": max(point["z"] for point in points),
    }


def _geometry_bounds_list(geometry: dict[str, Any]) -> list[dict[str, float]]:
    if geometry.get("type") == "rect":
        x = float(geometry["x"])
        z = float(geometry["z"])
        return [
            {
                "min_x": x,
                "max_x": x + float(geometry["width"]),
                "min_z": z,
                "max_z": z + float(geometry["depth"]),
            }
        ]
    if geometry.get("type") == "polygon":
        bounds = _bounds_from_scene_points(geometry.get("points", []))
        return [bounds] if bounds is not None else []
    if geometry.get("type") == "multi_polygon":
        bounds = [
            _bounds_from_scene_points(polygon)
            for polygon in geometry.get("polygons", [])
        ]
        return [item for item in bounds if item is not None]
    return []


def _opening_gap_bounds(model: HouseModel) -> list[dict[str, float]]:
    gaps = []
    for feature in model.raw.get("current_structure", {}).get("features", []):
        if feature.get("type") not in OPENING_GAP_TYPES:
            continue
        display_px = feature.get("display_px")
        if not isinstance(display_px, dict):
            continue
        geometry = _scene_geometry_from_display_px(display_px)
        if geometry is None:
            continue
        gaps.extend(_geometry_bounds_list(geometry))
    return gaps


def _subtract_intervals(
    source: tuple[float, float],
    cuts: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    source_low, source_high = sorted(source)
    pieces = [(source_low, source_high)]
    for cut_low, cut_high in sorted(cuts):
        if cut_high <= source_low or cut_low >= source_high:
            continue
        overlap = min(source_high, cut_high) - max(source_low, cut_low)
        if overlap < MIN_OPENING_OVERLAP_M:
            continue
        next_pieces = []
        for piece_low, piece_high in pieces:
            if cut_high <= piece_low or cut_low >= piece_high:
                next_pieces.append((piece_low, piece_high))
                continue
            left = (piece_low, min(cut_low, piece_high))
            right = (max(cut_high, piece_low), piece_high)
            if left[1] - left[0] >= MIN_WALL_PIECE_LENGTH_M:
                next_pieces.append(left)
            if right[1] - right[0] >= MIN_WALL_PIECE_LENGTH_M:
                next_pieces.append(right)
        pieces = next_pieces
    return pieces


def _split_wall_segment_for_openings(
    start_point: dict[str, float],
    end_point: dict[str, float],
    opening_gaps: list[dict[str, float]],
) -> list[dict[str, float]]:
    x1 = start_point["x"]
    z1 = start_point["z"]
    x2 = end_point["x"]
    z2 = end_point["z"]
    vertical = abs(x1 - x2) < 1e-6
    horizontal = abs(z1 - z2) < 1e-6
    if not (vertical or horizontal):
        return [{"x1": x1, "z1": z1, "x2": x2, "z2": z2}]

    if vertical:
        cut_intervals = [
            (
                gap["min_z"] - OPENING_GAP_MARGIN_M,
                gap["max_z"] + OPENING_GAP_MARGIN_M,
            )
            for gap in opening_gaps
            if gap["min_x"] - OPENING_WALL_PROXIMITY_M <= x1 <= gap["max_x"] + OPENING_WALL_PROXIMITY_M
        ]
        pieces = _subtract_intervals((z1, z2), cut_intervals)
        if z1 > z2:
            pieces = [(high, low) for low, high in pieces]
        return [{"x1": x1, "z1": low, "x2": x2, "z2": high} for low, high in pieces]

    cut_intervals = [
        (
            gap["min_x"] - OPENING_GAP_MARGIN_M,
            gap["max_x"] + OPENING_GAP_MARGIN_M,
        )
        for gap in opening_gaps
        if gap["min_z"] - OPENING_WALL_PROXIMITY_M <= z1 <= gap["max_z"] + OPENING_WALL_PROXIMITY_M
    ]
    pieces = _subtract_intervals((x1, x2), cut_intervals)
    if x1 > x2:
        pieces = [(high, low) for low, high in pieces]
    return [{"x1": low, "z1": z1, "x2": high, "z2": z2} for low, high in pieces]


def _wall_config(model: HouseModel) -> list[dict[str, Any]]:
    walls = []
    opening_gaps = _opening_gap_bounds(model)
    for wall_id, wall_class, path_data in CURATED_WALL_PATHS:
        spec = WALL_CLASS_SPECS[wall_class]
        segments = []
        for start, end in _wall_path_segments(path_data):
            start_point = _scene_point_from_px(start)
            end_point = _scene_point_from_px(end)
            segments.extend(
                _split_wall_segment_for_openings(start_point, end_point, opening_gaps)
            )
        walls.append(
            {
                "id": wall_id,
                "class": wall_class,
                "pixel_path": path_data,
                "segments": segments,
                "height": spec["height"],
                "thickness": spec["thickness"],
                "material": "painted_wall",
            }
        )
    return walls


def _current_space_lookup(model: HouseModel) -> dict[str, dict[str, Any]]:
    spaces = {}
    for space in model.raw.get("current_structure", {}).get("spaces", []):
        display_px = space.get("display_px")
        if isinstance(display_px, dict):
            spaces[str(space.get("id"))] = display_px
    return spaces


def _feature_material(feature: dict[str, Any]) -> str:
    feature_type = str(feature.get("type", ""))
    if feature_type in GLAZING_TYPES or "glazing" in str(feature.get("id", "")):
        return "glazing"
    return "painted_wall"


def _feature_config(model: HouseModel) -> list[dict[str, Any]]:
    features = []
    for feature in model.raw.get("current_structure", {}).get("features", []):
        display_px = feature.get("display_px")
        if not isinstance(display_px, dict):
            continue
        geometry = _scene_geometry_from_display_px(display_px)
        if geometry is None:
            continue
        features.append(
            {
                "id": feature["id"],
                "type": feature.get("type", "feature"),
                "status": feature.get("status", "unknown"),
                "room": feature.get("room"),
                "between": feature.get("between", []),
                "geometry": geometry,
                "material": _feature_material(feature),
                "evidence_photo_paths": feature.get("evidence_photo_paths", []),
            }
        )
    return features


def _site_material(element: dict[str, Any]) -> str:
    category = str(element.get("category") or element.get("surface") or element.get("type", ""))
    element_type = str(element.get("type", ""))
    if "deck" in category or "deck" in element_type:
        return "deck_timber"
    if category in {"hardscape", "driveway", "concrete_pad", "concrete_path"} or "path" in element_type:
        return "paver_concrete"
    if category in {"building", "accessory_cottage"} or element_type in {"outbuilding", "accessory_cottage"}:
        return "painted_wall"
    return "lawn"


def _site_height(material: str) -> float:
    if material == "painted_wall":
        return 2.7
    if material == "deck_timber":
        return 0.12
    if material == "paver_concrete":
        return 0.06
    return 0.01


def _site_config(model: HouseModel) -> list[dict[str, Any]]:
    site = []
    for element in model.raw.get("current_site", {}).get("elements", []):
        layout = element.get("display_px") or element.get("layout")
        if not isinstance(layout, dict):
            continue
        geometry = _scene_geometry_from_display_px(layout)
        if geometry is None:
            continue
        material = _site_material(element)
        site.append(
            {
                "id": element["id"],
                "type": element.get("type", "site"),
                "surface": element.get("surface"),
                "category": element.get("category"),
                "geometry": geometry,
                "material": material,
                "height": _site_height(material),
            }
        )
    return site


def _fixture_config() -> list[dict[str, Any]]:
    fixtures = []
    for fixture in PHOTO_FIXTURE_SPECS:
        geometry = _scene_geometry_from_display_px(fixture["display_px"])
        if geometry is None:
            continue
        fixtures.append(
            {
                "id": fixture["id"],
                "room": fixture["room"],
                "geometry": geometry,
                "height": fixture["height"],
                "material": fixture["material"],
                "evidence_photo_paths": fixture["evidence_photo_paths"],
            }
        )
    return fixtures


def build_house_3d_config(model: HouseModel) -> dict[str, Any]:
    rooms, warnings = _room_config(model)
    return {
        "title": "House 3D Viewer",
        "units": model.units,
        "orientation": model.raw.get("orientation", {}),
        "rooms": rooms,
        "features": _feature_config(model),
        "site": _site_config(model),
        "walls": _wall_config(model),
        "wall_source": "curated-matplotlib-wall-network",
        "fixtures": _fixture_config(),
        "start_camera": START_CAMERA,
        "materials": MATERIALS,
        "warnings": warnings,
    }


def render_house_3d_html(model: HouseModel) -> str:
    config_json = json.dumps(build_house_3d_config(model), separators=(",", ":"))
    title = escape("House 3D Viewer")
    module_script = _module_script()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; overflow: hidden; background: #d8d4ca; font-family: Arial, sans-serif; }}
    #house-3d-stage {{ position: fixed; inset: 0; }}
    #house-3d-status {{
      position: fixed; left: 14px; top: 14px; z-index: 2; max-width: 360px;
      padding: 10px 12px; border: 1px solid rgba(40, 44, 42, 0.18);
      border-radius: 6px; background: rgba(255, 253, 248, 0.92); color: #1f2522;
      font-size: 13px; line-height: 1.35;
    }}
    #house-3d-stage canvas {{ display: block; width: 100%; height: 100%; }}
    #reset-view {{
      position: fixed; right: 14px; top: 14px; z-index: 2;
      border: 1px solid rgba(40, 44, 42, 0.2); border-radius: 5px;
      padding: 8px 10px; background: rgba(255, 253, 248, 0.92);
      color: #1f2522; font: inherit; cursor: pointer;
    }}
    @media (max-width: 560px) {{
      #house-3d-status {{
        left: 12px; right: 12px; top: 12px; max-width: none;
        font-size: 12px;
      }}
      #reset-view {{
        top: auto; right: 12px; bottom: 12px;
      }}
    }}
  </style>
  <script type="importmap">
  {{
    "imports": {{
      "three": "https://cdn.jsdelivr.net/npm/three@{THREE_VERSION}/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@{THREE_VERSION}/examples/jsm/"
    }}
  }}
  </script>
</head>
<body>
  <main id="house-3d-stage" aria-label="Interactive 3D house viewer"></main>
  <aside id="house-3d-status">Click the scene to explore. Use W A S D, mouse look, and Mouse wheel height.</aside>
  <button id="reset-view" type="button">Reset view</button>
  <script type="application/json" id="house-3d-config">{config_json}</script>
  <script type="module">
{module_script}
  </script>
</body>
</html>
"""


def _module_script() -> str:
    return """    import * as THREE from 'three';
    import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
    import WebGL from 'three/addons/capabilities/WebGL.js';

    const config = JSON.parse(document.getElementById('house-3d-config').textContent);
    const stage = document.getElementById('house-3d-stage');
    const status = document.getElementById('house-3d-status');
    const resetButton = document.getElementById('reset-view');
    const keysPressed = new Set();
    const clock = new THREE.Clock();
    const materialCache = new Map();
    let camera;
    let controls;
    let renderer;
    let scene;
    const MIN_CAMERA_HEIGHT = 0.45;
    const MAX_CAMERA_HEIGHT = 5.4;

    function showUnsupported(message) {
      status.textContent = message;
    }

    function createRenderer() {
      const nextRenderer = new THREE.WebGLRenderer({ antialias: true });
      nextRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      nextRenderer.setSize(window.innerWidth, window.innerHeight);
      nextRenderer.setClearColor(0xd8d4ca, 1);
      nextRenderer.outputColorSpace = THREE.SRGBColorSpace;
      nextRenderer.shadowMap.enabled = true;
      nextRenderer.shadowMap.type = THREE.PCFSoftShadowMap;
      stage.appendChild(nextRenderer.domElement);
      return nextRenderer;
    }

    function createScene() {
      const nextScene = new THREE.Scene();
      nextScene.background = new THREE.Color(0xd8d4ca);
      nextScene.fog = new THREE.Fog(0xd8d4ca, 32, 80);
      nextScene.add(new THREE.HemisphereLight(0xffffff, 0x8f8a7d, 1.45));
      const sun = new THREE.DirectionalLight(0xffffff, 1.5);
      sun.position.set(-8, 12, -6);
      sun.castShadow = true;
      sun.shadow.mapSize.set(1024, 1024);
      nextScene.add(sun);
      const ground = new THREE.Mesh(
        new THREE.PlaneGeometry(70, 32),
        new THREE.MeshStandardMaterial({ color: 0xa8bd90, roughness: 1 })
      );
      ground.rotation.x = -Math.PI / 2;
      ground.position.set(10, -0.08, 4.5);
      ground.receiveShadow = true;
      nextScene.add(ground);
      return nextScene;
    }

    function patternTexture(item) {
      if (!item.pattern) return null;
      const canvas = document.createElement('canvas');
      canvas.width = 128;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = item.color || '#eeeeee';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      if (item.pattern === 'planks' || item.pattern === 'deck') {
        ctx.strokeStyle = 'rgba(55, 45, 34, 0.32)';
        ctx.lineWidth = item.pattern === 'deck' ? 3 : 2;
        for (let y = 10; y < canvas.height; y += item.pattern === 'deck' ? 18 : 20) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(canvas.width, y + 4);
          ctx.stroke();
        }
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.16)';
        for (let x = 24; x < canvas.width; x += 32) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, canvas.height);
          ctx.stroke();
        }
      } else if (item.pattern === 'carpet') {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
        for (let x = 0; x < canvas.width; x += 7) {
          for (let y = 0; y < canvas.height; y += 9) {
            ctx.fillRect(x, y, 1, 1);
          }
        }
      } else if (item.pattern === 'tile') {
        ctx.strokeStyle = 'rgba(95, 105, 105, 0.24)';
        ctx.lineWidth = 2;
        for (let x = 0; x <= canvas.width; x += 32) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, canvas.height);
          ctx.stroke();
        }
        for (let y = 0; y <= canvas.height; y += 32) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(canvas.width, y);
          ctx.stroke();
        }
      }
      const texture = new THREE.CanvasTexture(canvas);
      texture.wrapS = THREE.RepeatWrapping;
      texture.wrapT = THREE.RepeatWrapping;
      texture.repeat.set(3, 3);
      texture.colorSpace = THREE.SRGBColorSpace;
      return texture;
    }

    function materialFor(id) {
      if (materialCache.has(id)) return materialCache.get(id);
      const item = config.materials[id] || config.materials.painted_wall || {};
      const options = {
        color: new THREE.Color(item.color || '#eeeeee'),
        roughness: item.roughness ?? 0.85,
        metalness: 0,
        side: THREE.DoubleSide
      };
      const texture = patternTexture(item);
      if (texture) options.map = texture;
      if (item.opacity !== undefined) {
        options.transparent = true;
        options.opacity = item.opacity;
        options.depthWrite = false;
      }
      const material = new THREE.MeshStandardMaterial(options);
      materialCache.set(id, material);
      return material;
    }

    function buildPolygonFloor(scene, points, material, roomId) {
      const shape = new THREE.Shape();
      points.forEach((point, index) => {
        if (index === 0) shape.moveTo(point.x, point.z);
        else shape.lineTo(point.x, point.z);
      });
      shape.closePath();
      const mesh = new THREE.Mesh(new THREE.ShapeGeometry(shape), material);
      mesh.rotation.x = Math.PI / 2;
      mesh.userData.roomId = roomId;
      mesh.name = `floor:${roomId}`;
      return mesh;
    }

    function buildFloor(scene, room) {
      const material = materialFor(room.floor_material);
      let mesh;
      if (room.geometry.type === 'rect') {
        const geo = new THREE.BoxGeometry(room.geometry.width, 0.04, room.geometry.depth);
        mesh = new THREE.Mesh(geo, material);
        mesh.position.set(
          room.geometry.x + room.geometry.width / 2,
          0,
          room.geometry.z + room.geometry.depth / 2
        );
      } else {
        mesh = buildPolygonFloor(scene, room.geometry.points, material, room.id);
      }
      mesh.userData.roomId = room.id;
      mesh.name = `floor:${room.id}`;
      mesh.receiveShadow = true;
      scene.add(mesh);
    }

    function rectPoints(geometry) {
      return [
        { x: geometry.x, z: geometry.z },
        { x: geometry.x + geometry.width, z: geometry.z },
        { x: geometry.x + geometry.width, z: geometry.z + geometry.depth },
        { x: geometry.x, z: geometry.z + geometry.depth }
      ];
    }

    function geometryPoints(geometry) {
      if (geometry.type === 'rect') return rectPoints(geometry);
      if (geometry.type === 'polygon') return geometry.points || [];
      return [];
    }

    function edgeKey(a, b) {
      const pointKey = (point) => `${Math.round(point.x * 20) / 20}:${Math.round(point.z * 20) / 20}`;
      return [pointKey(a), pointKey(b)].sort().join('|');
    }

    function geometryBounds(geometry) {
      if (geometry.type === 'rect') {
        return {
          minX: geometry.x,
          maxX: geometry.x + geometry.width,
          minZ: geometry.z,
          maxZ: geometry.z + geometry.depth
        };
      }
      const points = geometry.type === 'multi_polygon'
        ? geometry.polygons.flat()
        : geometry.points || [];
      return boundsFromPoints(points);
    }

    function intervalsOverlap(aMin, aMax, bMin, bMax) {
      return Math.min(aMax, bMax) - Math.max(aMin, bMin);
    }

    function edgeCrossesOpening(start, end, roomId) {
      const horizontal = Math.abs(end.x - start.x) >= Math.abs(end.z - start.z);
      const edgeMinX = Math.min(start.x, end.x);
      const edgeMaxX = Math.max(start.x, end.x);
      const edgeMinZ = Math.min(start.z, end.z);
      const edgeMaxZ = Math.max(start.z, end.z);
      return config.features.some((feature) => {
        if (!['door', 'door_group', 'slider', 'sliding_door', 'opening'].includes(feature.type)) {
          return false;
        }
        const linked = feature.room === roomId || (feature.between || []).includes(roomId);
        if (!linked) return false;
        const bounds = geometryBounds(feature.geometry);
        if (horizontal) {
          const near = Math.abs(((start.z + end.z) / 2) - ((bounds.minZ + bounds.maxZ) / 2)) < 0.24;
          return near && intervalsOverlap(edgeMinX, edgeMaxX, bounds.minX, bounds.maxX) > 0.18;
        }
        const near = Math.abs(((start.x + end.x) / 2) - ((bounds.minX + bounds.maxX) / 2)) < 0.24;
        return near && intervalsOverlap(edgeMinZ, edgeMaxZ, bounds.minZ, bounds.maxZ) > 0.18;
      });
    }

    function edgeWall(scene, start, end, height, thickness, name) {
      const dx = end.x - start.x;
      const dz = end.z - start.z;
      const length = Math.hypot(dx, dz);
      if (length < 0.18) return null;
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(length, height, thickness),
        materialFor('painted_wall')
      );
      mesh.position.set((start.x + end.x) / 2, height / 2, (start.z + end.z) / 2);
      mesh.rotation.y = -Math.atan2(dz, dx);
      mesh.name = name;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);
      return mesh;
    }

    function buildRoomOutlineWalls(scene, room, wallKeys) {
      const points = geometryPoints(room.geometry);
      if (points.length < 2) return;
      const height = Math.min(room.height || 2.4, 2.35);
      const thickness = 0.08;
      points.forEach((start, index) => {
        const end = points[(index + 1) % points.length];
        const key = edgeKey(start, end);
        if (wallKeys.has(key) || edgeCrossesOpening(start, end, room.id)) return;
        wallKeys.add(key);
        edgeWall(scene, start, end, height, thickness, `wall:${room.id}:${index}`);
      });
    }

    function buildCuratedWall(scene, wall) {
      wall.segments.forEach((segment, index) => {
        edgeWall(
          scene,
          { x: segment.x1, z: segment.z1 },
          { x: segment.x2, z: segment.z2 },
          wall.height,
          wall.thickness,
          `wall:${wall.id}:${index}`
        );
      });
    }

    function boundsFromPoints(points) {
      return points.reduce((bounds, point) => ({
        minX: Math.min(bounds.minX, point.x),
        maxX: Math.max(bounds.maxX, point.x),
        minZ: Math.min(bounds.minZ, point.z),
        maxZ: Math.max(bounds.maxZ, point.z)
      }), { minX: Infinity, maxX: -Infinity, minZ: Infinity, maxZ: -Infinity });
    }

    function polygonMesh(points, material, height, name) {
      const shape = new THREE.Shape();
      points.forEach((point, index) => {
        if (index === 0) shape.moveTo(point.x, point.z);
        else shape.lineTo(point.x, point.z);
      });
      shape.closePath();
      const mesh = new THREE.Mesh(new THREE.ShapeGeometry(shape), material);
      mesh.rotation.x = Math.PI / 2;
      mesh.position.y = height;
      mesh.name = name;
      mesh.receiveShadow = true;
      return mesh;
    }

    function buildSiteElement(scene, element) {
      const material = materialFor(element.material);
      const height = element.height || 0.06;
      if (element.geometry.type === 'rect') {
        const geo = new THREE.BoxGeometry(element.geometry.width, height, element.geometry.depth);
        const mesh = new THREE.Mesh(geo, material);
        mesh.position.set(
          element.geometry.x + element.geometry.width / 2,
          height / 2,
          element.geometry.z + element.geometry.depth / 2
        );
        mesh.name = `site:${element.id}`;
        mesh.castShadow = height > 0.4;
        mesh.receiveShadow = true;
        scene.add(mesh);
      } else if (element.geometry.type === 'polygon') {
        scene.add(polygonMesh(element.geometry.points, material, height, `site:${element.id}`));
      } else if (element.geometry.type === 'multi_polygon') {
        element.geometry.polygons.forEach((polygon, index) => {
          scene.add(polygonMesh(polygon, material, height, `site:${element.id}:${index}`));
        });
      }
    }

    function wallSurroundPanelForBounds(bounds, feature, suffix, bottom, height) {
      if (height <= 0.04) return null;
      const width = Math.max(bounds.maxX - bounds.minX, 0.08);
      const depth = Math.max(bounds.maxZ - bounds.minZ, 0.08);
      const horizontal = width >= depth;
      const geo = horizontal
        ? new THREE.BoxGeometry(width, height, 0.065)
        : new THREE.BoxGeometry(0.065, height, depth);
      const mesh = new THREE.Mesh(geo, materialFor('painted_wall'));
      mesh.position.set(
        (bounds.minX + bounds.maxX) / 2,
        bottom + height / 2,
        (bounds.minZ + bounds.maxZ) / 2
      );
      mesh.name = `feature:${feature.id}:wall-surround:${suffix}:${bottom.toFixed(2)}`;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      return mesh;
    }

    function buildOpeningSurround(feature) {
      if (feature.type === 'opening') return null;
      const group = new THREE.Group();
      group.name = `feature:${feature.id}:wall-surround`;
      const addSurroundForBounds = (bounds, suffix) => {
        const doorLike = ['door', 'door_group', 'slider', 'sliding_door'].includes(feature.type);
        const bottom = doorLike ? 0.08 : 0.85;
        const panelHeight = doorLike ? 2.05 : 1.15;
        const wallHeight = 2.35;
        if (!doorLike) {
          const sill = wallSurroundPanelForBounds(bounds, feature, `${suffix}:sill`, 0, bottom);
          if (sill) group.add(sill);
        }
        const headerHeight = wallHeight - (bottom + panelHeight);
        const header = wallSurroundPanelForBounds(bounds, feature, `${suffix}:header`, bottom + panelHeight, headerHeight);
        if (header) group.add(header);
      };
      if (feature.geometry.type === 'multi_polygon') {
        feature.geometry.polygons.forEach((polygon, index) => {
          addSurroundForBounds(boundsFromPoints(polygon), index);
        });
      } else {
        const bounds = geometryBounds(feature.geometry);
        if (!Number.isFinite(bounds.minX)) return null;
        addSurroundForBounds(bounds, 0);
      }
      return group.children.length ? group : null;
    }

    function panelMeshesForBounds(bounds, feature, suffix) {
      const width = Math.max(bounds.maxX - bounds.minX, 0.08);
      const depth = Math.max(bounds.maxZ - bounds.minZ, 0.08);
      const horizontal = width >= depth;
      const doorLike = ['door', 'door_group', 'slider', 'sliding_door', 'opening'].includes(feature.type);
      const panelHeight = doorLike ? 2.05 : 1.15;
      const bottom = doorLike ? 0.08 : 0.85;
      const group = new THREE.Group();
      const panelGeo = horizontal
        ? new THREE.BoxGeometry(width, panelHeight, 0.035)
        : new THREE.BoxGeometry(0.035, panelHeight, depth);
      const panel = new THREE.Mesh(panelGeo, materialFor(feature.material));
      panel.position.set((bounds.minX + bounds.maxX) / 2, bottom + panelHeight / 2, (bounds.minZ + bounds.maxZ) / 2);
      panel.name = `feature:${feature.id}:panel:${suffix}`;
      panel.userData.featureId = feature.id;
      group.add(panel);

      const frameMaterial = materialFor('white_frame');
      const span = horizontal ? width : depth;
      const frameDepth = horizontal ? 0.055 : span;
      const frameWidth = horizontal ? span : 0.055;
      const topBottomGeo = new THREE.BoxGeometry(frameWidth, 0.07, frameDepth);
      const sideGeo = horizontal
        ? new THREE.BoxGeometry(0.07, panelHeight + 0.1, 0.06)
        : new THREE.BoxGeometry(0.06, panelHeight + 0.1, 0.07);
      const centerX = (bounds.minX + bounds.maxX) / 2;
      const centerZ = (bounds.minZ + bounds.maxZ) / 2;
      const lowFrame = new THREE.Mesh(topBottomGeo, frameMaterial);
      lowFrame.position.set(centerX, bottom, centerZ);
      const highFrame = new THREE.Mesh(topBottomGeo, frameMaterial);
      highFrame.position.set(centerX, bottom + panelHeight, centerZ);
      const sideA = new THREE.Mesh(sideGeo, frameMaterial);
      const sideB = new THREE.Mesh(sideGeo, frameMaterial);
      if (horizontal) {
        sideA.position.set(bounds.minX, bottom + panelHeight / 2, centerZ);
        sideB.position.set(bounds.maxX, bottom + panelHeight / 2, centerZ);
      } else {
        sideA.position.set(centerX, bottom + panelHeight / 2, bounds.minZ);
        sideB.position.set(centerX, bottom + panelHeight / 2, bounds.maxZ);
      }
      [lowFrame, highFrame, sideA, sideB].forEach((frame, index) => {
        frame.name = `feature:${feature.id}:frame:${suffix}:${index}`;
        frame.castShadow = true;
        frame.receiveShadow = true;
        group.add(frame);
      });
      return group;
    }

    function buildOpeningPanel(feature) {
      if (feature.type === 'opening') return null;
      const group = new THREE.Group();
      group.name = `feature:${feature.id}`;
      if (feature.geometry.type === 'multi_polygon') {
        feature.geometry.polygons.forEach((polygon, index) => {
          group.add(panelMeshesForBounds(boundsFromPoints(polygon), feature, index));
        });
      } else {
        const bounds = geometryBounds(feature.geometry);
        if (!Number.isFinite(bounds.minX)) return null;
        group.add(panelMeshesForBounds(bounds, feature, 0));
      }
      return group;
    }

    function buildFixture(scene, fixture) {
      const bounds = geometryBounds(fixture.geometry);
      if (!Number.isFinite(bounds.minX)) return;
      const width = Math.max(bounds.maxX - bounds.minX, 0.12);
      const depth = Math.max(bounds.maxZ - bounds.minZ, 0.12);
      const height = fixture.height || 0.7;
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(width, height, depth),
        materialFor(fixture.material)
      );
      mesh.position.set((bounds.minX + bounds.maxX) / 2, 0.04 + height / 2, (bounds.minZ + bounds.maxZ) / 2);
      mesh.name = `fixture:${fixture.id}`;
      mesh.userData.fixtureId = fixture.id;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);
    }

    function resetCamera() {
      const start = config.start_camera || {
        position: { x: 7.2, y: 1.65, z: 4.4 },
        look_at: { x: 9.5, y: 1.45, z: 5.4 }
      };
      camera.position.set(start.position.x, start.position.y, start.position.z);
      camera.rotation.set(0, 0, 0);
      controls.getObject().lookAt(start.look_at.x, start.look_at.y, start.look_at.z);
    }

    function adjustCameraHeight(deltaY) {
      const step = keysPressed.has('ShiftLeft') || keysPressed.has('ShiftRight') ? 0.55 : 0.28;
      const direction = deltaY < 0 ? 1 : -1;
      camera.position.y = THREE.MathUtils.clamp(
        camera.position.y + direction * step,
        MIN_CAMERA_HEIGHT,
        MAX_CAMERA_HEIGHT
      );
    }

    function moveCamera(delta) {
      const speed = keysPressed.has('ShiftLeft') || keysPressed.has('ShiftRight') ? 5.2 : 2.7;
      const step = speed * delta;
      if (keysPressed.has('KeyW') || keysPressed.has('ArrowUp')) controls.moveForward(step);
      if (keysPressed.has('KeyS') || keysPressed.has('ArrowDown')) controls.moveForward(-step);
      if (keysPressed.has('KeyA') || keysPressed.has('ArrowLeft')) controls.moveRight(-step);
      if (keysPressed.has('KeyD') || keysPressed.has('ArrowRight')) controls.moveRight(step);
      if (keysPressed.has('KeyQ')) camera.position.y = THREE.MathUtils.clamp(camera.position.y - step, MIN_CAMERA_HEIGHT, MAX_CAMERA_HEIGHT);
      if (keysPressed.has('KeyE')) camera.position.y = THREE.MathUtils.clamp(camera.position.y + step, MIN_CAMERA_HEIGHT, MAX_CAMERA_HEIGHT);
    }

    function animate() {
      requestAnimationFrame(animate);
      moveCamera(clock.getDelta());
      renderer.render(scene, camera);
    }

    function startViewer() {
      if (!WebGL.isWebGL2Available()) {
        showUnsupported('WebGL is unavailable in this browser.');
        return;
      }
      scene = createScene();
      renderer = createRenderer();
      camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.05, 120);
      controls = new PointerLockControls(camera, renderer.domElement);
      scene.add(controls.getObject());
      resetCamera();

      config.site.forEach((element) => buildSiteElement(scene, element));
      config.rooms.forEach((room) => buildFloor(scene, room));
      if (config.walls && config.walls.length) {
        config.walls.forEach((wall) => buildCuratedWall(scene, wall));
      } else {
        const wallKeys = new Set();
        config.rooms.forEach((room) => buildRoomOutlineWalls(scene, room, wallKeys));
      }
      config.features.map(buildOpeningSurround).filter(Boolean).forEach((mesh) => scene.add(mesh));
      config.features.map(buildOpeningPanel).filter(Boolean).forEach((mesh) => scene.add(mesh));
      config.fixtures.forEach((fixture) => buildFixture(scene, fixture));

      stage.addEventListener('click', () => controls.lock());
      renderer.domElement.addEventListener('wheel', (event) => {
        event.preventDefault();
        adjustCameraHeight(event.deltaY);
      }, { passive: false });
      resetButton.addEventListener('click', resetCamera);
      document.addEventListener('keydown', (event) => {
        keysPressed.add(event.code);
        if (event.code === 'KeyR') resetCamera();
      });
      document.addEventListener('keyup', (event) => keysPressed.delete(event.code));
      window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });

      status.textContent = `${config.title}: ${config.rooms.length} rooms, ${config.features.length} openings/features, ${config.fixtures.length} photo cues. Mouse wheel raises/lowers the view.`;
      animate();
    }

    startViewer();
"""
