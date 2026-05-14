# Home Design Baseline Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a structured current-state house model and deterministic 2D SVG renderer with geometry validation and daylight exposure data.

**Architecture:** Store all source-of-truth measurements in `DATA/house_model.json`. Use a small Python package under `CODE/home_design/` to load, validate, summarize, and render that model. Generate SVG outputs into `OUTPUT/`; generated files are review artifacts, not source data.

**Tech Stack:** Python 3 standard library, JSON, SVG output, `unittest` for tests. Avoid Matplotlib for the first implementation because it is not installed in the current environment.

---

## Scope

This plan implements the first baseline system only:

- Create a structured model file.
- Add model loading and validation.
- Add qualitative daylight matrix data by room.
- Render a clean SVG current-state floor plan.
- Render an optional daylight overlay by season and time band.

It does not implement an interactive browser app, 3D model, AI images, or physically exact solar simulation.

## File Structure

- Create: `DATA/house_model.json`
  - Source-of-truth model: site, assumptions, anchors, rooms, openings, reference layers, daylight, and initial approximate layout coordinates.

- Create: `CODE/home_design/__init__.py`
  - Package marker and version.

- Create: `CODE/home_design/model.py`
  - Dataclasses and JSON loading helpers.

- Create: `CODE/home_design/validate.py`
  - Validation checks for required fields, anchors, wall assumptions, daylight matrix shape, and room dimensions.

- Create: `CODE/home_design/render_svg.py`
  - Deterministic SVG renderer for baseline geometry and daylight overlays.

- Create: `CODE/home_design/cli.py`
  - Command-line entry point for validation and rendering.

- Create: `tests/test_house_model.py`
  - Unit tests for loading, model shape, daylight matrix completeness, and validation.

- Create: `tests/test_render_svg.py`
  - Unit tests for SVG output containing expected room labels, dimensions, and daylight overlay metadata.

- Generated: `OUTPUT/current_baseline.svg`
  - Baseline floor plan generated from `DATA/house_model.json`.

- Generated: `OUTPUT/daylight_<season>_<time_band>.svg`
  - Optional daylight overlay renders, for example `OUTPUT/daylight_winter_afternoon.svg`.

## Model Coordinate Convention

Use metres. For the initial model, use a local house coordinate system:

- `x`: increases from street/front side toward rear/back of property.
- `y`: increases from driveway/deck side toward the opposite long side.
- Rectangular rooms use `x`, `y`, `width`, and `depth`.
- Irregular spaces, especially the sunroom, use polygon points.

This local coordinate system is allowed to differ from final site placement. The renderer can later place the house model within the wider section.

## Task 1: Package Skeleton And CLI

**Files:**
- Create: `CODE/home_design/__init__.py`
- Create: `CODE/home_design/cli.py`
- Create: `tests/test_house_model.py`

- [ ] **Step 1: Write failing package import test**

```python
import unittest


class PackageImportTests(unittest.TestCase):
    def test_package_imports(self):
        import CODE.home_design as home_design

        self.assertTrue(hasattr(home_design, "__version__"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_house_model.PackageImportTests -v`

Expected: FAIL because `CODE/home_design` does not exist.

- [ ] **Step 3: Create package marker**

Create `CODE/home_design/__init__.py`:

```python
"""Tools for modelling and rendering the home design baseline."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Add minimal CLI shell**

Create `CODE/home_design/cli.py`:

```python
from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Home design model tools")
    parser.add_argument("command", choices=["validate", "render"])
    parser.add_argument("--model", default="DATA/house_model.json")
    parser.add_argument("--output", default="OUTPUT/current_baseline.svg")
    parser.add_argument("--season", default=None)
    parser.add_argument("--time-band", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m unittest tests.test_house_model.PackageImportTests -v`

Expected: PASS.

- [ ] **Step 6: Manual checkpoint**

If this workspace is converted into a git repo later, commit this checkpoint.

## Task 2: Source Model JSON

**Files:**
- Create: `DATA/house_model.json`
- Modify: `tests/test_house_model.py`

- [ ] **Step 1: Write failing model existence and shape tests**

Add tests:

```python
import json
from pathlib import Path


class HouseModelJsonTests(unittest.TestCase):
    def setUp(self):
        self.path = Path("DATA/house_model.json")

    def test_model_file_exists(self):
        self.assertTrue(self.path.exists())

    def test_model_has_required_sections(self):
        model = json.loads(self.path.read_text())
        for key in [
            "units",
            "orientation",
            "site",
            "assumptions",
            "anchors",
            "rooms",
            "openings",
            "reference_layers",
            "daylight",
        ]:
            self.assertIn(key, model)

    def test_known_external_anchors_are_recorded(self):
        model = json.loads(self.path.read_text())
        anchors = {item["id"]: item["value_m"] for item in model["anchors"]}
        self.assertAlmostEqual(anchors["long_side_master_to_laundry"], 16.1)
        self.assertAlmostEqual(anchors["combined_external_depth"], 11.58)
        self.assertAlmostEqual(anchors["master_street_frontage"], 4.77)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_house_model.HouseModelJsonTests -v`

Expected: FAIL because `DATA/house_model.json` does not exist.

- [ ] **Step 3: Create initial model JSON**

Create `DATA/house_model.json` with:

- `units`: `"metres"`
- `orientation`: road/street left, rear to right, deck/driveway side noted
- `site`: depth `53.75`, width `16.75`
- `assumptions`: exterior wall `0.30`, internal wall `0.14`, sunroom frame `0.10`
- `anchors`: all measured external anchors from the design spec
- `rooms`: all rooms from `CODE/House-Plan-Brief.md`
- `openings`: known sliders, large openings, and door/window notes
- `reference_layers`: satellite and outline image file paths
- `daylight`: season/time matrix for each room

Use the following room IDs:

```text
kitchen_dining
lounge
sunroom
hallway
office
bathroom
master_bedroom
bedroom_2
entrance
laundry
toilet
```

Each room should include:

```json
{
  "id": "lounge",
  "name": "Lounge",
  "dimensions_m": {
    "length": 4.9,
    "width": 3.7,
    "height": 2.4
  },
  "confidence": "measured",
  "notes": [],
  "layout": {
    "type": "rect",
    "x": 0.0,
    "y": 0.0,
    "width": 4.9,
    "depth": 3.7,
    "confidence": "inferred"
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_house_model.HouseModelJsonTests -v`

Expected: PASS.

- [ ] **Step 5: Manual checkpoint**

If this workspace is converted into a git repo later, commit this checkpoint.

## Task 3: Model Loader

**Files:**
- Create: `CODE/home_design/model.py`
- Modify: `tests/test_house_model.py`

- [ ] **Step 1: Write failing loader tests**

Add tests:

```python
from CODE.home_design.model import load_model


class ModelLoaderTests(unittest.TestCase):
    def test_load_model_returns_model_object(self):
        model = load_model("DATA/house_model.json")
        self.assertEqual(model.units, "metres")
        self.assertGreaterEqual(len(model.rooms), 10)

    def test_find_room_by_id(self):
        model = load_model("DATA/house_model.json")
        lounge = model.room("lounge")
        self.assertEqual(lounge.name, "Lounge")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_house_model.ModelLoaderTests -v`

Expected: FAIL because `CODE.home_design.model` does not exist.

- [ ] **Step 3: Implement dataclasses and loader**

Create `CODE/home_design/model.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Room:
    id: str
    name: str
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


def load_model(path: str | Path) -> HouseModel:
    raw = json.loads(Path(path).read_text())
    rooms = [
        Room(
            id=item["id"],
            name=item["name"],
            dimensions_m=item.get("dimensions_m", {}),
            confidence=item.get("confidence", "unknown"),
            notes=item.get("notes", []),
            layout=item.get("layout", {}),
        )
        for item in raw.get("rooms", [])
    ]
    return HouseModel(raw=raw, units=raw["units"], rooms=rooms)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_house_model.ModelLoaderTests -v`

Expected: PASS.

- [ ] **Step 5: Manual checkpoint**

If this workspace is converted into a git repo later, commit this checkpoint.

## Task 4: Model Validation

**Files:**
- Create: `CODE/home_design/validate.py`
- Modify: `CODE/home_design/cli.py`
- Modify: `tests/test_house_model.py`

- [ ] **Step 1: Write failing validation tests**

Add tests:

```python
from CODE.home_design.model import load_model
from CODE.home_design.validate import validate_model


class ModelValidationTests(unittest.TestCase):
    def test_current_model_validates(self):
        model = load_model("DATA/house_model.json")
        result = validate_model(model)
        self.assertEqual(result.errors, [])

    def test_daylight_matrix_complete(self):
        model = load_model("DATA/house_model.json")
        result = validate_model(model)
        self.assertNotIn("daylight", " ".join(result.errors).lower())
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_house_model.ModelValidationTests -v`

Expected: FAIL because validation module does not exist.

- [ ] **Step 3: Implement validation**

Create `CODE/home_design/validate.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from .model import HouseModel


SEASONS = ("summer", "autumn", "winter", "spring")
TIME_BANDS = ("morning", "midday", "afternoon")
LIGHT_LEVELS = ("low", "medium", "high", "unknown")


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_model(model: HouseModel) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    raw = model.raw

    if raw.get("units") != "metres":
        errors.append("units must be metres")

    assumptions = raw.get("assumptions", {})
    if assumptions.get("exterior_wall_thickness_m") != 0.30:
        warnings.append("exterior wall thickness differs from current 0.30m assumption")
    if assumptions.get("internal_wall_thickness_m") != 0.14:
        errors.append("internal wall thickness must be 0.14m")

    anchors = {item.get("id"): item for item in raw.get("anchors", [])}
    for anchor_id in [
        "long_side_master_to_laundry",
        "combined_external_depth",
        "master_street_frontage",
        "dining_edge_to_entrance_laundry_edge",
        "laundry_toilet_projection_wall",
    ]:
        if anchor_id not in anchors:
            errors.append(f"missing anchor: {anchor_id}")

    daylight = raw.get("daylight", {}).get("rooms", {})
    for room in model.rooms:
        matrix = daylight.get(room.id)
        if not matrix:
            errors.append(f"missing daylight matrix for {room.id}")
            continue
        for season in SEASONS:
            if season not in matrix:
                errors.append(f"missing {season} daylight for {room.id}")
                continue
            for band in TIME_BANDS:
                value = matrix[season].get(band)
                if value not in LIGHT_LEVELS:
                    errors.append(f"invalid daylight value for {room.id}.{season}.{band}: {value}")

    return ValidationResult(errors=errors, warnings=warnings)
```

- [ ] **Step 4: Wire validation into CLI**

Update `CODE/home_design/cli.py` so `validate` loads the model, prints errors/warnings, and returns `1` on errors.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_house_model.ModelValidationTests -v`

Expected: PASS.

- [ ] **Step 6: Run CLI validation**

Run: `python3 -m CODE.home_design.cli validate --model DATA/house_model.json`

Expected: exit code `0`, no validation errors.

- [ ] **Step 7: Manual checkpoint**

If this workspace is converted into a git repo later, commit this checkpoint.

## Task 5: Baseline SVG Renderer

**Files:**
- Create: `CODE/home_design/render_svg.py`
- Modify: `CODE/home_design/cli.py`
- Create: `tests/test_render_svg.py`

- [ ] **Step 1: Write failing SVG render tests**

Create `tests/test_render_svg.py`:

```python
import unittest

from CODE.home_design.model import load_model
from CODE.home_design.render_svg import render_baseline_svg


class SvgRenderTests(unittest.TestCase):
    def test_baseline_svg_contains_room_labels(self):
        model = load_model("DATA/house_model.json")
        svg = render_baseline_svg(model)
        self.assertIn("<svg", svg)
        self.assertIn("Lounge", svg)
        self.assertIn("Kitchen / Dining", svg)
        self.assertIn("Bedroom 2", svg)

    def test_baseline_svg_contains_anchor_notes(self):
        model = load_model("DATA/house_model.json")
        svg = render_baseline_svg(model)
        self.assertIn("16.1m", svg)
        self.assertIn("11.58m", svg)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_render_svg -v`

Expected: FAIL because renderer does not exist.

- [ ] **Step 3: Implement renderer**

Create `CODE/home_design/render_svg.py` with:

- Room fill colours by category.
- Stroke pattern by confidence.
- Scale helper from metres to pixels.
- Rect room rendering for rectangular layouts.
- Polygon rendering for sunroom.
- Text labels.
- Anchor/dimension notes.
- Optional daylight overlay if `season` and `time_band` are supplied.

Core function signatures:

```python
from __future__ import annotations

from html import escape
from pathlib import Path

from .model import HouseModel


def render_baseline_svg(
    model: HouseModel,
    *,
    season: str | None = None,
    time_band: str | None = None,
) -> str:
    ...


def write_svg(path: str | Path, svg: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)
```

- [ ] **Step 4: Wire rendering into CLI**

Update `CODE/home_design/cli.py` so `render`:

- loads the model
- validates it
- writes baseline SVG to `--output`
- accepts optional `--season` and `--time-band`

- [ ] **Step 5: Run render tests**

Run: `python3 -m unittest tests.test_render_svg -v`

Expected: PASS.

- [ ] **Step 6: Generate baseline SVG**

Run: `python3 -m CODE.home_design.cli render --model DATA/house_model.json --output OUTPUT/current_baseline.svg`

Expected: file exists at `OUTPUT/current_baseline.svg`.

- [ ] **Step 7: Manual checkpoint**

If this workspace is converted into a git repo later, commit this checkpoint.

## Task 6: Daylight Overlay Rendering

**Files:**
- Modify: `CODE/home_design/render_svg.py`
- Modify: `tests/test_render_svg.py`

- [ ] **Step 1: Write failing daylight overlay test**

Add test:

```python
class DaylightOverlayRenderTests(unittest.TestCase):
    def test_daylight_overlay_identifies_selected_period(self):
        model = load_model("DATA/house_model.json")
        svg = render_baseline_svg(model, season="winter", time_band="afternoon")
        self.assertIn("Daylight: winter afternoon", svg)
        self.assertIn("data-light-level", svg)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_render_svg.DaylightOverlayRenderTests -v`

Expected: FAIL until daylight overlay attributes and title are implemented.

- [ ] **Step 3: Implement daylight overlay styling**

In `render_svg.py`:

- Map `high` to warm yellow overlay.
- Map `medium` to pale amber overlay.
- Map `low` to cool grey/blue overlay.
- Map `unknown` to neutral hatch or light grey.
- Add `data-light-level="<level>"` to rendered room shapes when overlay is active.
- Add title text: `Daylight: <season> <time_band>`.
- Include room daylight notes in SVG `<title>` elements where available.

- [ ] **Step 4: Run daylight overlay test**

Run: `python3 -m unittest tests.test_render_svg.DaylightOverlayRenderTests -v`

Expected: PASS.

- [ ] **Step 5: Generate representative daylight SVGs**

Run:

```bash
python3 -m CODE.home_design.cli render --model DATA/house_model.json --output OUTPUT/daylight_summer_morning.svg --season summer --time-band morning
python3 -m CODE.home_design.cli render --model DATA/house_model.json --output OUTPUT/daylight_winter_afternoon.svg --season winter --time-band afternoon
```

Expected: both files exist in `OUTPUT/`.

- [ ] **Step 6: Manual checkpoint**

If this workspace is converted into a git repo later, commit this checkpoint.

## Task 7: End-To-End Verification

**Files:**
- Modify as needed based on failures.

- [ ] **Step 1: Run all tests**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 2: Validate model**

Run: `python3 -m CODE.home_design.cli validate --model DATA/house_model.json`

Expected: exit code `0`, no validation errors.

- [ ] **Step 3: Render baseline**

Run: `python3 -m CODE.home_design.cli render --model DATA/house_model.json --output OUTPUT/current_baseline.svg`

Expected: `OUTPUT/current_baseline.svg` exists and contains room labels and anchor notes.

- [ ] **Step 4: Render daylight overlay**

Run: `python3 -m CODE.home_design.cli render --model DATA/house_model.json --output OUTPUT/daylight_winter_afternoon.svg --season winter --time-band afternoon`

Expected: `OUTPUT/daylight_winter_afternoon.svg` exists and contains `Daylight: winter afternoon`.

- [ ] **Step 5: Inspect generated SVG files**

Open or view:

- `OUTPUT/current_baseline.svg`
- `OUTPUT/daylight_winter_afternoon.svg`

Check:

- All rooms appear.
- Labels fit reasonably.
- The model visibly distinguishes measured/inferred geometry.
- Anchor notes `16.1m`, `11.58m`, and `4.77m` are present.
- Daylight overlay is visible and labelled.

- [ ] **Step 6: Capture known limitations**

If visual inspection reveals obvious geometry inaccuracies, update `DATA/house_model.json` notes/confidence fields. Do not hand-edit generated SVG.

## Implementation Notes

- Use ASCII-only file content.
- Keep `DATA/house_model.json` readable and structured; this is more important than compactness.
- Do not delete or rewrite the existing Matplotlib scripts. They are historical references.
- Do not add external dependencies in the first pass unless absolutely necessary.
- Since this folder is currently not a git repository, commit steps are manual checkpoints only.
