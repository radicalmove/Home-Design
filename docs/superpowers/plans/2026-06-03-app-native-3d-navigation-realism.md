# App-Native 3D Navigation Realism Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task in-session. Use superpowers:subagent-driven-development only if the user explicitly asks for subagents. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the static iframe-based 3D Navigation with a native Svelte/Three.js view that loads the current house model, saved furniture layout, photo-informed scene cues, and a 0.30m raised pile/foundation level.

**Architecture:** Keep Rust/Tauri data loading as the runtime boundary, and build the Three.js scene in the Svelte frontend from pure, testable TypeScript scene-config modules. The component loads `DesignReviewData` because that command already combines the model JSON with the current saved furniture layout. Geometry/material/furniture conversion stays in small modules under `apps/desktop-ui/src/lib/threeD/`, while `ThreeDNavigationView.svelte` owns renderer lifecycle, controls, and visual UI overlays.

**Tech Stack:** Svelte 5, Vite, TypeScript, Vitest source/logic tests, Three.js 0.160.0, existing Tauri commands, existing saved furniture layout contract.

---

## Implementation Notes

- Work tests-first. Add the focused failing test for each task before implementation.
- The worktree currently has uncommitted Design Review cleanup files. Do not revert or stage those unless explicitly instructed.
- If committing during execution, stage only the task's touched files and keep unrelated dirty files out of the commit.
- Do not hard-code the user's app-data furniture path in the frontend. Use `loadDesignReviewData(projectId, "current")`.
- Keep `apps/desktop-ui/public/views/house_3d.html` in place until the native view is stable; the manifest can still list its asset path even if `App.svelte` routes 3D natively.
- Use simple primitives first. The first milestone must be accurate enough to navigate, not asset-heavy.

## File Structure

- Create `apps/desktop-ui/src/lib/threeD/geometry.ts`
  - Shared metre/display geometry conversion, bounds, polygon helpers, rotation helpers, raised-floor constants.

- Create `apps/desktop-ui/src/lib/threeD/walls.ts`
  - Curated wall network ported from `CODE/home_design/three_d_viewer.py`.
  - Splits walls around opening bounds so windows, doors, sliders, and sunroom gaps remain visible in the native scene.

- Create `apps/desktop-ui/src/lib/threeD/sceneConfig.ts`
  - Pure conversion from `DesignReviewData` to `ThreeDSceneConfig`.
  - Extracts rooms, walls/features/site where possible, furniture objects, floor elevation, pile/foundation settings, and photo viewpoint targets.

- Create `apps/desktop-ui/src/lib/threeD/materials.ts`
  - Material presets and procedural texture descriptors.

- Create `apps/desktop-ui/src/lib/threeD/furniture3d.ts`
  - Furniture type metadata: default heights, shape kind, material category, special L-shape handling.

- Create `apps/desktop-ui/src/lib/threeD/photoViewpoints.ts`
  - Photo-informed camera presets.

- Create `apps/desktop-ui/src/lib/threeD/sceneConfig.test.ts`
  - Tests data conversion without WebGL.

- Create `apps/desktop-ui/src/ThreeDNavigationView.svelte`
  - Svelte/Three component with data load, renderer lifecycle, controls, toggles, presets, and cleanup.

- Create or modify `apps/desktop-ui/src/threeDNavigationView.test.ts`
  - Source-level wiring/lifecycle assertions consistent with existing frontend tests.

- Modify `apps/desktop-ui/src/App.svelte`
  - Route `selectedView.mode === "three_d_navigation"` to `ThreeDNavigationView` instead of the generic iframe.

## Task 1: Scene Config Contract From Model And Furniture

**Files:**
- Create: `apps/desktop-ui/src/lib/threeD/geometry.ts`
- Create: `apps/desktop-ui/src/lib/threeD/walls.ts`
- Create: `apps/desktop-ui/src/lib/threeD/sceneConfig.ts`
- Create: `apps/desktop-ui/src/lib/threeD/sceneConfig.test.ts`

- [ ] **Step 1: Write the failing scene config test**

Create `sceneConfig.test.ts` with a small in-memory `DesignReviewData` fixture. It should assert:

```ts
import { describe, expect, it } from "vitest";
import { buildThreeDSceneConfig, HOUSE_FLOOR_ELEVATION_M } from "./sceneConfig";

describe("three-dimensional scene config", () => {
  it("builds a raised current-house scene from model and saved furniture", () => {
    const config = buildThreeDSceneConfig(reviewDataFixture);

    expect(config.floorElevationM).toBe(HOUSE_FLOOR_ELEVATION_M);
    expect(config.floorElevationM).toBe(0.3);
    expect(config.rooms.map((room) => room.id)).toContain("lounge");
    expect(config.walls.map((wall) => wall.id)).toContain("lounge_sunroom_wall");
    expect(config.walls.find((wall) => wall.id === "kitchen_east_wall")?.segments.length).toBeGreaterThan(3);
    expect(config.site.map((site) => site.id)).toContain("rear_timber_deck");
    expect(config.openings.map((opening) => opening.id)).toContain("sunroom_lounge_slider");
    expect(config.furniture.map((item) => item.id)).toContain("l_sofa-1");
    expect(config.furniture.find((item) => item.id === "partition_wall-1")?.depthM).toBeLessThanOrEqual(0.04);
  });
});
```

Use a minimal fixture with:
- two rooms
- enough opening definitions to split at least one curated wall
- one site deck element
- one opening
- one L-shaped sofa
- one thin partition wall
- a `plan_transform` matching the furniture layout contract

- [ ] **Step 2: Run focused test to verify failure**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts
```

Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement geometry helpers and scene config types**

Implement:

```ts
export const HOUSE_FLOOR_ELEVATION_M = 0.3;
```

Define types:

```ts
export type ThreeDSceneConfig = {
  units: "metres";
  floorElevationM: number;
  rooms: ThreeDRoom[];
  site: ThreeDSiteElement[];
  openings: ThreeDOpening[];
  furniture: ThreeDFurnitureItem[];
  materials: Record<string, ThreeDMaterialPreset>;
  photoViewpoints: ThreeDPhotoViewpoint[];
};
```

Implement conversion functions for:
- model `current_structure.spaces[*].display_px`
- curated wall paths and wall specs from `CODE/home_design/three_d_viewer.py`
- splitting wall segments around model opening bounds
- model `current_site.elements[*].display_px`
- model `current_structure.features[*].display_px`
- saved furniture objects from `data.furniture_layout.layout.objects`

- [ ] **Step 4: Run focused test to verify pass**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts
```

Expected: PASS.

- [ ] **Step 5: Checkpoint**

If committing is approved:

```bash
git add apps/desktop-ui/src/lib/threeD/geometry.ts apps/desktop-ui/src/lib/threeD/walls.ts apps/desktop-ui/src/lib/threeD/sceneConfig.ts apps/desktop-ui/src/lib/threeD/sceneConfig.test.ts
git commit -m "feat: add native 3d scene config"
```

## Task 2: Native 3D Route And Loading State

**Files:**
- Create: `apps/desktop-ui/src/ThreeDNavigationView.svelte`
- Create: `apps/desktop-ui/src/threeDNavigationView.test.ts`
- Modify: `apps/desktop-ui/src/App.svelte`

- [ ] **Step 1: Write failing source/wiring test**

Create `threeDNavigationView.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import appSource from "./App.svelte?raw";
import viewSource from "./ThreeDNavigationView.svelte?raw";

describe("native 3D navigation view wiring", () => {
  it("routes three_d_navigation to the native Svelte view", () => {
    expect(appSource).toContain('import ThreeDNavigationView from "./ThreeDNavigationView.svelte";');
    expect(appSource).toContain('selectedView.mode === "three_d_navigation"');
    expect(appSource).toContain("<ThreeDNavigationView projectId={project.id} />");
    expect(appSource).toContain("selectedViewDisplayPath");
    expect(appSource).toContain("Native renderer");
  });

  it("loads design review data for model and saved furniture", () => {
    expect(viewSource).toContain("loadDesignReviewData");
    expect(viewSource).toContain("buildThreeDSceneConfig");
    expect(viewSource).toContain("Furniture layout");
  });
});
```

- [ ] **Step 2: Run focused test to verify failure**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/threeDNavigationView.test.ts
```

Expected: FAIL because the component/import/routing does not exist.

- [ ] **Step 3: Implement native component shell**

Create `ThreeDNavigationView.svelte`:
- props: `projectId: string`
- state: loading, error, reviewData, sceneConfig
- on mount: call `loadDesignReviewData(projectId, "current")`
- derive scene config with `buildThreeDSceneConfig`
- render a full-height `section.three-d-navigation`
- include a status overlay with model/furniture source and object count
- include a `div` placeholder for the future canvas

- [ ] **Step 4: Route App.svelte**

Modify `App.svelte`:
- import `ThreeDNavigationView`
- add a branch before the generic iframe:

```svelte
{:else if selectedView.mode === "three_d_navigation" && project}
  <ThreeDNavigationView projectId={project.id} />
```

- add a small display helper so the app header shows `Native renderer` for `three_d_navigation`, rather than the stale `/views/house_3d.html` asset path

- [ ] **Step 5: Run focused test**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/threeDNavigationView.test.ts src/lib/threeD/sceneConfig.test.ts
```

Expected: PASS.

## Task 3: Three.js Renderer Lifecycle And Navigation Controls

**Files:**
- Modify: `apps/desktop-ui/src/ThreeDNavigationView.svelte`
- Modify: `apps/desktop-ui/src/threeDNavigationView.test.ts`

- [ ] **Step 1: Write failing source test for renderer lifecycle**

Add assertions:

```ts
expect(viewSource).toContain('import * as THREE from "three";');
expect(viewSource).toContain("new THREE.WebGLRenderer");
expect(viewSource).toContain("requestAnimationFrame");
expect(viewSource).toContain("cleanupThreeDScene");
expect(viewSource).toContain("keysPressed");
expect(viewSource).toContain("resetCamera");
```

- [ ] **Step 2: Run focused test to verify failure**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/threeDNavigationView.test.ts
```

Expected: FAIL on missing Three.js renderer lifecycle code.

- [ ] **Step 3: Implement renderer lifecycle**

In `ThreeDNavigationView.svelte`:
- bind a canvas/stage container
- create renderer, scene, perspective camera, clock
- set `renderer.outputColorSpace = THREE.SRGBColorSpace`
- set tone mapping and shadow map
- attach resize handler
- implement animation loop
- clean up renderer, geometries/materials, event listeners, and animation frame on destroy

- [ ] **Step 4: Implement navigation controls**

Preserve current behaviour:
- drag look
- `W/S` forward/back
- `A/D` strafe
- `J/L` and arrows turn
- `Q/E` or wheel height
- Reset view button

Do this without PointerLock initially if drag-look is more reliable inside Tauri; pointer lock can be re-added later if needed.

- [ ] **Step 5: Run focused test**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/threeDNavigationView.test.ts
```

Expected: PASS.

## Task 4: Raised House Geometry, Site Context, And Piles

**Files:**
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.ts`
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.test.ts`
- Modify: `apps/desktop-ui/src/ThreeDNavigationView.svelte`

- [ ] **Step 1: Write failing tests for raised floor and piles**

Extend `sceneConfig.test.ts`:

```ts
expect(config.foundation.floorElevationM).toBe(0.3);
expect(config.foundation.pileHeightM).toBe(0.3);
expect(config.foundation.piles.length).toBeGreaterThan(4);
expect(config.site.find((site) => site.id === "rear_timber_deck")?.elevationM).toBeCloseTo(0.28, 1);
```

- [ ] **Step 2: Run focused test to verify failure**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts
```

Expected: FAIL because foundation config and piles do not exist.

- [ ] **Step 3: Implement foundation config**

Generate:
- `foundation.floorElevationM = 0.3`
- `foundation.pileHeightM = 0.3`
- pile points around house outer geometry and major deck/threshold edges
- deck elevation close to threshold

Keep piles simple cylinders or square posts in render code.

- [ ] **Step 4: Render floors/site at elevation**

In the component scene builders:
- room floors at `floorElevationM`
- walls start at floor elevation
- furniture sits on floor elevation
- site ground remains at `Y = 0`
- deck/steps use their own elevations
- piles/foundation posts bridge ground to floor level

- [ ] **Step 5: Run focused tests**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts src/threeDNavigationView.test.ts
```

Expected: PASS.

## Task 5: Saved Furniture Rendering

**Files:**
- Create: `apps/desktop-ui/src/lib/threeD/furniture3d.ts`
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.ts`
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.test.ts`
- Modify: `apps/desktop-ui/src/ThreeDNavigationView.svelte`

- [ ] **Step 1: Write failing tests for furniture type metadata**

Add tests that assert:

```ts
expect(config.furniture.find((item) => item.type === "l_sofa")?.shape).toBe("l_sofa");
expect(config.furniture.find((item) => item.type === "l_desk")?.lShape).toBeTruthy();
expect(config.furniture.find((item) => item.type === "wardrobe_doors")?.heightM).toBeLessThanOrEqual(2.1);
expect(config.furniture.find((item) => item.type === "partition_wall")?.depthM).toBeLessThanOrEqual(0.04);
```

- [ ] **Step 2: Run focused test to verify failure**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts
```

Expected: FAIL on missing furniture shape metadata.

- [ ] **Step 3: Implement furniture metadata**

In `furniture3d.ts`, map types to:
- shape kind
- height
- material family
- whether it should use rounded upholstery, thin panel, tabletop, appliance, sanitary fixture, etc.

Include at least:
`l_sofa`, `l_desk`, `piano`, `bed`, `queen_bed`, `chair`, `stool`, `table`, `desk`, `bookcase`, `cabinet`, `pantry`, `refrigerator`, `oven_cooktop`, `dishwasher`, `washer`, `dryer`, `sink`, `bath`, `shower`, `toilet`, `vanity`, `wardrobe_doors`, `partition_wall`, `fireplace`, `tv`, `dresser_drawers`, `bedside_table`.

- [ ] **Step 4: Implement primitive furniture builders**

In `ThreeDNavigationView.svelte`:
- render simple boxes/panels first
- apply rotation around centre
- use object colour where available
- build L-shapes from two blocks using `l_shape.main_depth_m` and `l_shape.return_width_m`
- render very thin partition/wardrobe objects without inflating thickness

- [ ] **Step 5: Run focused tests**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts src/threeDNavigationView.test.ts
```

Expected: PASS.

## Task 6: Photo-Informed Materials And Lighting

**Files:**
- Create: `apps/desktop-ui/src/lib/threeD/materials.ts`
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.ts`
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.test.ts`
- Modify: `apps/desktop-ui/src/ThreeDNavigationView.svelte`

- [ ] **Step 1: Write failing material tests**

Assert:

```ts
expect(config.materials.kitchenCabinet.baseColor).toBe("#315f8c");
expect(config.materials.deckTimber.pattern).toBe("deck_boards");
expect(config.materials.glazing.transparent).toBe(true);
expect(config.materials.carpet.pattern).toBe("carpet_noise");
```

- [ ] **Step 2: Run focused test to verify failure**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts
```

Expected: FAIL on missing material presets.

- [ ] **Step 3: Implement material presets**

Create material presets for:
- carpet
- vinyl plank
- tile
- plaster wall
- white trim/frame
- glazing
- deck timber
- concrete
- lawn/hedge
- navy kitchen cabinetry
- white counters/sanitary fixtures
- dark sofa fabric
- timber furniture
- dark TV/fireplace/piano

- [ ] **Step 4: Implement material builders**

In `ThreeDNavigationView.svelte`:
- create `MeshStandardMaterial`
- build canvas textures for carpet, plank, tile, deck, concrete, lawn
- set transparent glazing material
- enable shadows and tone mapping
- add hemisphere, directional sun, and warm interior fill lights

- [ ] **Step 5: Run focused tests**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts src/threeDNavigationView.test.ts
```

Expected: PASS.

## Task 7: Photo Viewpoint Presets

**Files:**
- Create: `apps/desktop-ui/src/lib/threeD/photoViewpoints.ts`
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.ts`
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.test.ts`
- Modify: `apps/desktop-ui/src/ThreeDNavigationView.svelte`

- [ ] **Step 1: Write failing viewpoint tests**

Assert config has presets:

```ts
expect(config.photoViewpoints.map((view) => view.id)).toEqual(expect.arrayContaining([
  "deck_to_house",
  "lounge_to_sunroom",
  "sunroom_to_lounge",
  "kitchen_galley",
  "bedroom2_window_wall",
  "front_to_sunroom",
]));
```

- [ ] **Step 2: Run focused test to verify failure**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts
```

Expected: FAIL on missing presets.

- [ ] **Step 3: Implement viewpoint presets**

Add photo-informed camera position/look-at pairs. Use room/site centres and photo names as evidence labels. Keep them approximate but stable.

- [ ] **Step 4: Add preset control**

Add a compact menu or segmented control in `ThreeDNavigationView.svelte`:
- selecting a preset moves camera to position/look-at
- reset returns to default exterior/deck-aware start

- [ ] **Step 5: Run focused tests**

Run:

```bash
cd apps/desktop-ui
npm run test -- src/lib/threeD/sceneConfig.test.ts src/threeDNavigationView.test.ts
```

Expected: PASS.

## Task 8: Full Verification And Visual QA

**Files:**
- All touched files

- [ ] **Step 1: Run full verification**

Run:

```bash
cargo test
cd apps/desktop-ui && npm run test
cd apps/desktop-ui && npm run build
git diff --check
cd apps/desktop-ui && npm run tauri -- build --debug
```

Expected:
- Rust tests pass
- Vitest passes
- Svelte check reports 0 errors and 0 warnings
- Vite build succeeds
- diff check exits 0
- Tauri debug bundle succeeds

- [ ] **Step 2: Relaunch debug app**

Run:

```bash
pkill -f '/Home Design.app/Contents/MacOS/home-design-tauri' || true
open -n '/Users/rcd58/Home-Design/.worktrees/rust-model-core/target/debug/bundle/macos/Home Design.app'
```

- [ ] **Step 3: Visual inspect 3D Navigation**

Open 3D Navigation and check:
- canvas is nonblank
- house is raised above ground on visible piles/foundation
- deck and thresholds align plausibly
- fixed and moveable furniture render
- L-shaped sofa and L-shaped desk are recognisable
- thin partition walls and wardrobe doors remain thin
- sunroom glazing is prominent
- navigation keys and drag-look work
- no UI overlap or cramped text

- [ ] **Step 4: Capture screenshots**

Capture at least:

```bash
screencapture -x /tmp/home-design-native-3d-overview.png
screencapture -x /tmp/home-design-native-3d-lounge.png
screencapture -x /tmp/home-design-native-3d-deck.png
```

Use visual inspection to decide whether another pass is needed before reporting completion.

- [ ] **Step 5: Checkpoint**

If committing is approved:

```bash
git status --short
git add apps/desktop-ui/src/App.svelte \
  apps/desktop-ui/src/ThreeDNavigationView.svelte \
  apps/desktop-ui/src/threeDNavigationView.test.ts \
  apps/desktop-ui/src/lib/threeD \
  docs/superpowers/specs/2026-06-03-app-native-3d-navigation-realism-design.md \
  docs/superpowers/plans/2026-06-03-app-native-3d-navigation-realism.md
git commit -m "feat: add native 3d navigation baseline"
```

## Follow-Up Room Realism Passes

After Task 8, continue in separate tested passes:

1. Kitchen/dining cabinetry, appliance, dining, and deck-door detail.
2. Lounge sofa/fireplace/TV/desk/lighting refinement.
3. Sunroom glazing, piano, play/storage table, thermal-garden-room feel.
4. Bedroom 2 storage, bed, wardrobe/partition, teen-use layout.
5. Master bedroom furniture and wardrobe/window cues.
6. Laundry/entrance/toilet service-zone detail.
7. Exterior front/sunroom arrival sequence.
8. Deck shade/wind context and garden baseline.
