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
PIXEL_TO_METRE = 0.81 / 22.0
REFERENCE_PIXEL_ORIGIN = {"x": 518.0, "y": 314.0}
GLAZING_TYPES = {"window", "window_group", "slider", "sliding_door"}


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
                "height": 0.08 if material != "painted_wall" else 2.7,
            }
        )
    return site


def build_house_3d_config(model: HouseModel) -> dict[str, Any]:
    rooms, warnings = _room_config(model)
    return {
        "title": "House 3D Viewer",
        "units": model.units,
        "orientation": model.raw.get("orientation", {}),
        "rooms": rooms,
        "features": _feature_config(model),
        "site": _site_config(model),
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
    let camera;
    let controls;
    let renderer;
    let scene;

    function showUnsupported(message) {
      status.textContent = message;
    }

    function createRenderer() {
      const nextRenderer = new THREE.WebGLRenderer({ antialias: true });
      nextRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      nextRenderer.setSize(window.innerWidth, window.innerHeight);
      nextRenderer.setClearColor(0xd8d4ca, 1);
      stage.appendChild(nextRenderer.domElement);
      return nextRenderer;
    }

    function createScene() {
      const nextScene = new THREE.Scene();
      nextScene.background = new THREE.Color(0xd8d4ca);
      nextScene.add(new THREE.HemisphereLight(0xffffff, 0x8f8a7d, 1.8));
      const sun = new THREE.DirectionalLight(0xffffff, 1.5);
      sun.position.set(-8, 12, 6);
      nextScene.add(sun);
      const grid = new THREE.GridHelper(60, 60, 0x9c9689, 0xc8c1b4);
      grid.position.y = -0.03;
      nextScene.add(grid);
      return nextScene;
    }

    function materialFor(id) {
      const item = config.materials[id] || config.materials.painted_wall || {};
      const options = {
        color: new THREE.Color(item.color || '#eeeeee'),
        roughness: item.roughness ?? 0.85,
        metalness: 0
      };
      if (item.opacity !== undefined) {
        options.transparent = true;
        options.opacity = item.opacity;
        options.depthWrite = false;
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
        scene.add(mesh);
      } else if (element.geometry.type === 'polygon') {
        scene.add(polygonMesh(element.geometry.points, material, height, `site:${element.id}`));
      } else if (element.geometry.type === 'multi_polygon') {
        element.geometry.polygons.forEach((polygon, index) => {
          scene.add(polygonMesh(polygon, material, height, `site:${element.id}:${index}`));
        });
      }
    }

    function featurePanel(feature) {
      const points = feature.geometry.type === 'multi_polygon'
        ? feature.geometry.polygons.flat()
        : feature.geometry.points || [];
      if (!points.length) return null;
      const bounds = boundsFromPoints(points);
      const width = Math.max(bounds.maxX - bounds.minX, 0.08);
      const depth = Math.max(bounds.maxZ - bounds.minZ, 0.08);
      const horizontal = width >= depth;
      const geo = horizontal
        ? new THREE.BoxGeometry(width, 1.55, 0.04)
        : new THREE.BoxGeometry(0.04, 1.55, depth);
      const mesh = new THREE.Mesh(geo, materialFor(feature.material));
      mesh.position.set((bounds.minX + bounds.maxX) / 2, 1.15, (bounds.minZ + bounds.maxZ) / 2);
      mesh.name = `feature:${feature.id}`;
      mesh.userData.featureId = feature.id;
      return mesh;
    }

    function resetCamera() {
      camera.position.set(7.2, 1.65, 4.4);
      camera.rotation.set(0, 0, 0);
      controls.getObject().lookAt(9.5, 1.45, 5.4);
    }

    function moveCamera(delta) {
      const speed = keysPressed.has('ShiftLeft') || keysPressed.has('ShiftRight') ? 5.2 : 2.7;
      const step = speed * delta;
      if (keysPressed.has('KeyW') || keysPressed.has('ArrowUp')) controls.moveForward(step);
      if (keysPressed.has('KeyS') || keysPressed.has('ArrowDown')) controls.moveForward(-step);
      if (keysPressed.has('KeyA') || keysPressed.has('ArrowLeft')) controls.moveRight(-step);
      if (keysPressed.has('KeyD') || keysPressed.has('ArrowRight')) controls.moveRight(step);
      if (keysPressed.has('KeyQ')) camera.position.y = Math.max(0.45, camera.position.y - step);
      if (keysPressed.has('KeyE')) camera.position.y = Math.min(4.2, camera.position.y + step);
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
      config.rooms.forEach((room) => {
        buildFloor(scene, room);
        buildRectRoomWalls(scene, room);
      });
      config.features.map(featurePanel).filter(Boolean).forEach((mesh) => scene.add(mesh));

      stage.addEventListener('click', () => controls.lock());
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

      status.textContent = `${config.title}: ${config.rooms.length} rooms, ${config.features.length} openings/features.`;
      animate();
    }

    startViewer();
"""
