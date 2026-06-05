# Furniture Ordering And Zoom Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add persistent global furniture stacking controls and raise the furniture editor zoom limit to 2000%.

**Architecture:** Rust owns the persisted furniture contract and must load old saved layouts that do not yet contain order data. Svelte owns editing reducers and UI controls; the canvas should render from a sorted derived list while all changes continue through the existing commit, save, and undo/redo path.

**Tech Stack:** Rust workspace crates with serde, Tauri command boundary, Svelte 5, TypeScript, Vitest.

---

## File Structure

- Modify `crates/home-design-core/src/furniture.rs`
  - Add `z_index` to the Rust `FurnitureObject` contract.
  - Add z-order normalisation helpers for seed and loaded layouts.
  - Keep serde backwards-compatible with saved JSON missing `z_index`.
- Modify `crates/home-design-core/tests/furniture_contracts.rs`
  - Cover seed z-order and JSON round-trip including `z_index`.
  - Cover direct legacy object deserialization without `z_index`.
- Modify `crates/home-design-desktop/src/furniture_storage.rs`
  - Normalise saved furniture layout order before validation and return.
- Modify `crates/home-design-desktop/tests/desktop_contracts.rs`
  - Verify legacy saved furniture JSON without `z_index` loads and receives sequential order.
- Modify `apps/desktop-ui/src/types.ts`
  - Add `z_index` to the TypeScript `FurnitureObject` type.
- Modify `apps/desktop-ui/src/lib/furnitureState.ts`
  - Add ordering helpers.
  - Assign front-most order to added and duplicated objects.
  - Normalise legacy/missing order in loaded layouts.
- Modify `apps/desktop-ui/src/lib/furnitureState.test.ts`
  - Cover normalisation, add/duplicate front placement, and reorder operations.
- Modify `apps/desktop-ui/src/lib/furnitureGeometry.ts`
  - Raise max plan zoom from `10` to `20`.
- Modify `apps/desktop-ui/src/lib/furnitureGeometry.test.ts`
  - Update clamp, label, and wheel zoom tests for 2000%.
- Modify `apps/desktop-ui/src/PlanCanvas.svelte`
  - Render `visibleObjects` from sorted z-order.
- Modify `apps/desktop-ui/src/FurnitureEditorView.svelte`
  - Wire selected-object ordering through `commitLayout`.
- Modify `apps/desktop-ui/src/FurnitureObjectInspector.svelte`
  - Add order control buttons for the selected object.
- Modify `apps/desktop-ui/src/furnitureCanvasInteraction.test.ts`
  - Assert inspector controls, editor wiring, and sorted canvas rendering.

## Task 1: Rust Contract And Legacy Loading

**Files:**
- Modify: `crates/home-design-core/src/furniture.rs`
- Modify: `crates/home-design-core/tests/furniture_contracts.rs`
- Modify: `crates/home-design-desktop/src/furniture_storage.rs`
- Modify: `crates/home-design-desktop/tests/desktop_contracts.rs`

- [ ] **Step 1: Write failing core tests for z-order contract**

Add tests to `crates/home-design-core/tests/furniture_contracts.rs`:

```rust
#[test]
fn seed_layout_assigns_sequential_furniture_z_index() {
    let layout = seed_current_furniture_layout();

    let z_indexes: Vec<_> = layout.objects.iter().map(|object| object.z_index).collect();

    assert_eq!(z_indexes.first(), Some(&0));
    assert_eq!(z_indexes.last(), Some(&((layout.objects.len() as i32) - 1)));
    assert_eq!(
        z_indexes,
        (0..layout.objects.len() as i32).collect::<Vec<_>>()
    );
}

#[test]
fn furniture_object_deserializes_when_legacy_json_omits_z_index() {
    let json = serde_json::json!({
        "id": "legacy-chair",
        "catalog_id": "chair",
        "layer": "moveable",
        "type": "chair",
        "label": "Legacy chair",
        "abbreviation": null,
        "x_m": 1.0,
        "y_m": 2.0,
        "width_m": 0.5,
        "depth_m": 0.5,
        "rotation_deg": 0.0,
        "colour": "#ffffff",
        "locked": false,
        "notes": null,
        "evidence": null
    });

    let parsed: FurnitureObject = serde_json::from_value(json).expect("legacy object parses");

    assert_eq!(parsed.z_index, 0);
}
```

Update `furniture_layout_round_trips_json_in_metres` to include:

```rust
assert!(json.contains("\"z_index\""));
```

- [ ] **Step 2: Run core tests and confirm failure**

Run:

```bash
cargo test -p home-design-core furniture
```

Expected: FAIL because `FurnitureObject` has no `z_index` field.

- [ ] **Step 3: Implement Rust z-index field and normalisation**

In `crates/home-design-core/src/furniture.rs`, add the field:

```rust
    #[serde(default)]
    pub z_index: i32,
```

Place it after `layer` or before geometry fields so JSON remains readable.

Add a helper near the seed/validation helpers:

```rust
pub fn normalise_furniture_z_order(layout: &mut FurnitureLayout) {
    if layout.objects.is_empty() {
        return;
    }

    let all_default_order = layout.objects.iter().all(|object| object.z_index == 0);
    if all_default_order {
        for (index, object) in layout.objects.iter_mut().enumerate() {
            object.z_index = index as i32;
        }
        return;
    }

    let mut ordered: Vec<(usize, i32)> = layout
        .objects
        .iter()
        .enumerate()
        .map(|(index, object)| (index, object.z_index))
        .collect();
    ordered.sort_by_key(|(index, z_index)| (*z_index, *index));

    for (new_index, (object_index, _)) in ordered.into_iter().enumerate() {
        layout.objects[object_index].z_index = new_index as i32;
    }
}
```

Update `seed_current_furniture_layout()` so it builds the layout into a mutable variable, calls `normalise_furniture_z_order(&mut layout)`, then returns it:

```rust
pub fn seed_current_furniture_layout() -> FurnitureLayout {
    let mut layout = FurnitureLayout {
        // existing fields and objects
    };
    normalise_furniture_z_order(&mut layout);
    layout
}
```

Update `furniture_object(...)` to set:

```rust
        z_index: 0,
```

Update any direct `FurnitureObject` literals in Rust tests with `z_index: 0` unless they intentionally rely on serde default.

- [ ] **Step 4: Run core tests and confirm pass**

Run:

```bash
cargo test -p home-design-core furniture
```

Expected: PASS.

- [ ] **Step 5: Write failing desktop storage legacy-load test**

In `crates/home-design-desktop/tests/desktop_contracts.rs`, add a test that writes a saved layout with `z_index` removed from every object, then loads it:

```rust
#[test]
fn load_saved_furniture_layout_migrates_legacy_missing_z_index() {
    let root = isolated_storage_root("legacy-z-index");
    let path = root.join("projects/current-house/scenarios/current/furniture-layout.json");
    fs::create_dir_all(path.parent().expect("parent")).expect("create parent");

    let layout = home_design_core::seed_current_furniture_layout();
    let mut json = serde_json::to_value(&layout).expect("layout json");
    let objects = json
        .get_mut("objects")
        .and_then(|value| value.as_array_mut())
        .expect("objects array");
    for object in objects {
        object
            .as_object_mut()
            .expect("object")
            .remove("z_index");
    }
    fs::write(&path, serde_json::to_string_pretty(&json).expect("json")).expect("write layout");

    let loaded = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect("load legacy layout");

    assert_eq!(loaded.source, "saved");
    assert_eq!(
        loaded
            .layout
            .objects
            .iter()
            .map(|object| object.z_index)
            .collect::<Vec<_>>(),
        (0..loaded.layout.objects.len() as i32).collect::<Vec<_>>()
    );
}
```

- [ ] **Step 6: Run desktop test and confirm failure**

Run:

```bash
cargo test -p home-design-desktop load_saved_furniture_layout_migrates_legacy_missing_z_index
```

Expected: FAIL because saved layouts are not normalised after load.

- [ ] **Step 7: Normalise loaded layouts before validation**

In `crates/home-design-desktop/src/furniture_storage.rs`, import the helper:

```rust
use home_design_core::{
    FurnitureCatalog, FurnitureLayout, default_furniture_catalog, normalise_furniture_z_order,
    seed_current_furniture_layout, validate_furniture_layout,
};
```

Change saved layout loading to mutable and normalise before validation:

```rust
    let mut layout: FurnitureLayout = serde_json::from_str(&raw)
        .map_err(|error| format!("could not parse furniture layout: {error}"))?;
    normalise_furniture_z_order(&mut layout);
    let validation = validate_furniture_layout(&layout);
```

- [ ] **Step 8: Run Rust verification for touched crates**

Run:

```bash
cargo test -p home-design-core furniture
cargo test -p home-design-desktop furniture
```

Expected: PASS.

- [ ] **Step 9: Commit Rust contract and storage changes**

Run:

```bash
git add crates/home-design-core/src/furniture.rs crates/home-design-core/tests/furniture_contracts.rs crates/home-design-desktop/src/furniture_storage.rs crates/home-design-desktop/tests/desktop_contracts.rs
git commit -m "feat: persist furniture stacking order"
```

## Task 2: TypeScript Furniture Order Reducers

**Files:**
- Modify: `apps/desktop-ui/src/types.ts`
- Modify: `apps/desktop-ui/src/lib/furnitureState.ts`
- Modify: `apps/desktop-ui/src/lib/furnitureState.test.ts`

- [ ] **Step 1: Write failing TypeScript state tests**

In `apps/desktop-ui/src/lib/furnitureState.test.ts`, import the new helpers:

```ts
  reorderObject,
  sortedFurnitureObjects,
```

Add `z_index` to the base fixture objects:

```ts
      z_index: 0,
```

and:

```ts
      z_index: 1,
```

Add tests:

```ts
  it("normalises legacy layouts with missing z-indexes from existing order", () => {
    const legacyLayout = {
      ...layout,
      objects: layout.objects.map(({ z_index: _zIndex, ...object }) => object),
    } as FurnitureLayout;

    const normalised = normaliseFurnitureLayout(legacyLayout);

    expect(normalised.objects.map((object) => object.z_index)).toEqual([0, 1]);
  });

  it("adds and duplicates objects at the front of the global furniture order", () => {
    const added = addCatalogItem(layout, catalogItem, { x: 3, y: 4 });
    expect(added.objects.at(-1)?.z_index).toBe(2);

    const duplicated = duplicateObject(layout, "sofa");
    expect(duplicated.objects.at(-1)).toMatchObject({
      z_index: 2,
      locked: false,
    });
  });

  it("sorts furniture objects by z-index with array order as the tie breaker", () => {
    const unordered = {
      ...layout,
      objects: [
        { ...layout.objects[0], id: "front", z_index: 10 },
        { ...layout.objects[1], id: "back", z_index: 2 },
        { ...layout.objects[0], id: "middle", z_index: 2 },
      ],
    };

    expect(sortedFurnitureObjects(unordered.objects).map((object) => object.id)).toEqual([
      "back",
      "middle",
      "front",
    ]);
  });

  it("reorders objects globally without changing geometry or layer", () => {
    const orderedLayout = {
      ...layout,
      objects: [
        { ...layout.objects[0], id: "desk", z_index: 0, x_m: 1, layer: "fixed" as const },
        { ...layout.objects[1], id: "chair", z_index: 1, x_m: 2, layer: "moveable" as const },
        { ...layout.objects[0], id: "lamp", z_index: 2, x_m: 3, layer: "moveable" as const },
      ],
    };

    const sentBackward = reorderObject(orderedLayout, "chair", "backward");
    expect(sortedFurnitureObjects(sentBackward.objects).map((object) => object.id)).toEqual([
      "chair",
      "desk",
      "lamp",
    ]);
    expect(sentBackward.objects.find((object) => object.id === "chair")).toMatchObject({
      x_m: 2,
      layer: "moveable",
    });

    const broughtToFront = reorderObject(sentBackward, "chair", "front");
    expect(sortedFurnitureObjects(broughtToFront.objects).at(-1)?.id).toBe("chair");

    const sentToBack = reorderObject(broughtToFront, "chair", "back");
    expect(sortedFurnitureObjects(sentToBack.objects)[0].id).toBe("chair");
  });

  it("leaves boundary and missing-object reorders harmless", () => {
    expect(reorderObject(layout, "sofa", "back")).toEqual(layout);
    expect(reorderObject(layout, "missing", "front")).toEqual(layout);
  });
```

- [ ] **Step 2: Run focused state test and confirm failure**

Run:

```bash
npm run test -- src/lib/furnitureState.test.ts
```

from `apps/desktop-ui`.

Expected: FAIL because order fields/helpers do not exist.

- [ ] **Step 3: Implement TypeScript order model and helpers**

In `apps/desktop-ui/src/types.ts`, add:

```ts
  z_index: number;
```

to `FurnitureObject`.

In `apps/desktop-ui/src/lib/furnitureState.ts`, add:

```ts
export type FurnitureOrderAction = "back" | "backward" | "forward" | "front";

function zIndexForObject(object: Partial<Pick<FurnitureObject, "z_index">>, fallback: number): number {
  return Number.isFinite(object.z_index) ? Number(object.z_index) : fallback;
}

function nextZIndex(layout: FurnitureLayout): number {
  if (layout.objects.length === 0) {
    return 0;
  }
  return Math.max(...layout.objects.map((object, index) => zIndexForObject(object, index))) + 1;
}

function withCompactedZIndexes(objects: FurnitureObject[]): FurnitureObject[] {
  const orderedIds = sortedFurnitureObjects(objects).map((object) => object.id);
  const orderById = new Map(orderedIds.map((id, index) => [id, index]));
  return objects.map((object) => ({
    ...object,
    z_index: orderById.get(object.id) ?? 0,
  }));
}

export function sortedFurnitureObjects(objects: FurnitureObject[]): FurnitureObject[] {
  return objects
    .map((object, index) => ({ object, index }))
    .sort((a, b) => {
      const zDiff = zIndexForObject(a.object, a.index) - zIndexForObject(b.object, b.index);
      return zDiff === 0 ? a.index - b.index : zDiff;
    })
    .map(({ object }) => object);
}
```

Update `normaliseFurnitureObject` to preserve or default `z_index`:

```ts
    z_index: zIndexForObject(objectWithDefaults, 0),
```

Update `normaliseFurnitureLayout` to compact after object normalisation:

```ts
    objects: withCompactedZIndexes(layout.objects.map(normaliseFurnitureObject)),
```

Set new object order in `addCatalogItem`:

```ts
    z_index: nextZIndex(layout),
```

Set duplicate order in `duplicateObject`:

```ts
    z_index: nextZIndex(layout),
```

Add `reorderObject`:

```ts
export function reorderObject(
  layout: FurnitureLayout,
  objectId: string,
  action: FurnitureOrderAction,
): FurnitureLayout {
  const sorted = sortedFurnitureObjects(layout.objects);
  const currentIndex = sorted.findIndex((object) => object.id === objectId);
  if (currentIndex === -1) {
    return layout;
  }

  const nextSorted = [...sorted];
  const [selected] = nextSorted.splice(currentIndex, 1);
  let nextIndex = currentIndex;
  if (action === "back") {
    nextIndex = 0;
  } else if (action === "backward") {
    nextIndex = Math.max(0, currentIndex - 1);
  } else if (action === "forward") {
    nextIndex = Math.min(nextSorted.length, currentIndex + 1);
  } else {
    nextIndex = nextSorted.length;
  }

  if (nextIndex === currentIndex) {
    return layout;
  }

  nextSorted.splice(nextIndex, 0, selected);
  const zIndexById = new Map(nextSorted.map((object, index) => [object.id, index]));
  return {
    ...layout,
    objects: layout.objects.map((object) => ({
      ...object,
      z_index: zIndexById.get(object.id) ?? object.z_index,
    })),
  };
}
```

- [ ] **Step 4: Run state tests and fix fixture fallout**

Run:

```bash
npm run test -- src/lib/furnitureState.test.ts
```

Expected: PASS after updating any TypeScript fixture objects that now need `z_index`.

- [ ] **Step 5: Commit TypeScript reducer changes**

Run:

```bash
git add apps/desktop-ui/src/types.ts apps/desktop-ui/src/lib/furnitureState.ts apps/desktop-ui/src/lib/furnitureState.test.ts
git commit -m "feat: add furniture order reducers"
```

## Task 3: Canvas Rendering And Inspector Controls

**Files:**
- Modify: `apps/desktop-ui/src/PlanCanvas.svelte`
- Modify: `apps/desktop-ui/src/FurnitureEditorView.svelte`
- Modify: `apps/desktop-ui/src/FurnitureObjectInspector.svelte`
- Modify: `apps/desktop-ui/src/furnitureCanvasInteraction.test.ts`

- [ ] **Step 1: Write failing canvas/UI source tests**

In `apps/desktop-ui/src/furnitureCanvasInteraction.test.ts`, add tests:

```ts
  it("renders furniture in sorted global z-index order", () => {
    expect(planCanvasSource).toContain("sortedFurnitureObjects");
    expect(planCanvasSource).toContain("sortedFurnitureObjects(layout.objects)");
    expect(planCanvasSource).toContain("let visibleObjects = $derived(");
  });

  it("wires selected furniture order controls through the editor commit path", () => {
    expect(editorSource).toContain("reorderObject");
    expect(editorSource).toContain("handleReorderObject");
    expect(editorSource).toContain("commitLayout(reorderObject(layout, objectId, action))");
    expect(editorSource).toContain("onReorder={handleReorderObject}");
  });

  it("exposes global furniture order controls in the selected object inspector", () => {
    expect(inspectorSource).toContain('onReorder: (objectId: string, action: FurnitureOrderAction) => void;');
    expect(inspectorSource).toContain('aria-label="Furniture order controls"');
    expect(inspectorSource).toContain("Send to Back");
    expect(inspectorSource).toContain("Send Backward");
    expect(inspectorSource).toContain("Bring Forward");
    expect(inspectorSource).toContain("Bring to Front");
  });
```

- [ ] **Step 2: Run focused source test and confirm failure**

Run:

```bash
npm run test -- src/furnitureCanvasInteraction.test.ts
```

Expected: FAIL because sorted rendering and order controls are not wired.

- [ ] **Step 3: Sort canvas rendering by z-index**

In `apps/desktop-ui/src/PlanCanvas.svelte`, import the helper:

```ts
  import { fixedDepthForObject, sortedFurnitureObjects } from "./lib/furnitureState";
```

Change the derived visible list:

```ts
  let visibleObjects = $derived(
    sortedFurnitureObjects(layout.objects).filter(
      (object) =>
        (object.layer === "fixed" && fixedVisible) || (object.layer === "moveable" && moveableVisible),
    ),
  );
```

- [ ] **Step 4: Wire editor order handler through commit/history**

In `apps/desktop-ui/src/FurnitureEditorView.svelte`, import:

```ts
    reorderObject,
```

and type:

```ts
    FurnitureOrderAction,
```

Add handler near `handleChangeLayer`:

```ts
  function handleReorderObject(objectId: string, action: FurnitureOrderAction) {
    if (layout) {
      commitLayout(reorderObject(layout, objectId, action));
    }
  }
```

Pass it to the inspector:

```svelte
        onReorder={handleReorderObject}
```

- [ ] **Step 5: Add selected-object order controls**

In `apps/desktop-ui/src/FurnitureObjectInspector.svelte`, import the type:

```ts
  import type { FurnitureOrderAction } from "./lib/furnitureState";
```

Extend props:

```ts
    onReorder: (objectId: string, action: FurnitureOrderAction) => void;
```

Destructure `onReorder`.

Add an order button group before duplicate/delete actions:

```svelte
    <div class="order-actions" aria-label="Furniture order controls">
      <button type="button" onclick={() => onReorder(object.id, "back")}>Send to Back</button>
      <button type="button" onclick={() => onReorder(object.id, "backward")}>Send Backward</button>
      <button type="button" onclick={() => onReorder(object.id, "forward")}>Bring Forward</button>
      <button type="button" onclick={() => onReorder(object.id, "front")}>Bring to Front</button>
    </div>
```

Add CSS next to `.actions`:

```css
  .order-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }
```

If the source test expects a specific prop type string, keep formatting stable enough for the test.

- [ ] **Step 6: Run focused UI source test**

Run:

```bash
npm run test -- src/furnitureCanvasInteraction.test.ts
```

Expected: PASS.

- [ ] **Step 7: Run Svelte check for prop/type mistakes**

Run:

```bash
npm run build
```

Expected: PASS with `svelte-check found 0 errors and 0 warnings`.

- [ ] **Step 8: Commit rendering and inspector controls**

Run:

```bash
git add apps/desktop-ui/src/PlanCanvas.svelte apps/desktop-ui/src/FurnitureEditorView.svelte apps/desktop-ui/src/FurnitureObjectInspector.svelte apps/desktop-ui/src/furnitureCanvasInteraction.test.ts
git commit -m "feat: add furniture order controls"
```

## Task 4: Raise Furniture Zoom To 2000%

**Files:**
- Modify: `apps/desktop-ui/src/lib/furnitureGeometry.ts`
- Modify: `apps/desktop-ui/src/lib/furnitureGeometry.test.ts`

- [ ] **Step 1: Write failing zoom tests**

In `apps/desktop-ui/src/lib/furnitureGeometry.test.ts`, update the zoom tests:

```ts
  it("clamps and labels furniture plan zoom", () => {
    expect(clampPlanZoom(0.2)).toBe(0.5);
    expect(clampPlanZoom(24)).toBe(20);
    expect(planZoomLabel(1.25)).toBe("125%");
    expect(planZoomLabel(20)).toBe("2000%");
  });

  it("computes wheel zoom up to 2000 percent", () => {
    expect(nextWheelPlanZoom(1, -1)).toBe(1.1);
    expect(nextWheelPlanZoom(1, 1)).toBe(0.9);
    expect(nextWheelPlanZoom(19.9, -1)).toBe(20);
  });
```

- [ ] **Step 2: Run focused zoom tests and confirm failure**

Run:

```bash
npm run test -- src/lib/furnitureGeometry.test.ts
```

Expected: FAIL because `MAX_PLAN_ZOOM` is still `10`.

- [ ] **Step 3: Raise the max zoom constant**

In `apps/desktop-ui/src/lib/furnitureGeometry.ts`, change:

```ts
export const MAX_PLAN_ZOOM = 20;
```

- [ ] **Step 4: Run focused zoom tests**

Run:

```bash
npm run test -- src/lib/furnitureGeometry.test.ts
```

Expected: PASS.

- [ ] **Step 5: Commit zoom change**

Run:

```bash
git add apps/desktop-ui/src/lib/furnitureGeometry.ts apps/desktop-ui/src/lib/furnitureGeometry.test.ts
git commit -m "feat: allow 2000 percent furniture zoom"
```

## Task 5: Full Verification, Relaunch, And Push

**Files:**
- No new feature files; verification touches only generated build outputs outside git.

- [ ] **Step 1: Check worktree scope**

Run:

```bash
git status --short
git log --oneline -5
```

Expected: only intended tracked files are modified or staged between commits.

- [ ] **Step 2: Run full Rust tests**

Run from repository root:

```bash
cargo test
```

Expected: PASS.

- [ ] **Step 3: Run full frontend tests**

Run from `apps/desktop-ui`:

```bash
npm run test
```

Expected: PASS.

- [ ] **Step 4: Run frontend production build**

Run from `apps/desktop-ui`:

```bash
npm run build
```

Expected: PASS, including `svelte-check found 0 errors and 0 warnings`.

- [ ] **Step 5: Check whitespace/errors in git diff**

Run from repository root:

```bash
git diff --check
```

Expected: no output.

- [ ] **Step 6: Build debug Tauri bundle**

Run from `apps/desktop-ui`:

```bash
npm run tauri -- build --debug
```

Expected: PASS and bundle path includes:

```text
target/debug/bundle/macos/Home Design.app
```

- [ ] **Step 7: Relaunch the app for user testing**

Run from repository root:

```bash
pkill -f '/Home Design.app/Contents/MacOS/home-design-tauri' || true
open -n '/Users/rcd58/Home-Design/.worktrees/rust-model-core/target/debug/bundle/macos/Home Design.app'
```

Expected: Home Design opens from the rebuilt debug bundle.

- [ ] **Step 8: Push branch**

Run:

```bash
git push origin codex/rust-model-core
```

Expected: remote branch updates successfully.

- [ ] **Step 9: Final response**

Report:

- ordering controls added and persisted
- new/duplicated furniture appears front-most
- old saved layouts migrate safely
- zoom now reaches 2000%
- verification commands run
- latest commit hashes

Include git directives for any successful stage/commit/push actions in the final response.
