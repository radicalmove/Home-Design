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
