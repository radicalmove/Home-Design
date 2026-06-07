# Reference Plan Sunlight Overlay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an interactive 2D sunlight mode to the Reference Style Plan HTML using Christchurch solar position, the model's recorded compass orientation, and known window/glazed-opening geometry.

**Architecture:** Create a focused Python helper that extracts sunlight config from `DATA/house_model.json`, then embed that config into `CODE/home_design/reference_plan_viewer.py`. The viewer owns the controls, JavaScript solar calculation, SVG overlay layer, and status text; the existing reference SVG renderer remains focused on drawing the base plan.

**Tech Stack:** Python standard library, `unittest`, generated HTML/SVG, vanilla JavaScript, existing `CODE.home_design` model/rendering modules.

---

## File Structure

- Create `CODE/home_design/sunlight.py`
  - Owns Christchurch metadata, year/time slider config, eligible light-entry opening IDs, simple model geometry extraction, and JSON-safe config creation.
  - Exposes `build_sunlight_config(model: HouseModel) -> dict[str, object]`.
  - Keeps browser-specific JavaScript out of Python.

- Modify `CODE/home_design/reference_plan_viewer.py`
  - Imports `json` and `build_sunlight_config`.
  - Injects a new SVG overlay group before `</svg>`.
  - Adds sunlight controls to the lower review panel.
  - Embeds config as `<script type="application/json" id="sunlight-config">...</script>`.
  - Adds CSS and JavaScript functions for sun position, plan-vector conversion, ray drawing, and no-direct-light state.

- Modify `tests/test_reference_viewer.py`
  - Adds tests for controls, embedded config, required opening IDs, required JavaScript functions, and below-horizon/no-direct-light branch.

- Regenerate `OUTPUT/reference_plan.html` after implementation.
  - Use the CLI command already documented in `README.md`.
  - Do not hand-edit generated output.

## Task 1: Sunlight Config Helper

**Files:**
- Create: `CODE/home_design/sunlight.py`
- Test: `tests/test_reference_viewer.py`

- [ ] **Step 1: Write the failing config test**

Add this test to `tests/test_reference_viewer.py`:

```python
import json
import re


class ReferencePlanSunlightTests(unittest.TestCase):
    def test_reference_plan_embeds_christchurch_sunlight_config(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        match = re.search(
            r'<script type="application/json" id="sunlight-config">(.*?)</script>',
            html,
            re.S,
        )

        self.assertIsNotNone(match)
        config = json.loads(match.group(1))
        self.assertEqual(config["location"]["name"], "Christchurch, New Zealand")
        self.assertAlmostEqual(config["location"]["latitude"], -43.53333)
        self.assertAlmostEqual(config["location"]["longitude"], 172.63333)
        self.assertAlmostEqual(config["orientation"]["plan_right_bearing_degrees"], 52.5)
        self.assertEqual(len(config["year_points"]), 16)
        self.assertEqual(config["time_slider"], {"start_minutes": 240, "end_minutes": 1320, "step_minutes": 30})
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_reference_viewer.ReferencePlanSunlightTests.test_reference_plan_embeds_christchurch_sunlight_config -v
```

Expected: FAIL because `sunlight-config` does not exist yet.

- [ ] **Step 3: Implement minimal config helper**

Create `CODE/home_design/sunlight.py`:

```python
from __future__ import annotations

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
    {"index": 11, "month": 2, "day": 29, "label": "Late Summer Feb"},
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


def build_sunlight_config(model: HouseModel) -> dict[str, Any]:
    compass = model.raw.get("orientation", {}).get("compass", {})
    return {
        "location": CHRISTCHURCH_LOCATION,
        "orientation": {
            "plan_right_bearing_degrees": float(compass.get("plan_right_bearing_degrees", 90.0)),
            "north_arrow_degrees_clockwise_from_plan_up": float(
                compass.get("north_arrow_degrees_clockwise_from_plan_up", 0.0)
            ),
            "confidence": str(compass.get("confidence", "unknown")),
        },
        "year_points": YEAR_POINTS,
        "time_slider": {"start_minutes": 240, "end_minutes": 1320, "step_minutes": 30},
        "light_entries": [],
        "rooms": [],
    }
```

Modify `CODE/home_design/reference_plan_viewer.py` just enough to embed this config:

```python
import json

from .sunlight import build_sunlight_config
```

and inside `render_reference_plan_html`:

```python
sunlight_config = json.dumps(build_sunlight_config(model), separators=(",", ":"))
```

then add before the main script:

```html
  <script type="application/json" id="sunlight-config">{sunlight_config}</script>
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_reference_viewer.ReferencePlanSunlightTests.test_reference_plan_embeds_christchurch_sunlight_config -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add CODE/home_design/sunlight.py CODE/home_design/reference_plan_viewer.py tests/test_reference_viewer.py
git commit -m "Add sunlight config for reference plan"
```

## Task 2: Light Entry Geometry Extraction

**Files:**
- Modify: `CODE/home_design/sunlight.py`
- Test: `tests/test_reference_viewer.py`

- [ ] **Step 1: Write the failing geometry test**

Add:

```python
    def test_sunlight_config_includes_required_light_entry_openings(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)
        config = json.loads(
            re.search(
                r'<script type="application/json" id="sunlight-config">(.*?)</script>',
                html,
                re.S,
            ).group(1)
        )

        entry_ids = {entry["id"] for entry in config["light_entries"]}

        for required_id in [
            "sunroom_wraparound_glazing",
            "deck_door_group",
            "entrance_deck_slider",
            "sunroom_lounge_slider",
            "bedroom2_entrance_internal_window",
            "bedroom2_se_window",
        ]:
            self.assertIn(required_id, entry_ids)

        deck_entry = next(entry for entry in config["light_entries"] if entry["id"] == "deck_door_group")
        self.assertEqual(deck_entry["type"], "door_group")
        self.assertEqual(deck_entry["centerlines"][0], {"x1": 826.0, "y1": 338.0, "x2": 826.0, "y2": 396.0})

    def test_sunlight_config_includes_room_geometry_for_future_clipping(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)
        config = json.loads(
            re.search(
                r'<script type="application/json" id="sunlight-config">(.*?)</script>',
                html,
                re.S,
            ).group(1)
        )

        room_ids = {room["id"] for room in config["rooms"]}

        self.assertIn("sunroom", room_ids)
        self.assertIn("kitchen_dining", room_ids)
        self.assertIn("bedroom_2", room_ids)
        sunroom = next(room for room in config["rooms"] if room["id"] == "sunroom")
        self.assertEqual(sunroom["geometry"]["type"], "polygon")
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_reference_viewer.ReferencePlanSunlightTests.test_sunlight_config_includes_required_light_entry_openings tests.test_reference_viewer.ReferencePlanSunlightTests.test_sunlight_config_includes_room_geometry_for_future_clipping -v
```

Expected: FAIL because `light_entries` and `rooms` are still empty.

- [ ] **Step 3: Implement geometry extraction**

In `CODE/home_design/sunlight.py`, add:

```python
def _light_entries(model: HouseModel) -> list[dict[str, Any]]:
    entries = []
    for feature in model.raw.get("current_structure", {}).get("features", []):
        feature_id = str(feature.get("id", ""))
        if feature_id not in LIGHT_ENTRY_FEATURE_IDS:
            continue
        centerlines = _geometry_centerlines(feature.get("display_px", {}))
        if not centerlines:
            continue
        entries.append(
            {
                "id": feature_id,
                "type": str(feature.get("type", "unknown")),
                "room": feature.get("room"),
                "between": feature.get("between"),
                "centerlines": [
                    {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                    for x1, y1, x2, y2 in centerlines
                ],
            }
        )
    return entries


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
            }
        )
    return rooms


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
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    if max_y - min_y >= max_x - min_x:
        x = (min_x + max_x) / 2
        return x, min_y, x, max_y
    y = (min_y + max_y) / 2
    return min_x, y, max_x, y
```

Then set:

```python
"light_entries": _light_entries(model),
"rooms": _rooms(model),
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_reference_viewer.ReferencePlanSunlightTests.test_sunlight_config_includes_required_light_entry_openings tests.test_reference_viewer.ReferencePlanSunlightTests.test_sunlight_config_includes_room_geometry_for_future_clipping -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add CODE/home_design/sunlight.py tests/test_reference_viewer.py
git commit -m "Extract sunlight entry openings"
```

## Task 3: Sunlight Controls And Overlay Markup

**Files:**
- Modify: `CODE/home_design/reference_plan_viewer.py`
- Test: `tests/test_reference_viewer.py`

- [ ] **Step 1: Write the failing controls test**

Add:

```python
    def test_reference_plan_html_exposes_sunlight_controls_and_overlay(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        self.assertIn('id="toggle-sunlight"', html)
        self.assertIn('id="sunlight-year-slider"', html)
        self.assertIn('id="sunlight-time-slider"', html)
        self.assertIn('id="sunlight-status"', html)
        self.assertIn('id="sunlight-overlay-layer"', html)
        self.assertIn('id="sunlight-dark-layer"', html)
        self.assertIn('id="sunlight-ray-layer"', html)
        self.assertIn('id="sunlight-direction-marker"', html)
        self.assertIn("Sunlight", html)
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_reference_viewer.ReferencePlanSunlightTests.test_reference_plan_html_exposes_sunlight_controls_and_overlay -v
```

Expected: FAIL because controls and overlay do not exist.

- [ ] **Step 3: Add minimal overlay SVG and controls**

In `render_reference_plan_html`, inject the overlay:

```python
svg = render_reference_plan_svg(model)
svg = svg.replace("</svg>", _render_sunlight_overlay_svg() + "\n</svg>", 1)
```

Add helper:

```python
def _render_sunlight_overlay_svg() -> str:
    return """
<g id="sunlight-overlay-layer" aria-hidden="true" style="display:none">
  <rect id="sunlight-dark-layer" x="0" y="0" width="1600" height="900" fill="#12100c" opacity="0.48"/>
  <g id="sunlight-ray-layer"></g>
  <g id="sunlight-direction-marker"></g>
</g>
""".strip()
```

Replace the review panel with a grid that keeps the existing title/build text and adds:

```html
      <div class="sunlight-panel" aria-label="Sunlight controls">
        <label class="sunlight-toggle"><input id="toggle-sunlight" type="checkbox"> Sunlight</label>
        <div class="sunlight-slider-row">
          <label for="sunlight-year-slider">Year</label>
          <input id="sunlight-year-slider" type="range" min="0" max="15" step="1" value="0" disabled>
          <span id="sunlight-year-label">Winter Jun</span>
        </div>
        <div class="sunlight-slider-row">
          <label for="sunlight-time-slider">Time</label>
          <input id="sunlight-time-slider" type="range" min="240" max="1320" step="30" value="720" disabled>
          <span id="sunlight-time-label">12:00</span>
        </div>
        <p id="sunlight-status">Sunlight mode off</p>
      </div>
```

Add CSS for `.review-panel` grid and `.sunlight-panel` with restrained controls and no nested cards.

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_reference_viewer.ReferencePlanSunlightTests.test_reference_plan_html_exposes_sunlight_controls_and_overlay -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add CODE/home_design/reference_plan_viewer.py tests/test_reference_viewer.py
git commit -m "Add sunlight controls to reference viewer"
```

## Task 4: Browser Sun Position And Overlay Update JavaScript

**Files:**
- Modify: `CODE/home_design/reference_plan_viewer.py`
- Test: `tests/test_reference_viewer.py`

- [ ] **Step 1: Write the failing JavaScript behaviour test**

Add:

```python
    def test_reference_plan_sunlight_script_updates_overlay_and_handles_darkness(self):
        model = load_model("DATA/house_model.json")
        html = render_reference_plan_html(model)

        self.assertIn("function solarPosition", html)
        self.assertIn("function azimuthToPlanVector", html)
        self.assertIn("function updateSunlightOverlay", html)
        self.assertIn("function renderSunlightRays", html)
        self.assertIn("No direct natural light", html)
        self.assertIn("position.elevation <= 0", html)
        self.assertIn("lightEntry.centerlines", html)
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_reference_viewer.ReferencePlanSunlightTests.test_reference_plan_sunlight_script_updates_overlay_and_handles_darkness -v
```

Expected: FAIL because these functions do not exist.

- [ ] **Step 3: Add minimal JavaScript implementation**

Append to the existing script in `reference_plan_viewer.py`:

```javascript
    const sunlightConfig = JSON.parse(document.getElementById('sunlight-config').textContent);
    const sunlightOverlay = document.getElementById('sunlight-overlay-layer');
    const sunlightDarkLayer = document.getElementById('sunlight-dark-layer');
    const sunlightRayLayer = document.getElementById('sunlight-ray-layer');
    const sunlightMarker = document.getElementById('sunlight-direction-marker');
    const sunlightToggle = document.getElementById('toggle-sunlight');
    const sunlightYearSlider = document.getElementById('sunlight-year-slider');
    const sunlightTimeSlider = document.getElementById('sunlight-time-slider');
    const sunlightYearLabel = document.getElementById('sunlight-year-label');
    const sunlightTimeLabel = document.getElementById('sunlight-time-label');
    const sunlightStatus = document.getElementById('sunlight-status');

    function solarPosition(date, latitude, longitude) {
      const rad = Math.PI / 180;
      const dayStart = Date.UTC(date.getUTCFullYear(), 0, 0);
      const dayOfYear = Math.floor((date.getTime() - dayStart) / 86400000);
      const minutes = date.getUTCHours() * 60 + date.getUTCMinutes();
      const gamma = 2 * Math.PI / 365 * (dayOfYear - 1 + (minutes - 720) / 1440);
      const equationOfTime = 229.18 * (
        0.000075 + 0.001868 * Math.cos(gamma) - 0.032077 * Math.sin(gamma)
        - 0.014615 * Math.cos(2 * gamma) - 0.040849 * Math.sin(2 * gamma)
      );
      const declination = (
        0.006918 - 0.399912 * Math.cos(gamma) + 0.070257 * Math.sin(gamma)
        - 0.006758 * Math.cos(2 * gamma) + 0.000907 * Math.sin(2 * gamma)
        - 0.002697 * Math.cos(3 * gamma) + 0.00148 * Math.sin(3 * gamma)
      );
      const trueSolarTime = (minutes + equationOfTime + 4 * longitude) % 1440;
      const hourAngle = (trueSolarTime / 4 < 0 ? trueSolarTime / 4 + 180 : trueSolarTime / 4 - 180) * rad;
      const latRad = latitude * rad;
      const cosZenith = Math.sin(latRad) * Math.sin(declination)
        + Math.cos(latRad) * Math.cos(declination) * Math.cos(hourAngle);
      const zenith = Math.acos(Math.min(1, Math.max(-1, cosZenith)));
      const elevation = 90 - zenith / rad;
      const azimuth = (Math.atan2(
        Math.sin(hourAngle),
        Math.cos(hourAngle) * Math.sin(latRad) - Math.tan(declination) * Math.cos(latRad)
      ) / rad + 180) % 360;
      return { azimuth, elevation };
    }

    function azimuthToPlanVector(azimuthDegrees, planRightBearingDegrees) {
      const planAngle = (azimuthDegrees - planRightBearingDegrees) * Math.PI / 180;
      return { x: Math.sin(planAngle), y: -Math.cos(planAngle) };
    }

    function selectedSunlightDate() {
      const yearPoint = sunlightConfig.year_points[Number(sunlightYearSlider.value)];
      const localYear = yearPoint.month < 6 ? 2027 : 2026;
      const minutes = Number(sunlightTimeSlider.value);
      return new Date(localYear, yearPoint.month - 1, yearPoint.day, Math.floor(minutes / 60), minutes % 60);
    }

    function formatMinutes(minutes) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
    }

    function updateSunlightOverlay() {
      const active = sunlightToggle.checked;
      sunlightOverlay.style.display = active ? 'block' : 'none';
      sunlightYearSlider.disabled = !active;
      sunlightTimeSlider.disabled = !active;
      if (!active) {
        sunlightStatus.textContent = 'Sunlight mode off';
        return;
      }
      const yearPoint = sunlightConfig.year_points[Number(sunlightYearSlider.value)];
      sunlightYearLabel.textContent = yearPoint.label;
      sunlightTimeLabel.textContent = formatMinutes(Number(sunlightTimeSlider.value));
      const date = selectedSunlightDate();
      const position = solarPosition(date, sunlightConfig.location.latitude, sunlightConfig.location.longitude);
      if (position.elevation <= 0) {
        sunlightDarkLayer.setAttribute('opacity', '0.68');
        sunlightRayLayer.replaceChildren();
        sunlightMarker.replaceChildren();
        sunlightStatus.textContent = 'No direct natural light';
        return;
      }
      sunlightDarkLayer.setAttribute('opacity', '0.42');
      const sunVector = azimuthToPlanVector(
        position.azimuth,
        sunlightConfig.orientation.plan_right_bearing_degrees
      );
      renderSunlightRays({ x: -sunVector.x, y: -sunVector.y }, position);
      sunlightStatus.textContent = `Az ${Math.round(position.azimuth)} deg / El ${Math.round(position.elevation)} deg`;
    }

    function renderSunlightRays(lightVector, position) {
      sunlightRayLayer.replaceChildren();
      sunlightMarker.replaceChildren();
      sunlightConfig.light_entries.forEach((lightEntry) => {
        lightEntry.centerlines.forEach((line) => {
          const midX = (line.x1 + line.x2) / 2;
          const midY = (line.y1 + line.y2) / 2;
          const length = Math.max(70, Math.min(280, position.elevation * 4));
          const spread = 16;
          const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
          polygon.setAttribute('class', 'sunlight-ray');
          polygon.setAttribute(
            'points',
            `${line.x1},${line.y1} ${line.x2},${line.y2} ${midX + lightVector.x * length + spread},${midY + lightVector.y * length + spread} ${midX + lightVector.x * length - spread},${midY + lightVector.y * length - spread}`
          );
          sunlightRayLayer.appendChild(polygon);
        });
      });
      const marker = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      marker.setAttribute('class', 'sunlight-direction-line');
      marker.setAttribute('x1', '1040');
      marker.setAttribute('y1', '590');
      marker.setAttribute('x2', String(1040 - lightVector.x * 45));
      marker.setAttribute('y2', String(590 - lightVector.y * 45));
      sunlightMarker.appendChild(marker);
    }
```

Add CSS:

```css
    .sunlight-ray { fill: rgba(255, 198, 76, 0.46); stroke: rgba(227, 156, 32, 0.35); stroke-width: 1; }
    .sunlight-direction-line { stroke: #d79222; stroke-width: 4; stroke-linecap: round; }
```

Wire events:

```javascript
    sunlightToggle.addEventListener('change', updateSunlightOverlay);
    sunlightYearSlider.addEventListener('input', updateSunlightOverlay);
    sunlightTimeSlider.addEventListener('input', updateSunlightOverlay);
    updateSunlightOverlay();
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_reference_viewer.ReferencePlanSunlightTests.test_reference_plan_sunlight_script_updates_overlay_and_handles_darkness -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add CODE/home_design/reference_plan_viewer.py tests/test_reference_viewer.py
git commit -m "Render interactive sunlight overlay"
```

## Task 5: Generate Output And Verify Full Suite

**Files:**
- Modify generated: `OUTPUT/reference_plan.html`
- Test: full test suite

- [ ] **Step 1: Run focused viewer tests**

Run:

```bash
python3 -m unittest tests.test_reference_viewer -v
```

Expected: all reference viewer tests pass.

- [ ] **Step 2: Run full suite**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests pass. If unrelated existing uncommitted changes cause failures, record the failures and isolate whether the sunlight changes are responsible.

- [ ] **Step 3: Regenerate Reference Style Plan HTML**

Run:

```bash
python3 -m CODE.home_design.cli reference-plan --output OUTPUT/reference_plan.html
```

Expected: `wrote OUTPUT/reference_plan.html`.

- [ ] **Step 4: Smoke-test generated HTML content**

Run:

```bash
rg -n "toggle-sunlight|sunlight-config|sunlight-overlay-layer|No direct natural light" OUTPUT/reference_plan.html
```

Expected: all four terms are found.

- [ ] **Step 5: Commit**

```bash
git add OUTPUT/reference_plan.html
git commit -m "Regenerate reference plan sunlight viewer"
```

## Task 6: Visual Browser Verification

**Files:**
- No source edits expected unless visual QA finds an issue.

- [ ] **Step 1: Start a local server**

Run:

```bash
python3 -m http.server 8765
```

Expected: server starts at `http://127.0.0.1:8765/`.

- [ ] **Step 2: Open Reference Style Plan**

Open:

```text
http://127.0.0.1:8765/OUTPUT/reference_plan.html
```

Expected: reference plan renders, existing zoom/pan controls still work, sunlight controls sit in the lower control area.

- [ ] **Step 3: Check sunlight active state**

Turn on Sunlight, set year to `Winter Jun`, set time to midday.

Expected:

- Sliders are enabled.
- Status shows azimuth/elevation.
- Plan darkens.
- Warm light polygons appear from eligible openings.
- Direction marker appears near the plan fringe.

- [ ] **Step 4: Check below-horizon state**

Set time to `4:00`.

Expected:

- Status says `No direct natural light`.
- Plan is darkened.
- No warm light polygons are visible.

- [ ] **Step 5: Stop the server**

Stop the `python3 -m http.server` process.

Expected: no long-running implementation server remains.

## Final Verification Checklist

- [ ] `python3 -m unittest tests.test_reference_viewer -v`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `python3 -m CODE.home_design.cli reference-plan --output OUTPUT/reference_plan.html`
- [ ] Browser smoke test confirms controls, active sunlight, and no-direct-natural-light state.
