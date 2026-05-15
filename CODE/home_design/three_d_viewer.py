from __future__ import annotations

import json
from html import escape
from typing import Any

from .model import HouseModel


THREE_VERSION = "0.160.0"

MATERIALS = {
    "timber_floor": {"kind": "floor", "color": "#d2b58d", "roughness": 0.78},
    "wet_tile": {"kind": "floor", "color": "#d7dee0", "roughness": 0.62},
    "painted_wall": {"kind": "wall", "color": "#eee9df", "roughness": 0.86},
    "glazing": {"kind": "transparent", "color": "#b8d8e6", "opacity": 0.36},
    "deck_timber": {"kind": "site", "color": "#9a6438", "roughness": 0.72},
    "paver_concrete": {"kind": "site", "color": "#c9c4b8", "roughness": 0.9},
    "lawn": {"kind": "site", "color": "#78a85f", "roughness": 1.0},
}

WET_ROOM_IDS = {"bathroom", "laundry", "toilet"}


def _room_material(room_id: str, category: str) -> str:
    if room_id in WET_ROOM_IDS:
        return "wet_tile"
    return "timber_floor"


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
    for room in model.rooms:
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
                "height": float(room.dimensions_m.get("height") or 2.4),
                "floor_material": _room_material(room.id, room.category),
                "wall_material": "painted_wall",
                "notes": room.notes,
            }
        )
    return rooms, warnings


def build_house_3d_config(model: HouseModel) -> dict[str, Any]:
    rooms, warnings = _room_config(model)
    return {
        "title": "House 3D Viewer",
        "units": model.units,
        "orientation": model.raw.get("orientation", {}),
        "rooms": rooms,
        "features": [],
        "site": [],
        "materials": MATERIALS,
        "warnings": warnings,
    }


def render_house_3d_html(model: HouseModel) -> str:
    config_json = json.dumps(build_house_3d_config(model), separators=(",", ":"))
    title = escape("House 3D Viewer")
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
  <aside id="house-3d-status">Click the scene to explore. Use W A S D and mouse look.</aside>
  <script type="application/json" id="house-3d-config">{config_json}</script>
  <script type="module">
    import * as THREE from 'three';
    import {{ PointerLockControls }} from 'three/addons/controls/PointerLockControls.js';
    import WebGL from 'three/addons/capabilities/WebGL.js';

    const config = JSON.parse(document.getElementById('house-3d-config').textContent);
    const stage = document.getElementById('house-3d-stage');
    const status = document.getElementById('house-3d-status');

    function showUnsupported(message) {{
      status.textContent = message;
    }}

    if (!WebGL.isWebGL2Available()) {{
      showUnsupported('WebGL is unavailable in this browser.');
    }} else {{
      status.textContent = config.title + ' ready.';
    }}
  </script>
</body>
</html>
"""
