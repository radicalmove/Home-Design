# House 3D Viewer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a keyboard/mouse-explorable Three.js `OUTPUT/house_3d.html` view of the current house from `DATA/house_model.json`.

**Architecture:** Add a focused Python renderer that extracts a JSON scene config from the existing house model, then embeds that config into a standalone Three.js HTML page. Keep geometry/model extraction in Python and browser rendering/interactions in vanilla JavaScript so future layout scenarios can reuse the same data shape.

**Tech Stack:** Python standard library, `unittest`, generated HTML, vanilla JavaScript, Three.js ES modules loaded by import map from one CDN/version, existing `CODE.home_design` model and CLI modules.

---

## Implementation Notes

- Work tests-first. Do not write production code before the matching failing test.
- The worktree already has unrelated modified files:
  - `CODE/home_design/reference_plan.py`
  - `DATA/house_model.json`
  - `OUTPUT/reference_plan.html`
  - `OUTPUT/reference_plan.svg`
  - `tests/test_house_model.py`
  - `tests/test_reference_plan.py`
- Do not stage, overwrite, or revert those unrelated changes unless the user explicitly asks.
- Use the official Three.js import-map pattern: import `three` and `three/addons/` from the same CDN and version.
- Start with procedural/generated materials. Do not block on AI image assets.

## File Structure

- Create `CODE/home_design/three_d_viewer.py`
  - Owns 3D scene config extraction and generated HTML.
  - Exposes `build_house_3d_config(model: HouseModel) -> dict[str, object]`.
  - Exposes `render_house_3d_html(model: HouseModel) -> str`.
  - Keeps the data contract explicit and testable.

- Modify `CODE/home_design/cli.py`
  - Adds `house-3d` to the command choices.
  - Writes `.html` output using `render_house_3d_html`.

- Create `tests/test_house_3d_viewer.py`
  - Tests the renderer contract, embedded config, representative model IDs, material categories, and JavaScript interaction hooks.

- Modify `tests/test_cli.py`
  - Tests parser support for `house-3d`.
  - Tests that `main(["house-3d", "--output", path])` writes a usable HTML file.

- Generate `OUTPUT/house_3d.html`
  - Generated artifact only. Do not hand-edit it.

## Task 1: Renderer HTML Shell

**Files:**
- Create: `tests/test_house_3d_viewer.py`
- Create: `CODE/home_design/three_d_viewer.py`

- [ ] **Step 1: Write the failing renderer shell test**

Create `tests/test_house_3d_viewer.py`:

```python
import unittest

from CODE.home_design.model import load_model
from CODE.home_design.three_d_viewer import render_house_3d_html


class House3DViewerHtmlTests(unittest.TestCase):
    def test_house_3d_viewer_returns_standalone_html_shell(self):
        model = load_model("DATA/house_model.json")

        html = render_house_3d_html(model)

        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn("<title>House 3D Viewer</title>", html)
        self.assertIn('id="house-3d-stage"', html)
        self.assertIn('id="house-3d-status"', html)
        self.assertIn('type="importmap"', html)
        self.assertIn('"three": "https://cdn.jsdelivr.net/npm/three@', html)
        self.assertIn('"three/addons/": "https://cdn.jsdelivr.net/npm/three@', html)
        self.assertIn("PointerLockControls", html)
        self.assertIn("WebGL", html)
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_house_3d_viewer.House3DViewerHtmlTests.test_house_3d_viewer_returns_standalone_html_shell -v
```

Expected: FAIL with `ModuleNotFoundError` for `CODE.home_design.three_d_viewer`.

- [ ] **Step 3: Implement the minimal HTML renderer**

Create `CODE/home_design/three_d_viewer.py`:

```python
from __future__ import annotations

import json
from html import escape
from typing import Any

from .model import HouseModel


THREE_VERSION = "0.160.0"


def build_house_3d_config(model: HouseModel) -> dict[str, Any]:
    return {
        "title": "House 3D Viewer",
        "units": model.units,
        "rooms": [],
        "features": [],
        "site": [],
        "materials": {},
        "warnings": [],
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_house_3d_viewer.House3DViewerHtmlTests.test_house_3d_viewer_returns_standalone_html_shell -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add CODE/home_design/three_d_viewer.py tests/test_house_3d_viewer.py
git commit -m "Add house 3D viewer HTML shell"
```

## Task 2: Scene Config From Current Model

**Files:**
- Modify: `CODE/home_design/three_d_viewer.py`
- Modify: `tests/test_house_3d_viewer.py`

- [ ] **Step 1: Write the failing scene config test**

Add to `tests/test_house_3d_viewer.py`:

```python
import json
import re


def _embedded_config(html: str) -> dict:
    match = re.search(
        r'<script type="application/json" id="house-3d-config">(.*?)</script>',
        html,
        re.S,
    )
    if match is None:
        raise AssertionError("house-3d-config script not found")
    return json.loads(match.group(1))
```

Then add:

```python
    def test_house_3d_config_includes_current_room_geometry(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))
        room_ids = {room["id"] for room in config["rooms"]}

        for room_id in [
            "kitchen_dining",
            "lounge",
            "sunroom",
            "hallway",
            "master_bedroom",
            "office",
            "bathroom",
            "bedroom_2",
            "entrance",
            "laundry",
            "toilet",
        ]:
            self.assertIn(room_id, room_ids)

        kitchen = next(room for room in config["rooms"] if room["id"] == "kitchen_dining")
        self.assertEqual(kitchen["geometry"]["type"], "rect")
        self.assertEqual(kitchen["geometry"]["x"], 6.9)
        self.assertEqual(kitchen["geometry"]["z"], 0.8)
        self.assertEqual(kitchen["height"], 2.4)

        sunroom = next(room for room in config["rooms"] if room["id"] == "sunroom")
        self.assertEqual(sunroom["geometry"]["type"], "polygon")
        self.assertGreaterEqual(len(sunroom["geometry"]["points"]), 7)

    def test_house_3d_config_includes_material_categories(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))

        for material_id in [
            "timber_floor",
            "wet_tile",
            "painted_wall",
            "glazing",
            "deck_timber",
            "paver_concrete",
            "lawn",
        ]:
            self.assertIn(material_id, config["materials"])
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_house_3d_viewer.House3DViewerHtmlTests.test_house_3d_config_includes_current_room_geometry \
  tests.test_house_3d_viewer.House3DViewerHtmlTests.test_house_3d_config_includes_material_categories \
  -v
```

Expected: FAIL because `rooms` and `materials` are empty.

- [ ] **Step 3: Implement room/material config extraction**

Update `CODE/home_design/three_d_viewer.py`:

```python
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
```

Then update `build_house_3d_config` to use those helpers:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
python3 -m unittest tests.test_house_3d_viewer -v
```

Expected: all current `House3DViewerHtmlTests` PASS.

- [ ] **Step 5: Commit**

```bash
git add CODE/home_design/three_d_viewer.py tests/test_house_3d_viewer.py
git commit -m "Embed current house 3D scene config"
```

## Task 3: Openings And Site Context Config

**Files:**
- Modify: `CODE/home_design/three_d_viewer.py`
- Modify: `tests/test_house_3d_viewer.py`

- [ ] **Step 1: Write the failing feature/site tests**

Add:

```python
    def test_house_3d_config_includes_photo_verified_openings(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))
        feature_ids = {feature["id"] for feature in config["features"]}

        for feature_id in [
            "deck_door_group",
            "sunroom_lounge_slider",
            "entrance_deck_slider",
            "sunroom_wraparound_glazing",
            "bedroom2_se_window",
            "laundry_east_window",
        ]:
            self.assertIn(feature_id, feature_ids)

        sunroom_glazing = next(feature for feature in config["features"] if feature["id"] == "sunroom_wraparound_glazing")
        self.assertEqual(sunroom_glazing["material"], "glazing")
        self.assertTrue(sunroom_glazing["evidence_photo_paths"])

    def test_house_3d_config_includes_site_context_elements(self):
        model = load_model("DATA/house_model.json")

        config = _embedded_config(render_house_3d_html(model))
        site_ids = {element["id"] for element in config["site"]}

        for element_id in [
            "property_boundary",
            "upper_side_driveway",
            "rear_timber_deck",
            "garage_shed",
            "cottage",
        ]:
            self.assertIn(element_id, site_ids)

        deck = next(element for element in config["site"] if element["id"] == "rear_timber_deck")
        self.assertEqual(deck["material"], "deck_timber")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_house_3d_viewer.House3DViewerHtmlTests.test_house_3d_config_includes_photo_verified_openings \
  tests.test_house_3d_viewer.House3DViewerHtmlTests.test_house_3d_config_includes_site_context_elements \
  -v
```

Expected: FAIL because `features` and `site` are empty.

- [ ] **Step 3: Implement feature/site extraction**

Add helpers:

```python
PIXEL_TO_METRE = 0.81 / 22.0
REFERENCE_PIXEL_ORIGIN = {"x": 518.0, "y": 314.0}

GLAZING_TYPES = {"window", "window_group", "slider", "sliding_door"}


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
```

Add site material extraction:

```python
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


def _site_config(model: HouseModel) -> list[dict[str, Any]]:
    site = []
    for element in model.raw.get("current_site", {}).get("elements", []):
        layout = element.get("layout")
        if not isinstance(layout, dict):
            continue
        geometry = _scene_geometry_from_display_px(layout)
        if geometry is None:
            continue
        site.append(
            {
                "id": element["id"],
                "type": element.get("type", "site"),
                "surface": element.get("surface"),
                "category": element.get("category"),
                "geometry": geometry,
                "material": _site_material(element),
                "height": 0.08 if _site_material(element) != "painted_wall" else 2.7,
            }
        )
    return site
```

Update `build_house_3d_config` to include:

```python
"features": _feature_config(model),
"site": _site_config(model),
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
python3 -m unittest tests.test_house_3d_viewer -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add CODE/home_design/three_d_viewer.py tests/test_house_3d_viewer.py
git commit -m "Add 3D openings and site context config"
```

## Task 4: Three.js Scene Building And Controls

**Files:**
- Modify: `CODE/home_design/three_d_viewer.py`
- Modify: `tests/test_house_3d_viewer.py`

- [ ] **Step 1: Write the failing JavaScript behavior-string test**

Add:

```python
    def test_house_3d_viewer_includes_scene_builders_and_controls(self):
        model = load_model("DATA/house_model.json")

        html = render_house_3d_html(model)

        for function_name in [
            "function createRenderer",
            "function createScene",
            "function buildFloor",
            "function buildRectRoomWalls",
            "function buildPolygonFloor",
            "function buildSiteElement",
            "function animate",
            "function resetCamera",
        ]:
            self.assertIn(function_name, html)

        self.assertIn("new PointerLockControls", html)
        self.assertIn("keysPressed", html)
        self.assertIn("keydown", html)
        self.assertIn("keyup", html)
        self.assertIn("requestAnimationFrame(animate)", html)
        self.assertIn("userData.roomId", html)
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_house_3d_viewer.House3DViewerHtmlTests.test_house_3d_viewer_includes_scene_builders_and_controls -v
```

Expected: FAIL because the current module script is only a status placeholder.

- [ ] **Step 3: Implement minimal useful scene JavaScript**

Replace the placeholder module script with JavaScript that:

- Creates `THREE.Scene`, `PerspectiveCamera`, `WebGLRenderer`, hemisphere light, directional light, and a ground plane.
- Creates materials from `config.materials`.
- Builds floors from rect/polygon room geometry.
- Builds simple wall boxes around rectangular rooms first.
- Builds simplified site slabs/volumes.
- Adds transparent panels for feature geometries using the glazing material.
- Uses `PointerLockControls` with click-to-lock.
- Maintains `keysPressed` and moves the camera each frame.
- Adds a reset button or keyboard handler that calls `resetCamera`.

Use this minimum structure inside the module script:

```javascript
    function createRenderer() {
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setClearColor(0xd8d4ca, 1);
      stage.appendChild(renderer.domElement);
      return renderer;
    }

    function createScene() {
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0xd8d4ca);
      scene.add(new THREE.HemisphereLight(0xffffff, 0x8f8a7d, 1.8));
      const sun = new THREE.DirectionalLight(0xffffff, 1.5);
      sun.position.set(-8, 12, 6);
      scene.add(sun);
      return scene;
    }

    function materialFor(id) {
      const item = config.materials[id] || config.materials.painted_wall;
      const options = { color: new THREE.Color(item.color || '#eeeeee') };
      if (item.opacity !== undefined) {
        options.transparent = true;
        options.opacity = item.opacity;
      }
      return new THREE.MeshStandardMaterial(options);
    }

    function buildPolygonFloor(scene, points, material, roomId) {
      const shape = new THREE.Shape();
      points.forEach((point, index) => {
        if (index === 0) shape.moveTo(point.x, point.z);
        else shape.lineTo(point.x, point.z);
      });
      shape.closePath();
      const mesh = new THREE.Mesh(new THREE.ShapeGeometry(shape), material);
      mesh.rotation.x = -Math.PI / 2;
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
      scene.add(mesh);
    }

    function wallSegment(scene, x, z, width, depth, height, name) {
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(width, height, depth),
        materialFor('painted_wall')
      );
      mesh.position.set(x, height / 2, z);
      mesh.name = name;
      scene.add(mesh);
    }

    function buildRectRoomWalls(scene, room) {
      if (room.geometry.type !== 'rect') return;
      const wall = 0.12;
      const height = room.height || 2.4;
      const x = room.geometry.x;
      const z = room.geometry.z;
      const w = room.geometry.width;
      const d = room.geometry.depth;
      wallSegment(scene, x + w / 2, z, w, wall, height, `wall:${room.id}:north`);
      wallSegment(scene, x + w / 2, z + d, w, wall, height, `wall:${room.id}:south`);
      wallSegment(scene, x, z + d / 2, wall, d, height, `wall:${room.id}:west`);
      wallSegment(scene, x + w, z + d / 2, wall, d, height, `wall:${room.id}:east`);
    }
```

Keep the implementation simple. Do not try to solve perfect wall merging or exact opening cutouts in this task.

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
python3 -m unittest tests.test_house_3d_viewer -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add CODE/home_design/three_d_viewer.py tests/test_house_3d_viewer.py
git commit -m "Build interactive Three.js house scene"
```

## Task 5: CLI Command

**Files:**
- Modify: `CODE/home_design/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write the failing CLI tests**

Add to `tests/test_cli.py`:

```python
    def test_cli_accepts_house_3d_command(self):
        args = build_parser().parse_args(["house-3d", "--output", "OUTPUT/house_3d.html"])

        self.assertEqual(args.command, "house-3d")
        self.assertEqual(args.output, "OUTPUT/house_3d.html")

    def test_cli_can_write_house_3d_html(self):
        path = Path("/private/tmp/home-design-house-3d-test.html")
        result = main(["house-3d", "--output", str(path)])

        self.assertEqual(result, 0)
        html = path.read_text()
        self.assertIn("House 3D Viewer", html)
        self.assertIn('id="house-3d-config"', html)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_cli.CliTests.test_cli_accepts_house_3d_command \
  tests.test_cli.CliTests.test_cli_can_write_house_3d_html \
  -v
```

Expected: FAIL because `house-3d` is not a valid command.

- [ ] **Step 3: Add CLI support**

Modify `CODE/home_design/cli.py`:

```python
"house-3d",
```

Add a branch before the final `else`:

```python
    elif args.command == "house-3d":
        from pathlib import Path

        from .three_d_viewer import render_house_3d_html

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_house_3d_html(model))
        print(f"wrote {args.output}")
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_cli_accepts_house_3d_command tests.test_cli.CliTests.test_cli_can_write_house_3d_html -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add CODE/home_design/cli.py tests/test_cli.py
git commit -m "Add house 3D viewer CLI command"
```

## Task 6: Generate Artifact And Run Full Verification

**Files:**
- Create: `OUTPUT/house_3d.html`
- Modify if needed: `README.md`

- [ ] **Step 1: Generate the viewer**

Run:

```bash
python3 -m CODE.home_design.cli house-3d --output OUTPUT/house_3d.html
```

Expected: `wrote OUTPUT/house_3d.html`.

- [ ] **Step 2: Run full unit tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests PASS.

- [ ] **Step 3: Optionally document the command**

If the generated output works, add to `README.md`:

````markdown
Generate the current-house 3D viewer:

```bash
python3 -m CODE.home_design.cli house-3d --output OUTPUT/house_3d.html
```

Serve locally, then open `http://127.0.0.1:8765/OUTPUT/house_3d.html`.
````

If adding README docs, first add a simple check in `tests/test_cli.py` or skip docs if there is no existing README test pattern.

- [ ] **Step 4: Commit generated output and docs**

```bash
git add OUTPUT/house_3d.html README.md
git commit -m "Generate house 3D viewer output"
```

If `README.md` was not changed:

```bash
git add OUTPUT/house_3d.html
git commit -m "Generate house 3D viewer output"
```

## Task 7: Browser Visual Verification

**Files:**
- Modify: `CODE/home_design/three_d_viewer.py` only if visual verification exposes a real defect.
- Modify: `OUTPUT/house_3d.html` only by regenerating it from the CLI.

- [ ] **Step 1: Start a local server**

Run:

```bash
python3 -m http.server 8765
```

Expected: server listens on `http://127.0.0.1:8765/`.

- [ ] **Step 2: Open the generated viewer**

Open:

```text
http://127.0.0.1:8765/OUTPUT/house_3d.html
```

Expected:

- The page is not blank.
- Canvas pixels are non-background.
- The status panel is visible.
- The current-house scene includes floor/wall/site volumes.
- Mouse/pointer lock starts when clicking the scene.
- `W`, `A`, `S`, `D` moves the camera.
- Reset returns to the starting camera.

- [ ] **Step 3: Check browser console**

Expected: no uncaught JavaScript errors. If CDN loading fails, verify that all Three.js imports use the same version and CDN.

- [ ] **Step 4: Fix visual defects tests-first where practical**

If a defect is found:

1. Add or adjust a focused unit test when the defect is representable in generated HTML/config.
2. Implement the fix.
3. Regenerate `OUTPUT/house_3d.html`.
4. Re-run:

```bash
python3 -m unittest discover -s tests -v
```

- [ ] **Step 5: Final commit if fixes were required**

```bash
git add CODE/home_design/three_d_viewer.py tests/test_house_3d_viewer.py OUTPUT/house_3d.html
git commit -m "Polish house 3D viewer verification defects"
```

Skip this commit if browser verification required no changes.

## Final Verification Checklist

- [ ] `python3 -m unittest discover -s tests -v` passes.
- [ ] `python3 -m CODE.home_design.cli house-3d --output OUTPUT/house_3d.html` succeeds.
- [ ] Generated page opens through a local server.
- [ ] Scene is visibly nonblank.
- [ ] Keyboard/mouse navigation works.
- [ ] Existing unrelated modified files were not staged or reverted.
