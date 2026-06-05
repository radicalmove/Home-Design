# Vector 2D Plan Representation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the weakest part of the native 2D view by rendering the current house plan from structured vector geometry instead of relying on a static reference image.

**Architecture:** Use `DATA/house_model.json.current_structure` and `DATA/house_model.json.current_site` display geometry as the source of truth for the first slice. Add a small TypeScript adapter that converts spaces, site elements, and opening/window/door features into renderable SVG primitives. Render that layer inside `PlanCanvas.svelte` under furniture and future structural scenario overlays.

**Tech Stack:** Svelte 5, TypeScript, Vitest, Tauri/Rust desktop shell.

---

### Task 1: Add Vector Plan Data Adapter

**Files:**
- Create: `apps/desktop-ui/src/lib/planVectorModel.ts`
- Test: `apps/desktop-ui/src/lib/planVectorModel.test.ts`

- [ ] Write failing tests proving the adapter returns current rooms, site polygons, windows, doors, and wall segments from model-derived geometry.
- [ ] Implement focused static data for the current house from `DATA/house_model.json` display geometry.
- [ ] Keep output independent from Svelte so future scenario deltas can reuse it.

### Task 2: Render Vector Plan Layer

**Files:**
- Modify: `apps/desktop-ui/src/PlanCanvas.svelte`
- Modify: `apps/desktop-ui/src/baseView.test.ts`

- [ ] Write failing tests proving `PlanCanvas` imports the vector plan model and renders rooms, site, openings, and wall strokes.
- [ ] Render vector site/rooms before furniture.
- [ ] Render openings over walls so windows/doors read clearly.
- [ ] Keep existing furniture, pan/zoom, labels, wall-distance, and scenario transition behaviour intact.

### Task 3: Verify And Relaunch

**Commands:**
- `npm --prefix apps/desktop-ui run test`
- `npm --prefix apps/desktop-ui run build`
- `cargo test`
- `git diff --check`
- `npm --prefix apps/desktop-ui run tauri -- build --debug`
- Relaunch `/Users/rcd58/Home-Design/.worktrees/rust-model-core/target/debug/bundle/macos/Home Design.app`
