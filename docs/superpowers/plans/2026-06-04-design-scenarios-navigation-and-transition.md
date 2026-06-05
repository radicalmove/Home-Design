# Design Scenarios Navigation And Transition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add grouped Design 1 plus top-five redesign scenarios to the app, with the same four views under each design and a 10-second 2D transition animation for future designs.

**Architecture:** Introduce scenario/design descriptors at the manifest layer, keep view modes reusable rather than duplicating renderer code, and pass `scenarioId` into every scenario-aware view. Implement the UI in staged slices: grouped navigation first, scenario-aware data loading second, future-design data third, animation fourth.

**Tech Stack:** Rust core manifest + Tauri commands, Svelte 5 desktop UI, Vitest/Svelte tests, existing furniture/design-review/3D scene builders.

---

## Scope And Staging

This project should not attempt to finish every future-design model in one change. The safe route is:

1. Add scenario model and grouped navigation while preserving current-house behaviour.
2. Make the four existing views scenario-aware.
3. Add five top redesign descriptors and rough scenario data.
4. Add a 2D transition animation layer.
5. Populate/refine each scenario's 2D, editor layout, 3D scene, and design review.

The first shippable milestone is "Design 1 grouped nav behaves exactly like today's app, with placeholder future designs visible but not yet pretending to be complete."

## Files And Responsibilities

- `crates/home-design-core/src/lib.rs`
  - Add `DesignScenarioDescriptor` and include scenario metadata in `ProjectManifest`.
  - Keep the four existing `ViewDescriptor`s as reusable view modes.

- `crates/home-design-core/tests/project_manifest_contracts.rs`
  - Assert manifest contains Design 1 plus five redesign scenarios.
  - Assert each scenario is routable to the same four modes.

- `apps/desktop-ui/src/types.ts`
  - Mirror the Rust scenario descriptor shape.
  - Add type helpers for `DesignScenarioDescriptor` and scenario-aware view selection.

- `apps/desktop-ui/src/lib/viewState.ts`
  - Replace flat view selection helpers with scenario-aware helpers while preserving existing compatibility where useful.
  - Provide deterministic default: Design 1 / 2D Plan.

- `apps/desktop-ui/src/lib/viewState.test.ts`
  - Cover default scenario/view selection, unavailable view fallback, and design group selection.

- `apps/desktop-ui/src/App.svelte`
  - Replace flat sidebar view buttons with collapsible design groups.
  - Track `selectedScenarioId` and `selectedViewId`.
  - Pass `scenarioId` into native view components.

- `apps/desktop-ui/src/App.test.ts` or existing Svelte component tests if available
  - Add UI-level coverage for grouped navigation if existing test setup supports it. If not, keep logic in `viewState.test.ts`.

- `apps/desktop-ui/src/BaseView.svelte`
  - Accept `scenarioId`.
  - Load furniture layout for that scenario.
  - Show transition button when `scenarioId !== "current"`.

- `apps/desktop-ui/src/FurnitureEditorView.svelte`
  - Accept `scenarioId`.
  - Load/save the selected scenario's layout rather than hardcoding `"current"`.

- `apps/desktop-ui/src/DesignReviewView.svelte`
  - Accept `scenarioId`.
  - Load scenario-specific review data.

- `apps/desktop-ui/src/ThreeDNavigationView.svelte`
  - Accept `scenarioId`.
  - Load scenario-specific design review data for the scene config.

- `apps/desktop-ui/src/lib/designScenarios.ts`
  - UI helper for labels, scenario order, collapsible group defaults, and "is current design" checks.

- `apps/desktop-ui/src/lib/designTransitions.ts`
  - Define transition interpolation primitives for 2D plan elements and furniture positions.
  - Initial implementation can animate overlays/furniture between current and target scenario.

- `apps/desktop-ui/src/lib/designTransitions.test.ts`
  - Unit tests for 10-second progress interpolation and current-to-target mapping.

- `crates/home-design-core/src/furniture.rs`
  - Add seed layouts for future scenarios only when needed.
  - Keep Design 1 layout untouched.

- `crates/home-design-desktop/src/furniture_storage.rs`
  - Confirm scenario-specific load/save already works; add tests if future scenario IDs need fallback to seed layouts.

- `OUTPUT/bold_structural_redesign_brainstorm_report.md`
  - Source of the five scenario names and descriptions.

---

### Task 1: Add Scenario Metadata To The Project Manifest

**Files:**
- Modify: `crates/home-design-core/src/lib.rs`
- Modify: `crates/home-design-core/tests/project_manifest_contracts.rs`
- Modify: `apps/desktop-ui/src/types.ts`

- [x] **Step 1: Add failing Rust manifest contract**

Add assertions that `built_in_project_manifest()` returns six scenarios:

```rust
let manifest = built_in_project_manifest();
let scenario_ids: Vec<_> = manifest.scenarios.iter().map(|scenario| scenario.id.as_str()).collect();
assert_eq!(
    scenario_ids,
    vec![
        "current",
        "back-side-living-sunroom-bedroom",
        "wet-core-bright-day-room",
        "kitchen-kept-social-spine",
        "two-living-room-family",
        "new-bedroom-pod-bedroom2-lounge",
    ],
);
```

- [x] **Step 2: Run Rust contract test and verify failure**

Run:

```bash
cargo test -p home-design-core project_manifest_contracts
```

Expected: FAIL because `scenarios` is currently `Vec<String>` and does not contain descriptors.

- [x] **Step 3: Implement `DesignScenarioDescriptor`**

In `crates/home-design-core/src/lib.rs`, add:

```rust
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct DesignScenarioDescriptor {
    pub id: String,
    pub label: String,
    pub short_label: String,
    pub summary: String,
    pub source_design: Option<String>,
    pub rank: usize,
    pub complete: bool,
}
```

Change `ProjectManifest.scenarios` from `Vec<String>` to `Vec<DesignScenarioDescriptor>`.

- [x] **Step 4: Populate the six scenarios**

Use these initial labels:

```text
Design 1 - Current House
Design 2 - Back-Side Living Rebuild + Sunroom Bedroom Replacement
Design 3 - Office/Bathroom Wet Core + Bright Service-End Day Room
Design 4 - Kitchen-Kept Social Spine Rebuild
Design 5 - Two-Living-Room Family Plan
Design 6 - New Bedroom Pod + Bedroom 2 Lounge
```

Set `complete: true` only for Design 1 initially. Future designs are visible but marked draft until their data is populated.

- [x] **Step 5: Update TypeScript types**

In `apps/desktop-ui/src/types.ts`, add:

```ts
export type DesignScenarioDescriptor = {
  id: string;
  label: string;
  short_label: string;
  summary: string;
  source_design: string | null;
  rank: number;
  complete: boolean;
};
```

Change `ProjectManifest.scenarios` to `DesignScenarioDescriptor[]`.

- [x] **Step 6: Run focused tests**

Run:

```bash
cargo test -p home-design-core project_manifest_contracts
npm --prefix apps/desktop-ui run test -- src/lib/viewState.test.ts
```

Expected: Rust manifest tests pass; TypeScript may still fail until Task 2 updates helpers.

---

### Task 2: Add Scenario-Aware View State Helpers

**Files:**
- Modify: `apps/desktop-ui/src/lib/viewState.ts`
- Modify: `apps/desktop-ui/src/lib/viewState.test.ts`
- Create: `apps/desktop-ui/src/lib/designScenarios.ts`
- Test: `apps/desktop-ui/src/lib/viewState.test.ts`

- [x] **Step 1: Write failing tests for default selection**

Add tests for:

- default selected scenario is `"current"`;
- default selected view is `"base-view"`;
- unavailable requested view falls back inside the same scenario;
- unknown scenario falls back to `"current"`.

- [x] **Step 2: Implement scenario selection helpers**

Add helpers:

```ts
export type ScenarioViewSelection = {
  scenarioId: string;
  viewId: string;
};

export function firstScenarioId(project: ProjectManifest): string | null;
export function selectAvailableScenario(project: ProjectManifest, requestedScenarioId: string | null): string | null;
export function selectAvailableScenarioView(project: ProjectManifest, requestedScenarioId: string | null, requestedViewId: string | null): ScenarioViewSelection | null;
```

- [x] **Step 3: Preserve existing flat helper compatibility**

Keep `activeView()` and `selectAvailableView()` if existing components/tests still use them. Do not break unrelated callers in the same task.

- [x] **Step 4: Run focused tests**

Run:

```bash
npm --prefix apps/desktop-ui run test -- src/lib/viewState.test.ts
```

Expected: PASS.

---

### Task 3: Replace Flat Sidebar With Collapsible Design Groups

**Files:**
- Modify: `apps/desktop-ui/src/App.svelte`
- Modify: `apps/desktop-ui/src/styles.css` if shared styling is cleaner there
- Test: `apps/desktop-ui/src/lib/viewState.test.ts`

- [x] **Step 1: Add selected scenario state**

In `App.svelte`, replace single `selectedViewId` state with:

```ts
let selectedScenarioId = $state<string | null>(null);
let selectedViewId = $state<string | null>(null);
let collapsedScenarioIds = $state<Set<string>>(new Set());
```

- [x] **Step 2: Initialize Design 1 / 2D Plan**

On project load, call `selectAvailableScenarioView(project, "current", "base-view")`.

- [x] **Step 3: Render collapsible scenario groups**

Sidebar shape:

```svelte
{#each project.scenarios as scenario}
  <section class="design-group">
    <button class="design-group-heading">...</button>
    {#if !collapsed}
      {#each project.views as view}
        <button>2D Plan / 3D Navigation / Furniture Editor / Design Review</button>
      {/each}
    {/if}
  </section>
{/each}
```

- [x] **Step 4: Add draft marker for incomplete designs**

For `scenario.complete === false`, show a subtle `Draft` marker in the sidebar. Do not disable the views; future scenarios can initially show placeholder/current fallback data.

- [x] **Step 5: Update workspace heading**

Header should read:

```text
Design 2 - Back-Side Living Rebuild + Sunroom Bedroom Replacement
2D Plan
```

Use the selected scenario label plus selected view label.

- [x] **Step 6: Run UI checks**

Run:

```bash
npm --prefix apps/desktop-ui run check
npm --prefix apps/desktop-ui run test -- src/lib/viewState.test.ts
```

Expected: PASS.

---

### Task 4: Pass Scenario IDs Into All Native Views

**Files:**
- Modify: `apps/desktop-ui/src/App.svelte`
- Modify: `apps/desktop-ui/src/BaseView.svelte`
- Modify: `apps/desktop-ui/src/FurnitureEditorView.svelte`
- Modify: `apps/desktop-ui/src/DesignReviewView.svelte`
- Modify: `apps/desktop-ui/src/ThreeDNavigationView.svelte`
- Test: existing relevant tests

- [x] **Step 1: Update native view props**

Each native view accepts:

```ts
type Props = {
  projectId: string;
  scenarioId: string;
  ...
};
```

- [x] **Step 2: Replace hardcoded `"current"` loads**

Examples:

```ts
await loadFurnitureLayout(projectId, scenarioId);
await loadDesignReviewData(projectId, scenarioId);
```

- [x] **Step 3: Ensure saves preserve selected scenario**

Furniture editor save calls must save the layout returned/edited for the active scenario. Do not let Design 2 edits overwrite Design 1.

- [x] **Step 4: Run focused tests and type check**

Run:

```bash
npm --prefix apps/desktop-ui run check
npm --prefix apps/desktop-ui run test -- src/lib/furnitureStore.test.ts src/lib/designReview.test.ts src/lib/viewState.test.ts
```

Expected: PASS.

---

### Task 5: Add Future-Scenario Layout Fallbacks

**Files:**
- Modify: `crates/home-design-core/src/furniture.rs`
- Modify: `crates/home-design-desktop/src/furniture_storage.rs`
- Modify: `crates/home-design-core/tests/furniture_contracts.rs`
- Test: Rust furniture/storage tests

- [x] **Step 1: Write failing test for future scenario load**

Assert that loading `back-side-living-sunroom-bedroom` returns a layout with:

```rust
assert_eq!(layout.scenario_id, "back-side-living-sunroom-bedroom");
```

- [x] **Step 2: Implement seed fallback**

If a future scenario has no saved layout yet, return a cloned current layout with `scenario_id` changed and `source: "seed"`. This keeps all views working while future design geometry is built.

- [x] **Step 3: Add scenario validation**

Reject or fallback unknown scenario IDs deliberately. Do not silently save arbitrary typos as new scenarios.

- [x] **Step 4: Run Rust tests**

Run:

```bash
cargo test -p home-design-core furniture_contracts
cargo test
```

Expected: PASS.

---

### Task 6: Add Transition Button And Animation State To 2D Plan

**Files:**
- Modify: `apps/desktop-ui/src/BaseView.svelte`
- Create: `apps/desktop-ui/src/lib/designTransitions.ts`
- Create: `apps/desktop-ui/src/lib/designTransitions.test.ts`
- Modify: `apps/desktop-ui/src/PlanCanvas.svelte` only if overlay support is needed

- [x] **Step 1: Add tests for transition progress**

Test:

```ts
expect(transitionProgressAt(0, 10_000)).toBe(0);
expect(transitionProgressAt(5_000, 10_000)).toBe(0.5);
expect(transitionProgressAt(10_000, 10_000)).toBe(1);
```

- [x] **Step 2: Add future-design-only button**

In `BaseView.svelte`, render `Show transition` only when `scenarioId !== "current"`.

- [x] **Step 3: Implement 10-second animation timer**

Use `requestAnimationFrame`, duration `10_000`, and reset/cancel safely on component destroy.

- [x] **Step 4: Add initial visual transition**

Initial version can animate:

- furniture opacity/movement where matching object IDs exist;
- a current-to-target overlay fade;
- text status `Transition 0%` to `Transition 100%`.

Do not overbuild wall morphing until target scenario geometry exists.

- [x] **Step 5: Run tests**

Run:

```bash
npm --prefix apps/desktop-ui run test -- src/lib/designTransitions.test.ts
npm --prefix apps/desktop-ui run check
```

Expected: PASS.

---

### Task 7: Create Scenario Data For The Five Top Designs

**Files:**
- Create: `DATA/design_scenarios/*.json` or add structured scenario section to `DATA/house_model.json`
- Modify: `crates/home-design-core/src/model.rs` if new model fields are needed
- Modify: `apps/desktop-ui/src/lib/designReview.ts`
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.ts`

- [x] **Step 1: Decide storage shape**

Prefer separate files:

```text
DATA/design_scenarios/current.json
DATA/design_scenarios/back-side-living-sunroom-bedroom.json
DATA/design_scenarios/wet-core-bright-day-room.json
...
```

Each contains:

- scenario metadata;
- room purpose changes;
- rough wall/opening changes;
- rough cost band;
- key risks;
- planned furniture layout notes;
- transition mapping from current spaces.

- [x] **Step 2: Add first scenario data**

Start with `back-side-living-sunroom-bedroom.json`.

- [x] **Step 3: Add loader and tests**

Add Rust or TypeScript loader depending on whether Tauri commands need the data first.

- [x] **Step 4: Repeat for the remaining four designs**

Keep each scenario small and inspectable. Avoid pretending rough layouts are final measured CAD.

---

### Task 8: Scenario-Aware Design Review

**Files:**
- Modify: `apps/desktop-ui/src/lib/designReview.ts`
- Modify: `apps/desktop-ui/src/DesignReviewView.svelte`
- Test: `apps/desktop-ui/src/lib/designReview.test.ts`

- [x] **Step 1: Add failing test for future scenario review title**

For `back-side-living-sunroom-bedroom`, expect review output to mention:

```text
Bedroom 2 becomes the main lounge/day room
```

- [x] **Step 2: Add scenario-specific report sections**

Design review should include:

- what changes from Design 1;
- daylight improvement;
- movement/arrival impact;
- build complexity;
- cost band;
- risks and open feasibility checks.

- [x] **Step 3: Run tests**

Run:

```bash
npm --prefix apps/desktop-ui run test -- src/lib/designReview.test.ts
```

Expected: PASS.

---

### Task 9: Scenario-Aware 3D Navigation

**Files:**
- Modify: `apps/desktop-ui/src/lib/threeD/sceneConfig.ts`
- Modify: `apps/desktop-ui/src/ThreeDNavigationView.svelte`
- Test: `apps/desktop-ui/src/lib/threeD/*.test.ts`

- [x] **Step 1: Add scenario-aware scene config test**

Assert future design can hide/replace sunroom and relabel/use Bedroom 2 as lounge in scene metadata.

- [x] **Step 2: Add rough room-purpose rendering**

Initial future 3D can show:

- removed sunroom footprint as demolished/replaced massing;
- new bedroom mass;
- former Bedroom 2 as lounge;
- office/bathroom as wet-core placeholder.

- [x] **Step 3: Keep current 3D unchanged**

Design 1 must remain exactly current-house rendering unless explicitly selected.

- [x] **Step 4: Run tests/checks**

Run:

```bash
npm --prefix apps/desktop-ui run test -- src/lib/threeD
npm --prefix apps/desktop-ui run check
```

Expected: PASS.

---

### Task 10: End-To-End Verification And Relaunch

**Files:**
- All modified app/core files

- [x] **Step 1: Run full test suite**

Run:

```bash
cargo test
npm --prefix apps/desktop-ui run test
npm --prefix apps/desktop-ui run build
git diff --check
```

Expected: all pass.

- [x] **Step 2: Build debug app**

Run:

```bash
npm --prefix apps/desktop-ui run tauri -- build --debug
```

Expected: debug app bundle produced.

- [x] **Step 3: Relaunch app**

Open:

```text
apps/desktop-ui/src-tauri/target/debug/bundle/macos/Home Design.app
```

or the repo-specific target path shown by the build.

- [ ] **Step 4: Manual smoke checklist**

Check:

- Design 1 expands by default.
- Each design heading collapses/expands.
- Each design has 2D Plan, 3D Navigation, Furniture Editor, Design Review.
- Design 1 views behave as before.
- Future design 2 opens all four views.
- Future design 2 2D Plan shows `Show transition`.
- Transition runs for 10 seconds and resets cleanly.
- Furniture edits in Design 2 do not affect Design 1.

---

## Autonomous Execution Policy

Because the user explicitly asked for work to proceed without direct intervention:

- Use inline staged execution unless blocked.
- Do not stop to ask minor implementation questions; choose the conservative option that preserves Design 1.
- Commit only coherent slices if/when requested or when the workspace is clean enough to avoid unrelated changes.
- If a future-design layout is uncertain, create a draft/placeholder rather than inventing false precision.
- Keep Design 1 stable as the regression baseline.
