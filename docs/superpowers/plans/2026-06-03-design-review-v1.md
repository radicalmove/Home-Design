# Design Review V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Design Review button/view that shows a thorough first-pass interior-design and builder-style review backed by the latest saved furniture layout, measured model data, daylight assumptions, and representative plan snippets.

**Architecture:** Add a fourth manifest view with a Svelte component instead of an iframe. Rust exposes one review-data command that combines the built-in model JSON with the current saved furniture layout. A pure TypeScript analysis module derives room assignment, layer/object counts, daylight summaries, off-plan warnings, and static authored report sections so the view can refresh live evidence without requiring AI at runtime.

**Tech Stack:** Rust/Tauri command layer, Svelte 5 UI, TypeScript/Vitest analysis tests, existing furniture geometry helpers, existing saved furniture layout store.

---

### Task 1: Add Design Review Manifest And Command Contract

**Files:**
- Modify: `crates/home-design-core/src/lib.rs`
- Modify: `crates/home-design-core/tests/project_manifest_contracts.rs`
- Modify: `crates/home-design-desktop/src/commands.rs`
- Modify: `crates/home-design-desktop/src/lib.rs`
- Modify: `crates/home-design-desktop/tests/desktop_contracts.rs`
- Modify: `apps/desktop-ui/src-tauri/src/main.rs`

- [ ] **Step 1: Write failing Rust contract tests**

Add assertions that the built-in manifest includes a fourth `design-review` view with label `Design Review`, mode `DesignReview`, and an empty asset path. Add a desktop contract test that `load_design_review_data_from_root` returns the built-in model source plus a furniture layout load result.

- [ ] **Step 2: Run Rust tests to verify failure**

Run: `cargo test`
Expected: FAIL because `ViewMode::DesignReview` and `load_design_review_data_from_root` do not exist.

- [ ] **Step 3: Implement minimal Rust contract**

Add `ViewMode::DesignReview`, append the manifest view, define a serializable `DesignReviewData` with `model_source`, `house_model: serde_json::Value`, and `furniture_layout: FurnitureLayoutLoadResult`, and expose `load_design_review_data_from_root`.

- [ ] **Step 4: Wire Tauri command**

Add `load_design_review_data` in `apps/desktop-ui/src-tauri/src/main.rs`, using the existing app-data root and current project/scenario arguments.

- [ ] **Step 5: Run Rust tests**

Run: `cargo test`
Expected: PASS.

### Task 2: Add Pure Design Review Analysis

**Files:**
- Modify: `apps/desktop-ui/src/types.ts`
- Modify: `apps/desktop-ui/src/lib/homeDesignCommands.ts`
- Create: `apps/desktop-ui/src/lib/designReview.ts`
- Create: `apps/desktop-ui/src/lib/designReview.test.ts`

- [ ] **Step 1: Write failing Vitest tests**

Test that `buildDesignReviewAnalysis`:
- counts fixed and moveable objects
- assigns furniture to rooms using model display geometry and the layout transform
- flags off-plan objects
- identifies low winter daylight rooms
- includes core report sections for flow, daylight, bedrooms, furniture, and priorities

- [ ] **Step 2: Run focused test to verify failure**

Run: `npm run test -- src/lib/designReview.test.ts`
Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement analysis module**

Implement geometry conversion, point-in-room checks, daylight scoring, room furniture summaries, off-plan detection, dynamic warning generation, and authored report sections.

- [ ] **Step 4: Add command/types**

Add `design_review` to `ViewMode`, add `DesignReviewData` TypeScript type, and add `loadDesignReviewData(projectId, scenarioId)` to `homeDesignCommands.ts`.

- [ ] **Step 5: Run focused test**

Run: `npm run test -- src/lib/designReview.test.ts`
Expected: PASS.

### Task 3: Build Design Review UI

**Files:**
- Create: `apps/desktop-ui/src/DesignReviewView.svelte`
- Modify: `apps/desktop-ui/src/App.svelte`
- Modify: `apps/desktop-ui/src/styles.css` only if global shell styles need small support
- Modify/Create: focused UI tests by source-inspection where existing project style uses this pattern

- [ ] **Step 1: Write failing UI/source test**

Add assertions that the app imports `DesignReviewView`, routes `selectedView.mode === "design_review"` to it, and the component renders key headings: `Executive View`, `Movement Flow`, `Light And Seasons`, `Room-By-Room Review`, and `Priority Actions`.

- [ ] **Step 2: Run focused UI tests to verify failure**

Run: `npm run test -- src/furnitureCanvasInteraction.test.ts src/lib/viewState.test.ts`
Expected: FAIL on missing design review wiring.

- [ ] **Step 3: Implement view**

Create a dense report page with:
- live refresh button and source/status line
- KPI strip for rooms, furniture layer counts, off-plan items, and low-winter-light rooms
- authored review sections
- dynamic warnings and priorities
- plan snippet cards using the current reference plan SVG background with furniture overlays and focused viewBoxes
- evidence photo list from the model, not full photo loading

- [ ] **Step 4: Wire app navigation**

Import and render `DesignReviewView` for `design_review` mode, passing `project.id`.

- [ ] **Step 5: Run focused UI tests**

Run: `npm run test -- src/furnitureCanvasInteraction.test.ts src/lib/viewState.test.ts src/lib/designReview.test.ts`
Expected: PASS.

### Task 4: Verify, Rebuild, Relaunch, Commit, Push

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

- [ ] **Step 2: Relaunch debug app**

Run:
```bash
pkill -f '/Home Design.app/Contents/MacOS/home-design-tauri'
open -n '/Users/rcd58/Home-Design/.worktrees/rust-model-core/target/debug/bundle/macos/Home Design.app'
pgrep -fl 'Home Design.app/Contents/MacOS/home-design-tauri'
```

- [ ] **Step 3: Inspect Design Review visually**

Use the in-app browser/app where practical or direct desktop relaunch. Confirm the `Design Review` button appears and the report loads with latest furniture evidence.

- [ ] **Step 4: Commit and push**

Run:
```bash
git status --short
git add <touched files>
git commit -m "feat: add design review view"
git push origin codex/rust-model-core
```
