# Furniture Layers V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Base View dimensions overlay plus a native, persistent 2D furniture editor with fixed/moveable layers, catalog objects, object editing, and live metre sizing.

**Architecture:** Keep the existing generated Base View for sunlight/zoom and add its read-only dimensions overlay inside the Python reference-plan renderer. Add typed Rust furniture contracts in `home-design-core`, storage/load/save functions in `home-design-desktop`, Tauri command bridges in `apps/desktop-ui/src-tauri`, and focused Svelte/TypeScript editor modules in `apps/desktop-ui/src`. Persist user furniture layouts as JSON in Tauri app data, while keeping `DATA/house_model.json` as the measured baseline model.

**Tech Stack:** Python `unittest` for generated reference-plan tests, Rust 2024 with `serde`/`serde_json` for contracts and persistence, Tauri 2 commands for desktop integration, Svelte 5/Vite/Vitest/TypeScript for the frontend editor, SVG for plan and furniture rendering.

---

## File Structure

Create or modify these files:

- Modify `CODE/home_design/reference_plan.py`: add dimension annotation data structures, dimension SVG rendering, and CSS.
- Modify `CODE/home_design/reference_plan_viewer.py`: add the `Dimensions` toolbar toggle and show/hide script.
- Modify `tests/test_reference_plan.py`: add SVG dimension-layer tests.
- Modify `tests/test_reference_viewer.py`: add Base View dimensions-toggle tests.
- Regenerate `OUTPUT/reference_plan.html`, `OUTPUT/reference_plan.svg`, and `apps/desktop-ui/public/views/reference_plan.html`.
- Create `apps/desktop-ui/public/views/reference_plan.svg`: static SVG background for the native editor.
- Create `crates/home-design-core/src/furniture.rs`: furniture layout contracts, catalog seed, current-house seed layout, and validation.
- Modify `crates/home-design-core/src/lib.rs`: export furniture contracts and add `ViewMode::FurnitureEditor`.
- Create `crates/home-design-core/tests/furniture_contracts.rs`: core furniture model/catalog/validation tests.
- Modify `crates/home-design-core/tests/project_manifest_contracts.rs`: require the new Furniture Editor view.
- Create `crates/home-design-desktop/src/furniture_storage.rs`: app-data layout persistence, seeded fallback, validation, and atomic writes.
- Modify `crates/home-design-desktop/src/lib.rs`: export storage functions.
- Modify `crates/home-design-desktop/src/commands.rs`: expose non-Tauri command functions for tests.
- Modify `crates/home-design-desktop/tests/desktop_contracts.rs`: add storage/load/save tests.
- Modify `apps/desktop-ui/src-tauri/src/main.rs`: bridge `load_furniture_layout`, `save_furniture_layout`, and `load_furniture_catalog` Tauri commands using app-data root.
- Modify `apps/desktop-ui/src/types.ts`: add furniture/layout/catalog TypeScript types and `ViewMode`.
- Modify `apps/desktop-ui/src/lib/homeDesignCommands.ts`: add frontend Tauri command wrappers.
- Modify `apps/desktop-ui/src/lib/homeDesignCommands.test.ts`: add wrapper tests.
- Create `apps/desktop-ui/src/lib/furnitureGeometry.ts`: metre/pixel conversion, object bounds, resize helpers.
- Create `apps/desktop-ui/src/lib/furnitureGeometry.test.ts`: geometry and dimension tests.
- Create `apps/desktop-ui/src/lib/furnitureState.ts`: pure object add/move/resize/rotate/recolour/duplicate/delete reducers.
- Create `apps/desktop-ui/src/lib/furnitureState.test.ts`: reducer tests.
- Create `apps/desktop-ui/src/lib/furnitureSymbols.ts`: Planner 5D-style symbol mapping metadata.
- Create `apps/desktop-ui/src/lib/furnitureSymbols.test.ts`: symbol mapping tests.
- Create `apps/desktop-ui/src/lib/furnitureStore.ts`: load/save state helpers around Tauri commands.
- Create `apps/desktop-ui/src/FurnitureEditorView.svelte`: native furniture editor view.
- Create `apps/desktop-ui/src/PlanCanvas.svelte`: locked SVG background plus furniture overlay.
- Create `apps/desktop-ui/src/FurnitureLayerControls.svelte`: fixed/moveable layer toggles.
- Create `apps/desktop-ui/src/FurnitureCatalogPanel.svelte`: grouped catalog.
- Create `apps/desktop-ui/src/FurnitureObjectInspector.svelte`: selected-object controls.
- Create `apps/desktop-ui/src/DimensionBadge.svelte`: temporary metre-size badge.
- Modify `apps/desktop-ui/src/App.svelte`: render native editor for `furniture_editor` mode and iframe for existing packaged views.

Do not refactor unrelated Python renderers, existing 3D navigation code, or model validation outside the required furniture/dimensions seams.

---

## Task 1: Base View Dimensions Overlay

**Files:**
- Modify: `tests/test_reference_plan.py`
- Modify: `tests/test_reference_viewer.py`
- Modify: `CODE/home_design/reference_plan.py`
- Modify: `CODE/home_design/reference_plan_viewer.py`
- Update generated: `OUTPUT/reference_plan.html`
- Update generated: `OUTPUT/reference_plan.svg`
- Update generated: `apps/desktop-ui/public/views/reference_plan.html`
- Create: `apps/desktop-ui/public/views/reference_plan.svg`

- [ ] **Step 1: Write failing SVG dimension-layer tests**

Add tests near the existing scale/orientation tests in `tests/test_reference_plan.py`:

```python
def test_reference_plan_includes_hidden_dimension_layer(self):
    svg = render_reference_plan_svg(model)

    self.assertIn('id="reference-dimension-layer"', svg)
    self.assertIn('style="display:none"', svg)
    self.assertLess(svg.index('id="reference-dimension-layer"'), svg.index('id="reference-label-layer"'))


def test_reference_plan_dimension_layer_contains_external_and_internal_metres(self):
    svg = render_reference_plan_svg(model)

    self.assertIn('data-ref-dimension-kind="external"', svg)
    self.assertIn('data-ref-dimension-kind="internal"', svg)
    self.assertIn('data-ref-dimension="overall-master-to-laundry"', svg)
    self.assertIn('data-ref-dimension="master-bedroom-clear-width"', svg)
    self.assertIn('>16.10 m<', svg)
    self.assertIn('>3.30 m<', svg)


def test_reference_plan_dimension_layer_marks_approximate_dimensions(self):
    svg = render_reference_plan_svg(model)

    self.assertIn('data-ref-dimension-confidence="measured"', svg)
    self.assertIn('data-ref-dimension-confidence="approximate"', svg)
    self.assertIn('class="ref-dimension-label approximate"', svg)
```

Add tests in `tests/test_reference_viewer.py`:

```python
def test_reference_plan_html_exposes_dimensions_toggle(self):
    html = render_reference_plan_html(model)

    self.assertIn('id="toggle-dimensions"', html)
    self.assertIn('Dimensions', html)
    self.assertIn("const dimensionsLayer = document.getElementById('reference-dimension-layer');", html)
    self.assertIn("dimensionsVisible = false", html)


def test_reference_plan_dimensions_toggle_is_independent_from_sunlight(self):
    html = render_reference_plan_html(model)

    self.assertIn('id="toggle-sunlight"', html)
    self.assertIn('id="toggle-dimensions"', html)
    self.assertIn('function setDimensionsVisible', html)
    self.assertNotIn('toggleDimensions.disabled = sunlightActive', html)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest tests.test_reference_plan tests.test_reference_viewer -v
```

Expected: failures for missing `reference-dimension-layer` and `toggle-dimensions`.

- [ ] **Step 3: Add dimension annotations and renderer**

In `CODE/home_design/reference_plan.py`, add a small immutable annotation list near the other curated constants:

```python
DIMENSION_ANNOTATIONS = [
    {
        "id": "overall-master-to-laundry",
        "kind": "external",
        "label": "16.10 m",
        "metres": 16.10,
        "x1": 533.9,
        "y1": 617.8,
        "x2": 960.4,
        "y2": 617.8,
        "offset_x": 0.0,
        "offset_y": 26.0,
        "confidence": "measured",
        "source": "anchor:long_side_master_to_laundry",
    },
    {
        "id": "overall-external-depth",
        "kind": "external",
        "label": "11.58 m",
        "metres": 11.58,
        "x1": 984.4,
        "y1": 302.3,
        "x2": 984.4,
        "y2": 602.2,
        "offset_x": 28.0,
        "offset_y": 0.0,
        "confidence": "measured",
        "source": "anchor:combined_external_depth",
    },
    {
        "id": "kitchen-dining-clear-length",
        "kind": "internal",
        "label": "8.12 m",
        "metres": 8.12,
        "x1": 758.8,
        "y1": 331.0,
        "x2": 833.0,
        "y2": 331.0,
        "offset_x": 0.0,
        "offset_y": -18.0,
        "confidence": "measured",
        "source": "room:kitchen_dining.length",
    },
    {
        "id": "lounge-clear-depth",
        "kind": "internal",
        "label": "4.90 m",
        "metres": 4.90,
        "x1": 679.0,
        "y1": 348.8,
        "x2": 679.0,
        "y2": 484.6,
        "offset_x": -18.0,
        "offset_y": 0.0,
        "confidence": "measured",
        "source": "room:lounge.depth",
    },
    {
        "id": "master-bedroom-clear-width",
        "kind": "internal",
        "label": "3.30 m",
        "metres": 3.30,
        "x1": 533.9,
        "y1": 541.0,
        "x2": 627.1,
        "y2": 541.0,
        "offset_x": 0.0,
        "offset_y": -16.0,
        "confidence": "measured",
        "source": "room:master_bedroom.width",
    },
    {
        "id": "wardrobe-bay-depth",
        "kind": "built_in",
        "label": "0.62 m",
        "metres": 0.62,
        "x1": 627.1,
        "y1": 609.5,
        "x2": 646.8,
        "y2": 609.5,
        "offset_x": 0.0,
        "offset_y": 16.0,
        "confidence": "measured",
        "source": "built_in:master_bedroom_wardrobe",
    },
    {
        "id": "bedroom-2-clear-length",
        "kind": "internal",
        "label": "4.73 m",
        "metres": 4.73,
        "x1": 773.9,
        "y1": 546.0,
        "x2": 902.8,
        "y2": 546.0,
        "offset_x": 0.0,
        "offset_y": -16.0,
        "confidence": "measured",
        "source": "room:bedroom_2.length",
    },
    {
        "id": "sunroom-approx-span",
        "kind": "external",
        "label": "~4.87 m",
        "metres": 4.87,
        "x1": 533.9,
        "y1": 326.0,
        "x2": 663.1,
        "y2": 326.0,
        "offset_x": 0.0,
        "offset_y": -18.0,
        "confidence": "approximate",
        "source": "room:sunroom.reference_position",
    },
]
```

Add CSS in `_reference_css()`:

```python
.ref-dimension-line, .ref-dimension-extension, .ref-dimension-tick { stroke: #263238; stroke-width: 0.85; stroke-linecap: butt; fill: none; }
.ref-dimension-extension { opacity: 0.58; }
.ref-dimension-label { font-size: 7px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; fill: #263238; paint-order: stroke; stroke: #f6f4ef; stroke-width: 3px; }
.ref-dimension-label.approximate { fill: #7a5a1f; }
.ref-dimension-group.approximate .ref-dimension-line, .ref-dimension-group.approximate .ref-dimension-tick { stroke-dasharray: 3 2; stroke: #7a5a1f; }
```

Add `_render_dimension_layer()` and helper functions:

```python
def _render_dimension_layer() -> str:
    parts = ['<g id="reference-dimension-layer" style="display:none" aria-hidden="true">']
    for annotation in DIMENSION_ANNOTATIONS:
        parts.append(_render_dimension_annotation(annotation))
    parts.append("</g>")
    return "\n".join(parts)


def _render_dimension_annotation(annotation: dict[str, Any]) -> str:
    dimension_id = escape(str(annotation["id"]))
    kind = escape(str(annotation["kind"]))
    confidence = escape(str(annotation["confidence"]))
    label = escape(str(annotation["label"]))
    source = escape(str(annotation["source"]))
    x1 = float(annotation["x1"])
    y1 = float(annotation["y1"])
    x2 = float(annotation["x2"])
    y2 = float(annotation["y2"])
    offset_x = float(annotation["offset_x"])
    offset_y = float(annotation["offset_y"])
    line_x1 = x1 + offset_x
    line_y1 = y1 + offset_y
    line_x2 = x2 + offset_x
    line_y2 = y2 + offset_y
    label_x = (line_x1 + line_x2) / 2
    label_y = (line_y1 + line_y2) / 2
    tick = 4.5
    if abs(line_x2 - line_x1) >= abs(line_y2 - line_y1):
        tick_one = (line_x1, line_y1 - tick, line_x1, line_y1 + tick)
        tick_two = (line_x2, line_y2 - tick, line_x2, line_y2 + tick)
    else:
        tick_one = (line_x1 - tick, line_y1, line_x1 + tick, line_y1)
        tick_two = (line_x2 - tick, line_y2, line_x2 + tick, line_y2)
    return "\n".join(
        [
            f'<g class="ref-dimension-group {confidence}" data-ref-dimension="{dimension_id}" data-ref-dimension-kind="{kind}" data-ref-dimension-confidence="{confidence}" data-ref-dimension-source="{source}">',
            f'<line class="ref-dimension-extension" x1="{x1:.1f}" y1="{y1:.1f}" x2="{line_x1:.1f}" y2="{line_y1:.1f}"/>',
            f'<line class="ref-dimension-extension" x1="{x2:.1f}" y1="{y2:.1f}" x2="{line_x2:.1f}" y2="{line_y2:.1f}"/>',
            f'<line class="ref-dimension-line" x1="{line_x1:.1f}" y1="{line_y1:.1f}" x2="{line_x2:.1f}" y2="{line_y2:.1f}"/>',
            f'<line class="ref-dimension-tick" x1="{tick_one[0]:.1f}" y1="{tick_one[1]:.1f}" x2="{tick_one[2]:.1f}" y2="{tick_one[3]:.1f}"/>',
            f'<line class="ref-dimension-tick" x1="{tick_two[0]:.1f}" y1="{tick_two[1]:.1f}" x2="{tick_two[2]:.1f}" y2="{tick_two[3]:.1f}"/>',
            f'<text class="ref-dimension-label {confidence}" x="{label_x:.1f}" y="{label_y:.1f}">{label}</text>',
            "</g>",
        ]
    )
```

Insert `_render_dimension_layer()` after `_render_orientation_layer(...)` and before `_render_label_layer(...)` in `render_reference_plan_svg`.

- [ ] **Step 4: Add dimensions toggle to Base View HTML**

In `CODE/home_design/reference_plan_viewer.py`, add the toolbar button after `Fit house`:

```html
<button id="toggle-dimensions" type="button" aria-pressed="false">Dimensions</button>
```

Add script state near existing constants:

```javascript
const toggleDimensions = document.getElementById('toggle-dimensions');
const dimensionsLayer = document.getElementById('reference-dimension-layer');
let dimensionsVisible = false;

function setDimensionsVisible(visible) {
  dimensionsVisible = visible;
  if (dimensionsLayer) {
    dimensionsLayer.style.display = visible ? '' : 'none';
    dimensionsLayer.setAttribute('aria-hidden', visible ? 'false' : 'true');
  }
  toggleDimensions?.setAttribute('aria-pressed', visible ? 'true' : 'false');
}

toggleDimensions?.addEventListener('click', () => {
  setDimensionsVisible(!dimensionsVisible);
});

setDimensionsVisible(false);
```

- [ ] **Step 5: Run the targeted tests**

Run:

```bash
python3 -m unittest tests.test_reference_plan tests.test_reference_viewer -v
```

Expected: PASS.

- [ ] **Step 6: Regenerate reference assets**

Run:

```bash
python3 -m CODE.home_design.cli reference-plan --output OUTPUT/reference_plan.html
python3 -m CODE.home_design.cli reference-plan --output OUTPUT/reference_plan.svg
cp OUTPUT/reference_plan.html apps/desktop-ui/public/views/reference_plan.html
cp OUTPUT/reference_plan.svg apps/desktop-ui/public/views/reference_plan.svg
```

Expected: regenerated files exist and include `reference-dimension-layer`.

- [ ] **Step 7: Commit**

Run:

```bash
git add CODE/home_design/reference_plan.py CODE/home_design/reference_plan_viewer.py tests/test_reference_plan.py tests/test_reference_viewer.py OUTPUT/reference_plan.html OUTPUT/reference_plan.svg apps/desktop-ui/public/views/reference_plan.html apps/desktop-ui/public/views/reference_plan.svg
git commit -m "feat: add base view dimensions overlay"
```

---

## Task 2: Rust Furniture Contracts And Project Manifest

**Files:**
- Create: `crates/home-design-core/src/furniture.rs`
- Modify: `crates/home-design-core/src/lib.rs`
- Create: `crates/home-design-core/tests/furniture_contracts.rs`
- Modify: `crates/home-design-core/tests/project_manifest_contracts.rs`

- [ ] **Step 1: Write failing core contract tests**

Create `crates/home-design-core/tests/furniture_contracts.rs`:

```rust
use home_design_core::{
    default_furniture_catalog, seed_current_furniture_layout, validate_furniture_layout,
    FurnitureLayerKind,
};
use std::collections::BTreeSet;

#[test]
fn default_catalog_groups_current_house_first_objects() {
    let catalog = default_furniture_catalog();

    let group_names: BTreeSet<_> = catalog.groups.iter().map(|group| group.name.as_str()).collect();
    assert!(group_names.contains("Kitchen and built-ins"));
    assert!(group_names.contains("Bathroom and laundry"));
    assert!(group_names.contains("Lounge and dining"));
    assert!(group_names.contains("Bedroom and office"));
    assert!(group_names.contains("Custom objects"));

    let item_ids: BTreeSet<_> = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter().map(|item| item.id.as_str()))
        .collect();
    assert!(item_ids.contains("base_cabinet"));
    assert!(item_ids.contains("refrigerator"));
    assert!(item_ids.contains("sofa"));
    assert!(item_ids.contains("queen_bed"));
    assert!(item_ids.contains("custom_rectangle"));
}

#[test]
fn seed_layout_contains_fixed_and_moveable_current_house_objects() {
    let layout = seed_current_furniture_layout();

    assert_eq!(layout.project_id, "current-house");
    assert_eq!(layout.scenario_id, "current");
    assert_eq!(layout.plan_transform.units, "metres");
    assert!(layout.objects.iter().any(|object| object.layer == FurnitureLayerKind::Fixed));
    assert!(layout.objects.iter().any(|object| object.layer == FurnitureLayerKind::Moveable));
    assert!(layout.objects.iter().any(|object| object.id == "master_bedroom_wardrobe"));
    assert!(layout.objects.iter().any(|object| object.id == "lounge_sofa"));
    assert!(layout.objects.iter().any(|object| object.id == "office_desk"));
}

#[test]
fn furniture_layout_validation_rejects_duplicate_ids_and_invalid_dimensions() {
    let mut layout = seed_current_furniture_layout();
    let duplicate = layout.objects[0].clone();
    layout.objects.push(duplicate);
    layout.objects[0].width_m = 0.0;
    layout.objects[1].colour = "not-a-colour".to_string();

    let result = validate_furniture_layout(&layout);

    assert!(!result.ok());
    assert!(result.errors.iter().any(|error| error.contains("duplicate furniture object id")));
    assert!(result.errors.iter().any(|error| error.contains("width_m must be positive")));
    assert!(result.errors.iter().any(|error| error.contains("colour must be a hex colour")));
}

#[test]
fn furniture_layout_round_trips_json_in_metres() {
    let layout = seed_current_furniture_layout();

    let json = serde_json::to_string_pretty(&layout).expect("serialize layout");
    let parsed: home_design_core::FurnitureLayout =
        serde_json::from_str(&json).expect("deserialize layout");

    assert_eq!(parsed, layout);
    assert!(json.contains("\"width_m\""));
    assert!(json.contains("\"depth_m\""));
}
```

Update `crates/home-design-core/tests/project_manifest_contracts.rs` to expect three views and `ViewMode::FurnitureEditor`:

```rust
assert_eq!(manifest.views.len(), 3);
let furniture_view = manifest
    .views
    .iter()
    .find(|view| view.id == "furniture-editor")
    .expect("furniture editor view");
assert_eq!(furniture_view.label, "Furniture Editor");
assert_eq!(furniture_view.mode, ViewMode::FurnitureEditor);
assert_eq!(furniture_view.asset_path, "/views/reference_plan.svg");
assert!(furniture_view.available);
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cargo test -p home-design-core --test furniture_contracts
cargo test -p home-design-core --test project_manifest_contracts built_in_project_manifest_exposes_current_house_views
```

Expected: compile/test failures for missing furniture module and manifest mode.

- [ ] **Step 3: Implement furniture contracts**

Create `crates/home-design-core/src/furniture.rs`:

```rust
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FurnitureLayerKind {
    Fixed,
    Moveable,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PlanPoint {
    pub x: f64,
    pub y: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PlanTransform {
    pub units: String,
    pub svg_width_px: f64,
    pub svg_height_px: f64,
    pub origin_svg_px: PlanPoint,
    pub px_per_m: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureObject {
    pub id: String,
    pub catalog_id: Option<String>,
    pub layer: FurnitureLayerKind,
    #[serde(rename = "type")]
    pub object_type: String,
    pub label: String,
    pub abbreviation: Option<String>,
    pub x_m: f64,
    pub y_m: f64,
    pub width_m: f64,
    pub depth_m: f64,
    pub rotation_deg: f64,
    pub colour: String,
    pub locked: bool,
    pub notes: Option<String>,
    pub evidence: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureLayout {
    pub project_id: String,
    pub scenario_id: String,
    pub plan_transform: PlanTransform,
    pub objects: Vec<FurnitureObject>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureCatalog {
    pub groups: Vec<FurnitureCatalogGroup>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureCatalogGroup {
    pub id: String,
    pub name: String,
    pub items: Vec<FurnitureCatalogItem>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureCatalogItem {
    pub id: String,
    pub label: String,
    pub layer: FurnitureLayerKind,
    #[serde(rename = "type")]
    pub object_type: String,
    pub abbreviation: Option<String>,
    pub default_width_m: f64,
    pub default_depth_m: f64,
    pub colour: String,
    pub symbol: String,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct FurnitureValidationResult {
    pub errors: Vec<String>,
}

impl FurnitureValidationResult {
    pub fn ok(&self) -> bool {
        self.errors.is_empty()
    }
}

pub fn default_plan_transform() -> PlanTransform {
    PlanTransform {
        units: "metres".to_string(),
        svg_width_px: 1600.0,
        svg_height_px: 900.0,
        origin_svg_px: PlanPoint { x: 518.0, y: 314.0 },
        px_per_m: 22.0 / 0.81,
    }
}
```

Then add `default_furniture_catalog()`, `seed_current_furniture_layout()`, and `validate_furniture_layout(...)`. Seed layout should include at least:

- fixed: `master_bedroom_wardrobe`, `kitchen_base_cabinets`, `kitchen_refrigerator`, `laundry_washer`, `bathroom_vanity`, `bathroom_toilet`, `bathroom_shower`
- moveable: `lounge_sofa`, `dining_table`, `bedroom2_bed`, `office_desk`, `bookcase`

Use approximate metre coordinates now, derived from existing scenario editor placements through the plan transform. Keep notes honest, e.g. `"Approximate seed from current photo/model context."`.

Validation must check:

- project/scenario ids are non-empty.
- transform units are `metres`.
- each id is unique and non-empty.
- all numeric fields are finite.
- `width_m` and `depth_m` are greater than `0.05`.
- `colour` matches `#[0-9a-fA-F]{6}` without using regex; implement a small helper.

- [ ] **Step 4: Export contracts and add manifest view**

In `crates/home-design-core/src/lib.rs`:

```rust
mod furniture;
pub use furniture::{
    default_furniture_catalog, default_plan_transform, seed_current_furniture_layout,
    validate_furniture_layout, FurnitureCatalog, FurnitureCatalogGroup, FurnitureCatalogItem,
    FurnitureLayerKind, FurnitureLayout, FurnitureObject, FurnitureValidationResult, PlanPoint,
    PlanTransform,
};
```

Extend `ViewMode`:

```rust
FurnitureEditor,
```

Add the third view to `built_in_project_manifest()`:

```rust
ViewDescriptor {
    id: "furniture-editor".to_string(),
    label: "Furniture Editor".to_string(),
    mode: ViewMode::FurnitureEditor,
    asset_path: "/views/reference_plan.svg".to_string(),
    available: true,
},
```

- [ ] **Step 5: Run core tests**

Run:

```bash
cargo test -p home-design-core
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add crates/home-design-core/src/lib.rs crates/home-design-core/src/furniture.rs crates/home-design-core/tests/furniture_contracts.rs crates/home-design-core/tests/project_manifest_contracts.rs
git commit -m "feat: add furniture layout contracts"
```

---

## Task 3: Desktop Furniture Persistence Commands

**Files:**
- Create: `crates/home-design-desktop/src/furniture_storage.rs`
- Modify: `crates/home-design-desktop/src/lib.rs`
- Modify: `crates/home-design-desktop/src/commands.rs`
- Modify: `crates/home-design-desktop/tests/desktop_contracts.rs`

- [ ] **Step 1: Write failing desktop storage tests**

Add to `crates/home-design-desktop/tests/desktop_contracts.rs`:

```rust
use home_design_desktop::{
    load_furniture_catalog, load_furniture_layout_from_root, save_furniture_layout_to_root,
};
use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

fn isolated_storage_root(test_name: &str) -> PathBuf {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("time")
        .as_nanos();
    std::env::temp_dir().join(format!("home-design-{test_name}-{nonce}"))
}

#[test]
fn load_furniture_layout_returns_seed_when_no_saved_file_exists() {
    let root = isolated_storage_root("seed");

    let loaded = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect("load seeded layout");

    assert_eq!(loaded.source, "seed");
    assert_eq!(loaded.layout.project_id, "current-house");
    assert!(loaded.layout.objects.iter().any(|object| object.id == "lounge_sofa"));
}

#[test]
fn save_and_load_furniture_layout_persists_json() {
    let root = isolated_storage_root("save");
    let mut loaded = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect("load seeded layout");
    loaded.layout.objects[0].x_m += 0.5;

    save_furniture_layout_to_root(&root, &loaded.layout).expect("save layout");
    let reloaded = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect("load saved layout");

    assert_eq!(reloaded.source, "saved");
    assert_eq!(reloaded.layout.objects[0].x_m, loaded.layout.objects[0].x_m);
}

#[test]
fn invalid_saved_furniture_json_is_reported_without_overwriting() {
    let root = isolated_storage_root("invalid-json");
    let path = root.join("projects/current-house/scenarios/current/furniture-layout.json");
    fs::create_dir_all(path.parent().expect("parent")).expect("create parent");
    fs::write(&path, "{not json").expect("write invalid json");

    let error = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect_err("invalid json should fail");

    assert!(error.contains("could not parse furniture layout"));
    assert_eq!(fs::read_to_string(path).expect("read invalid file"), "{not json");
}

#[test]
fn load_furniture_catalog_returns_default_catalog() {
    let catalog = load_furniture_catalog();

    assert!(catalog.groups.iter().any(|group| group.name == "Kitchen and built-ins"));
}
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cargo test -p home-design-desktop --test desktop_contracts furniture
```

Expected: compile failures for missing functions/types.

- [ ] **Step 3: Implement storage module**

Create `crates/home-design-desktop/src/furniture_storage.rs`:

```rust
use home_design_core::{
    default_furniture_catalog, seed_current_furniture_layout, validate_furniture_layout,
    FurnitureCatalog, FurnitureLayout,
};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureLayoutLoadResult {
    pub source: String,
    pub layout: FurnitureLayout,
}

pub fn load_furniture_catalog() -> FurnitureCatalog {
    default_furniture_catalog()
}

pub fn furniture_layout_path(root: &Path, project_id: &str, scenario_id: &str) -> PathBuf {
    root.join("projects")
        .join(project_id)
        .join("scenarios")
        .join(scenario_id)
        .join("furniture-layout.json")
}

pub fn load_furniture_layout_from_root(
    root: &Path,
    project_id: &str,
    scenario_id: &str,
) -> Result<FurnitureLayoutLoadResult, String> {
    let path = furniture_layout_path(root, project_id, scenario_id);
    if !path.exists() {
        let mut layout = seed_current_furniture_layout();
        layout.project_id = project_id.to_string();
        layout.scenario_id = scenario_id.to_string();
        return Ok(FurnitureLayoutLoadResult {
            source: "seed".to_string(),
            layout,
        });
    }

    let raw = fs::read_to_string(&path)
        .map_err(|error| format!("could not read furniture layout: {error}"))?;
    let layout: FurnitureLayout = serde_json::from_str(&raw)
        .map_err(|error| format!("could not parse furniture layout: {error}"))?;
    let validation = validate_furniture_layout(&layout);
    if !validation.ok() {
        return Err(format!(
            "invalid furniture layout: {}",
            validation.errors.join("; ")
        ));
    }
    Ok(FurnitureLayoutLoadResult {
        source: "saved".to_string(),
        layout,
    })
}

pub fn save_furniture_layout_to_root(root: &Path, layout: &FurnitureLayout) -> Result<(), String> {
    let validation = validate_furniture_layout(layout);
    if !validation.ok() {
        return Err(format!(
            "invalid furniture layout: {}",
            validation.errors.join("; ")
        ));
    }
    let path = furniture_layout_path(root, &layout.project_id, &layout.scenario_id);
    let parent = path.parent().ok_or_else(|| "invalid furniture layout path".to_string())?;
    fs::create_dir_all(parent)
        .map_err(|error| format!("could not create furniture layout directory: {error}"))?;
    let temporary_path = path.with_extension("json.tmp");
    let json = serde_json::to_string_pretty(layout)
        .map_err(|error| format!("could not serialize furniture layout: {error}"))?;
    fs::write(&temporary_path, json)
        .map_err(|error| format!("could not write furniture layout: {error}"))?;
    fs::rename(&temporary_path, &path)
        .map_err(|error| format!("could not replace furniture layout: {error}"))?;
    Ok(())
}
```

- [ ] **Step 4: Export desktop storage functions**

In `crates/home-design-desktop/src/lib.rs`, export from `commands` or the new module according to existing style:

```rust
mod commands;
mod furniture_storage;

pub use commands::{get_app_status, load_builtin_model_status, load_builtin_project, BuiltInModelStatus};
pub use furniture_storage::{
    furniture_layout_path, load_furniture_catalog, load_furniture_layout_from_root,
    save_furniture_layout_to_root, FurnitureLayoutLoadResult,
};
```

If `lib.rs` already has exports, preserve existing exports and add the new ones.

- [ ] **Step 5: Run desktop tests**

Run:

```bash
cargo test -p home-design-desktop
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add crates/home-design-desktop/src/lib.rs crates/home-design-desktop/src/furniture_storage.rs crates/home-design-desktop/src/commands.rs crates/home-design-desktop/tests/desktop_contracts.rs
git commit -m "feat: persist furniture layouts"
```

---

## Task 4: Tauri Command Bridge And TypeScript Command Wrappers

**Files:**
- Modify: `apps/desktop-ui/src-tauri/src/main.rs`
- Modify: `apps/desktop-ui/src/types.ts`
- Modify: `apps/desktop-ui/src/lib/homeDesignCommands.ts`
- Modify: `apps/desktop-ui/src/lib/homeDesignCommands.test.ts`
- Modify: `apps/desktop-ui/src/lib/assetAvailability.test.ts`
- Modify: `apps/desktop-ui/src/lib/viewState.test.ts`

- [ ] **Step 1: Write failing frontend command tests**

In `apps/desktop-ui/src/lib/homeDesignCommands.test.ts`, add:

```ts
it("loads the furniture catalog from the Rust command", async () => {
  invokeMock.mockResolvedValueOnce({ groups: [] });

  const catalog = await loadFurnitureCatalog();

  expect(invokeMock).toHaveBeenCalledWith("load_furniture_catalog");
  expect(catalog.groups).toEqual([]);
});

it("loads a furniture layout for the current scenario", async () => {
  invokeMock.mockResolvedValueOnce({
    source: "seed",
    layout: {
      project_id: "current-house",
      scenario_id: "current",
      plan_transform: {
        units: "metres",
        svg_width_px: 1600,
        svg_height_px: 900,
        origin_svg_px: { x: 518, y: 314 },
        px_per_m: 27.16,
      },
      objects: [],
    },
  });

  const result = await loadFurnitureLayout("current-house", "current");

  expect(invokeMock).toHaveBeenCalledWith("load_furniture_layout", {
    projectId: "current-house",
    scenarioId: "current",
  });
  expect(result.source).toBe("seed");
});

it("saves a furniture layout through the Rust command", async () => {
  const layout = {
    project_id: "current-house",
    scenario_id: "current",
    plan_transform: {
      units: "metres",
      svg_width_px: 1600,
      svg_height_px: 900,
      origin_svg_px: { x: 518, y: 314 },
      px_per_m: 27.16,
    },
    objects: [],
  };
  invokeMock.mockResolvedValueOnce(undefined);

  await saveFurnitureLayout(layout);

  expect(invokeMock).toHaveBeenCalledWith("save_furniture_layout", { layout });
});
```

Update imports in that file to include `loadFurnitureCatalog`, `loadFurnitureLayout`, and `saveFurnitureLayout`.

Update `apps/desktop-ui/src/lib/viewState.test.ts` and `apps/desktop-ui/src/lib/assetAvailability.test.ts` fixtures to include the furniture editor view and `/views/reference_plan.svg`.

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
npm run test --prefix apps/desktop-ui -- homeDesignCommands viewState assetAvailability
```

Expected: missing TypeScript functions/types.

- [ ] **Step 3: Add TypeScript furniture types**

In `apps/desktop-ui/src/types.ts`, extend:

```ts
export type ViewMode = "base_plan" | "three_d_navigation" | "furniture_editor";

export type FurnitureLayerKind = "fixed" | "moveable";

export type PlanPoint = {
  x: number;
  y: number;
};

export type PlanTransform = {
  units: "metres";
  svg_width_px: number;
  svg_height_px: number;
  origin_svg_px: PlanPoint;
  px_per_m: number;
};

export type FurnitureObject = {
  id: string;
  catalog_id: string | null;
  layer: FurnitureLayerKind;
  type: string;
  label: string;
  abbreviation: string | null;
  x_m: number;
  y_m: number;
  width_m: number;
  depth_m: number;
  rotation_deg: number;
  colour: string;
  locked: boolean;
  notes: string | null;
  evidence: string | null;
};

export type FurnitureLayout = {
  project_id: string;
  scenario_id: string;
  plan_transform: PlanTransform;
  objects: FurnitureObject[];
};

export type FurnitureLayoutLoadResult = {
  source: "seed" | "saved";
  layout: FurnitureLayout;
};

export type FurnitureCatalogItem = {
  id: string;
  label: string;
  layer: FurnitureLayerKind;
  type: string;
  abbreviation: string | null;
  default_width_m: number;
  default_depth_m: number;
  colour: string;
  symbol: string;
};

export type FurnitureCatalogGroup = {
  id: string;
  name: string;
  items: FurnitureCatalogItem[];
};

export type FurnitureCatalog = {
  groups: FurnitureCatalogGroup[];
};
```

- [ ] **Step 4: Add Tauri command wrappers**

In `apps/desktop-ui/src/lib/homeDesignCommands.ts`:

```ts
import type {
  AppStatus,
  BuiltInModelStatus,
  FurnitureCatalog,
  FurnitureLayout,
  FurnitureLayoutLoadResult,
  ProjectManifest,
} from "../types";

export function loadFurnitureCatalog(): Promise<FurnitureCatalog> {
  return invoke<FurnitureCatalog>("load_furniture_catalog");
}

export function loadFurnitureLayout(
  projectId: string,
  scenarioId: string,
): Promise<FurnitureLayoutLoadResult> {
  return invoke<FurnitureLayoutLoadResult>("load_furniture_layout", { projectId, scenarioId });
}

export function saveFurnitureLayout(layout: FurnitureLayout): Promise<void> {
  return invoke<void>("save_furniture_layout", { layout });
}
```

- [ ] **Step 5: Bridge Tauri commands**

In `apps/desktop-ui/src-tauri/src/main.rs`, add:

```rust
use home_design_core::{FurnitureCatalog, FurnitureLayout};
use home_design_desktop::{FurnitureLayoutLoadResult, load_furniture_catalog as load_catalog};
use tauri::Manager;

fn app_data_root(app: &tauri::AppHandle) -> Result<std::path::PathBuf, String> {
    app.path()
        .app_data_dir()
        .map_err(|error| format!("could not resolve app data directory: {error}"))
}

#[tauri::command]
fn load_furniture_catalog() -> FurnitureCatalog {
    load_catalog()
}

#[tauri::command]
fn load_furniture_layout(
    app: tauri::AppHandle,
    project_id: String,
    scenario_id: String,
) -> Result<FurnitureLayoutLoadResult, String> {
    let root = app_data_root(&app)?;
    home_design_desktop::load_furniture_layout_from_root(&root, &project_id, &scenario_id)
}

#[tauri::command]
fn save_furniture_layout(app: tauri::AppHandle, layout: FurnitureLayout) -> Result<(), String> {
    let root = app_data_root(&app)?;
    home_design_desktop::save_furniture_layout_to_root(&root, &layout)
}
```

Add the new commands to `tauri::generate_handler![...]`.

- [ ] **Step 6: Run tests/build checks**

Run:

```bash
npm run test --prefix apps/desktop-ui
cargo test --workspace
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```bash
git add apps/desktop-ui/src-tauri/src/main.rs apps/desktop-ui/src/types.ts apps/desktop-ui/src/lib/homeDesignCommands.ts apps/desktop-ui/src/lib/homeDesignCommands.test.ts apps/desktop-ui/src/lib/assetAvailability.test.ts apps/desktop-ui/src/lib/viewState.test.ts
git commit -m "feat: expose furniture commands to desktop ui"
```

---

## Task 5: Frontend Furniture Geometry And State Reducers

**Files:**
- Create: `apps/desktop-ui/src/lib/furnitureGeometry.ts`
- Create: `apps/desktop-ui/src/lib/furnitureGeometry.test.ts`
- Create: `apps/desktop-ui/src/lib/furnitureState.ts`
- Create: `apps/desktop-ui/src/lib/furnitureState.test.ts`
- Create: `apps/desktop-ui/src/lib/furnitureSymbols.ts`
- Create: `apps/desktop-ui/src/lib/furnitureSymbols.test.ts`

- [ ] **Step 1: Write failing geometry tests**

Create `apps/desktop-ui/src/lib/furnitureGeometry.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import {
  dimensionLabel,
  metresToSvg,
  objectBoundsSvg,
  resizeObjectFromCorner,
  svgToMetres,
} from "./furnitureGeometry";
import type { FurnitureObject, PlanTransform } from "../types";

const transform: PlanTransform = {
  units: "metres",
  svg_width_px: 1600,
  svg_height_px: 900,
  origin_svg_px: { x: 518, y: 314 },
  px_per_m: 27.160493827160494,
};

const object: FurnitureObject = {
  id: "sofa",
  catalog_id: "sofa",
  layer: "moveable",
  type: "sofa",
  label: "Sofa",
  abbreviation: null,
  x_m: 5,
  y_m: 3,
  width_m: 2,
  depth_m: 0.9,
  rotation_deg: 0,
  colour: "#33312e",
  locked: false,
  notes: null,
  evidence: null,
};

describe("furniture geometry", () => {
  it("round trips between metres and SVG coordinates", () => {
    const svg = metresToSvg({ x: 2.5, y: 1.25 }, transform);
    const metres = svgToMetres(svg, transform);

    expect(metres.x).toBeCloseTo(2.5, 5);
    expect(metres.y).toBeCloseTo(1.25, 5);
  });

  it("computes SVG object bounds from metre dimensions", () => {
    const bounds = objectBoundsSvg(object, transform);

    expect(bounds.width).toBeCloseTo(54.32, 1);
    expect(bounds.height).toBeCloseTo(24.44, 1);
  });

  it("formats live dimensions in metres", () => {
    expect(dimensionLabel(object)).toBe("2.00 m x 0.90 m");
  });

  it("resizes from a corner with minimum positive dimensions", () => {
    const resized = resizeObjectFromCorner(object, { deltaWidthM: -4, deltaDepthM: 1 }, 0.2);

    expect(resized.width_m).toBe(0.2);
    expect(resized.depth_m).toBeCloseTo(1.9);
  });
});
```

- [ ] **Step 2: Write failing state/symbol tests**

Create `apps/desktop-ui/src/lib/furnitureState.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import {
  addCatalogItem,
  deleteObject,
  duplicateObject,
  moveObject,
  recolourObject,
  resizeObject,
  rotateObject,
} from "./furnitureState";
import type { FurnitureCatalogItem, FurnitureLayout } from "../types";

const layout: FurnitureLayout = {
  project_id: "current-house",
  scenario_id: "current",
  plan_transform: {
    units: "metres",
    svg_width_px: 1600,
    svg_height_px: 900,
    origin_svg_px: { x: 518, y: 314 },
    px_per_m: 27.16,
  },
  objects: [
    {
      id: "sofa",
      catalog_id: "sofa",
      layer: "moveable",
      type: "sofa",
      label: "Sofa",
      abbreviation: null,
      x_m: 1,
      y_m: 2,
      width_m: 2,
      depth_m: 1,
      rotation_deg: 0,
      colour: "#33312e",
      locked: false,
      notes: null,
      evidence: null,
    },
  ],
};

const catalogItem: FurnitureCatalogItem = {
  id: "custom_rectangle",
  label: "Custom rectangle",
  layer: "moveable",
  type: "custom",
  abbreviation: null,
  default_width_m: 1.2,
  default_depth_m: 0.6,
  colour: "#f7f8f6",
  symbol: "rectangle",
};

describe("furniture state reducers", () => {
  it("adds catalog items with unique ids", () => {
    const updated = addCatalogItem(layout, catalogItem, { x: 3, y: 4 });

    expect(updated.objects).toHaveLength(2);
    expect(updated.objects[1].id).toMatch(/^custom_rectangle-/);
    expect(updated.objects[1].x_m).toBe(3);
  });

  it("moves, resizes, rotates, and recolours objects immutably", () => {
    let updated = moveObject(layout, "sofa", { x: 2, y: 3 });
    updated = resizeObject(updated, "sofa", { width_m: 2.4, depth_m: 1.2 });
    updated = rotateObject(updated, "sofa", 90);
    updated = recolourObject(updated, "sofa", "#ffffff");

    expect(updated.objects[0]).toMatchObject({
      x_m: 2,
      y_m: 3,
      width_m: 2.4,
      depth_m: 1.2,
      rotation_deg: 90,
      colour: "#ffffff",
    });
    expect(layout.objects[0].x_m).toBe(1);
  });

  it("duplicates and deletes objects", () => {
    const duplicated = duplicateObject(layout, "sofa");
    expect(duplicated.objects).toHaveLength(2);
    expect(duplicated.objects[1].id).toMatch(/^sofa-copy-/);

    const deleted = deleteObject(duplicated, "sofa");
    expect(deleted.objects.map((object) => object.id)).not.toContain("sofa");
  });
});
```

Create `apps/desktop-ui/src/lib/furnitureSymbols.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { symbolForFurnitureObject } from "./furnitureSymbols";

describe("furniture symbols", () => {
  it("maps Planner-style abbreviations for fixtures", () => {
    expect(symbolForFurnitureObject("refrigerator", "REF")).toMatchObject({
      abbreviation: "REF",
      shape: "appliance",
    });
    expect(symbolForFurnitureObject("toilet", "TLT")).toMatchObject({
      abbreviation: "TLT",
      shape: "fixture",
    });
  });

  it("uses top-down furniture silhouettes for moveable furniture", () => {
    expect(symbolForFurnitureObject("sofa", null).shape).toBe("sofa");
    expect(symbolForFurnitureObject("desk", null).shape).toBe("desk");
  });
});
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
npm run test --prefix apps/desktop-ui -- furnitureGeometry furnitureState furnitureSymbols
```

Expected: missing module failures.

- [ ] **Step 4: Implement pure geometry/state/symbol modules**

Implement `furnitureGeometry.ts` with these exported functions:

```ts
import type { FurnitureObject, PlanPoint, PlanTransform } from "../types";

export type SvgBounds = {
  x: number;
  y: number;
  width: number;
  height: number;
  cx: number;
  cy: number;
};

export function metresToSvg(point: PlanPoint, transform: PlanTransform): PlanPoint {
  return {
    x: transform.origin_svg_px.x + point.x * transform.px_per_m,
    y: transform.origin_svg_px.y + point.y * transform.px_per_m,
  };
}

export function svgToMetres(point: PlanPoint, transform: PlanTransform): PlanPoint {
  return {
    x: (point.x - transform.origin_svg_px.x) / transform.px_per_m,
    y: (point.y - transform.origin_svg_px.y) / transform.px_per_m,
  };
}

export function objectBoundsSvg(object: FurnitureObject, transform: PlanTransform): SvgBounds {
  const centre = metresToSvg({ x: object.x_m, y: object.y_m }, transform);
  const width = object.width_m * transform.px_per_m;
  const height = object.depth_m * transform.px_per_m;
  return {
    x: centre.x - width / 2,
    y: centre.y - height / 2,
    width,
    height,
    cx: centre.x,
    cy: centre.y,
  };
}

export function dimensionLabel(object: Pick<FurnitureObject, "width_m" | "depth_m">): string {
  return `${object.width_m.toFixed(2)} m x ${object.depth_m.toFixed(2)} m`;
}

export function resizeObjectFromCorner<T extends FurnitureObject>(
  object: T,
  delta: { deltaWidthM: number; deltaDepthM: number },
  minimumM = 0.2,
): T {
  return {
    ...object,
    width_m: Math.max(minimumM, object.width_m + delta.deltaWidthM),
    depth_m: Math.max(minimumM, object.depth_m + delta.deltaDepthM),
  };
}
```

Implement `furnitureState.ts` as pure immutable reducers. Do not use timestamps or randomness inside reducers. Implement a local `nextObjectId(existingIds, baseId)` that returns `baseId-1`, `baseId-2`, etc.

Implement `furnitureSymbols.ts` with a small switch:

```ts
export type FurnitureSymbol = {
  shape: "rectangle" | "appliance" | "fixture" | "sofa" | "bed" | "desk" | "table" | "chair" | "storage";
  abbreviation: string | null;
};

export function symbolForFurnitureObject(type: string, abbreviation: string | null): FurnitureSymbol {
  switch (type) {
    case "refrigerator":
    case "dishwasher":
    case "washer":
    case "dryer":
      return { shape: "appliance", abbreviation };
    case "toilet":
    case "shower":
    case "vanity":
      return { shape: "fixture", abbreviation };
    case "sofa":
      return { shape: "sofa", abbreviation };
    case "bed":
      return { shape: "bed", abbreviation };
    case "desk":
      return { shape: "desk", abbreviation };
    case "table":
      return { shape: "table", abbreviation };
    case "chair":
      return { shape: "chair", abbreviation };
    case "wardrobe":
    case "bookcase":
    case "cabinet":
      return { shape: "storage", abbreviation };
    default:
      return { shape: "rectangle", abbreviation };
  }
}
```

- [ ] **Step 5: Run frontend tests**

Run:

```bash
npm run test --prefix apps/desktop-ui -- furnitureGeometry furnitureState furnitureSymbols
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add apps/desktop-ui/src/lib/furnitureGeometry.ts apps/desktop-ui/src/lib/furnitureGeometry.test.ts apps/desktop-ui/src/lib/furnitureState.ts apps/desktop-ui/src/lib/furnitureState.test.ts apps/desktop-ui/src/lib/furnitureSymbols.ts apps/desktop-ui/src/lib/furnitureSymbols.test.ts
git commit -m "feat: add furniture editor state helpers"
```

---

## Task 6: Native Furniture Editor Components

**Files:**
- Create: `apps/desktop-ui/src/lib/furnitureStore.ts`
- Create: `apps/desktop-ui/src/DimensionBadge.svelte`
- Create: `apps/desktop-ui/src/FurnitureLayerControls.svelte`
- Create: `apps/desktop-ui/src/FurnitureCatalogPanel.svelte`
- Create: `apps/desktop-ui/src/FurnitureObjectInspector.svelte`
- Create: `apps/desktop-ui/src/PlanCanvas.svelte`
- Create: `apps/desktop-ui/src/FurnitureEditorView.svelte`
- Modify: `apps/desktop-ui/src/App.svelte`
- Modify: `apps/desktop-ui/src/lib/viewState.test.ts`

- [ ] **Step 1: Write view-state test for native editor routing**

In `apps/desktop-ui/src/lib/viewState.test.ts`, add or update fixture assertions so the selected furniture view has mode `furniture_editor` and remains selectable:

```ts
it("selects the furniture editor native view when available", () => {
  const projectWithFurniture = {
    ...project,
    views: [
      ...project.views,
      {
        id: "furniture-editor",
        label: "Furniture Editor",
        mode: "furniture_editor",
        asset_path: "/views/reference_plan.svg",
        available: true,
      },
    ],
  } satisfies ProjectManifest;

  expect(selectAvailableView(projectWithFurniture, "furniture-editor")).toBe("furniture-editor");
  expect(activeView(projectWithFurniture, "furniture-editor")?.mode).toBe("furniture_editor");
});
```

- [ ] **Step 2: Add furniture store helper**

Create `apps/desktop-ui/src/lib/furnitureStore.ts`:

```ts
import type { FurnitureCatalog, FurnitureLayout, FurnitureLayoutLoadResult } from "../types";
import { loadFurnitureCatalog, loadFurnitureLayout, saveFurnitureLayout } from "./homeDesignCommands";

export type FurnitureEditorData = {
  catalog: FurnitureCatalog;
  layoutResult: FurnitureLayoutLoadResult;
};

export async function loadFurnitureEditorData(
  projectId: string,
  scenarioId = "current",
): Promise<FurnitureEditorData> {
  const [catalog, layoutResult] = await Promise.all([
    loadFurnitureCatalog(),
    loadFurnitureLayout(projectId, scenarioId),
  ]);
  return { catalog, layoutResult };
}

export async function persistFurnitureLayout(layout: FurnitureLayout): Promise<void> {
  await saveFurnitureLayout(layout);
}
```

- [ ] **Step 3: Add small presentational controls**

Create `DimensionBadge.svelte`:

```svelte
<script lang="ts">
  type Props = {
    label: string | null;
    x: number;
    y: number;
  };

  let { label, x, y }: Props = $props();
</script>

{#if label}
  <div class="dimension-badge" style={`left:${x}px; top:${y}px;`}>
    {label}
  </div>
{/if}

<style>
  .dimension-badge {
    position: absolute;
    transform: translate(-50%, -120%);
    pointer-events: none;
    padding: 3px 6px;
    border: 1px solid #263238;
    background: #fffdf8;
    color: #263238;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
  }
</style>
```

Create `FurnitureLayerControls.svelte` with two checkboxes for fixed/moveable visibility and edit mode. Keep the props simple:

```svelte
<script lang="ts">
  type Props = {
    fixedVisible: boolean;
    moveableVisible: boolean;
    onToggleFixed: () => void;
    onToggleMoveable: () => void;
  };

  let { fixedVisible, moveableVisible, onToggleFixed, onToggleMoveable }: Props = $props();
</script>

<section class="layer-controls" aria-label="Furniture layers">
  <label><input type="checkbox" checked={fixedVisible} onchange={onToggleFixed}> Fixed</label>
  <label><input type="checkbox" checked={moveableVisible} onchange={onToggleMoveable}> Moveable</label>
</section>
```

Create `FurnitureCatalogPanel.svelte` and `FurnitureObjectInspector.svelte` with no hidden side effects. They should call callbacks passed from `FurnitureEditorView`.

- [ ] **Step 4: Add PlanCanvas**

Create `apps/desktop-ui/src/PlanCanvas.svelte`. It should:

- render one `<svg viewBox="0 0 1600 900">`
- render `<image href={backgroundAssetPath} width="1600" height="900" />`
- filter objects by layer visibility
- render one group per object with `data-furniture-object={object.id}`
- use `objectBoundsSvg(...)`
- use `symbolForFurnitureObject(...)`
- expose pointer handlers for select, move, and resize
- display resize handles only for the selected object
- call `onResizePreview(label, x, y)` while resizing

Keep the first version simple: pointer drag moves objects; resize handles can adjust width/depth in object-local axes. Numeric inspector fields remain the fallback for rotated object resizing.

- [ ] **Step 5: Add FurnitureEditorView**

Create `apps/desktop-ui/src/FurnitureEditorView.svelte`. It should:

- load catalog/layout on mount using `loadFurnitureEditorData(projectId)`
- keep `layout`, `selectedObjectId`, `fixedVisible`, `moveableVisible`, `saveState`, and `dimensionBadge` in `$state`
- call reducers from `furnitureState.ts`
- debounce save with a short timeout or save explicitly after each completed edit
- show load/save errors without losing in-memory edits
- render `PlanCanvas`, `FurnitureLayerControls`, `FurnitureCatalogPanel`, and `FurnitureObjectInspector`

Use this component prop shape:

```ts
type Props = {
  projectId: string;
  backgroundAssetPath: string;
};
```

- [ ] **Step 6: Route native editor in App.svelte**

In `apps/desktop-ui/src/App.svelte`, import:

```ts
import FurnitureEditorView from "./FurnitureEditorView.svelte";
```

Change the selected-view rendering:

```svelte
{:else if selectedView}
  <header class="workspace-header">...</header>
  {#if selectedView.mode === "furniture_editor" && project}
    <FurnitureEditorView projectId={project.id} backgroundAssetPath={selectedView.asset_path} />
  {:else}
    <div class="view-frame">
      <iframe ...></iframe>
    </div>
  {/if}
```

Keep 3D keyboard forwarding active only for `three_d_navigation`.

- [ ] **Step 7: Run frontend checks**

Run:

```bash
npm run test --prefix apps/desktop-ui
npm run build --prefix apps/desktop-ui
```

Expected: PASS.

- [ ] **Step 8: Commit**

Run:

```bash
git add apps/desktop-ui/src/FurnitureEditorView.svelte apps/desktop-ui/src/PlanCanvas.svelte apps/desktop-ui/src/FurnitureLayerControls.svelte apps/desktop-ui/src/FurnitureCatalogPanel.svelte apps/desktop-ui/src/FurnitureObjectInspector.svelte apps/desktop-ui/src/DimensionBadge.svelte apps/desktop-ui/src/lib/furnitureStore.ts apps/desktop-ui/src/App.svelte apps/desktop-ui/src/lib/viewState.test.ts
git commit -m "feat: add native furniture editor view"
```

---

## Task 7: Full Verification, Packaging, And Manual App Check

**Files:**
- Any generated files from previous tasks.
- No new source files expected unless verification reveals a bug.

- [ ] **Step 1: Run the complete Python test suite**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run the complete Rust test suite**

Run:

```bash
cargo test --workspace
```

Expected: all tests pass.

- [ ] **Step 3: Run the complete frontend test/build suite**

Run:

```bash
npm run test --prefix apps/desktop-ui
npm run build --prefix apps/desktop-ui
```

Expected: all tests pass and the Vite build completes.

- [ ] **Step 4: Build the debug desktop app**

Run:

```bash
npm run tauri --prefix apps/desktop-ui -- build --debug
```

Expected: debug `.app` bundle is produced under `target/debug/bundle/macos/`.

- [ ] **Step 5: Manual desktop verification**

Open the debug app and verify:

- Base View loads.
- Base View `Dimensions` toggle shows and hides dimension lines.
- Sunlight controls still work with dimensions off and on.
- 3D Navigation still receives keyboard/mouse controls.
- Furniture Editor tab appears.
- Furniture Editor loads the reference SVG background.
- Fixed/moveable layer toggles work.
- Catalog adds objects.
- Selecting, moving, resizing, rotating, recolouring, duplicating, and deleting objects works.
- Resize feedback shows metre dimensions.
- Edits persist after closing/reopening the app.

- [ ] **Step 6: Commit any verification fixes**

If manual verification produces fixes:

```bash
git add <changed-files>
git commit -m "fix: polish furniture editor verification issues"
```

- [ ] **Step 7: Push branch**

Run:

```bash
git push
```

Expected: `codex/rust-model-core` pushes successfully.

---

## Final Acceptance Checklist

- [ ] Base View dimensions overlay is present, hidden by default, and uses metre labels.
- [ ] Base View dimensions toggle is independent from sunlight controls.
- [ ] Furniture Editor appears as a native desktop view.
- [ ] Fixed and moveable furniture layers can be toggled independently.
- [ ] Seed layout contains current-house fixed and moveable objects.
- [ ] Catalog contains current-house-first grouped objects and custom rectangle.
- [ ] Users can add, select, move, resize, rotate, recolour, duplicate, and delete objects.
- [ ] Resize interactions display temporary metre dimensions.
- [ ] Furniture layout saves to app data and reloads after restart.
- [ ] Python tests, Rust tests, frontend tests/build, and debug Tauri build pass.
- [ ] PR branch is pushed.
