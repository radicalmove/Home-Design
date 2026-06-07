# Design 2 V2 Coherent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework Design 2 so the 2D plan, furniture seed, labels, and transition animation match the revised whole-house concept.

**Architecture:** Keep Design 1 as the measured/reference source of truth. Apply Design 2 as scenario-specific overlay/vector/furniture data, with transition timing staged so structural changes precede furniture movement.

**Tech Stack:** Rust core contracts, Tauri command layer, Svelte 5 UI, Vitest, Cargo tests.

---

### Task 1: Pin the revised Design 2 behavior with tests

**Files:**
- Modify: `apps/desktop-ui/src/lib/designStructuralTransitions.test.ts`
- Modify: `apps/desktop-ui/src/lib/planVectorModel.test.ts`
- Modify: `apps/desktop-ui/src/lib/designTransitions.test.ts`
- Modify: `crates/home-design-core/tests/furniture_contracts.rs`

- [ ] Write tests requiring Design 2 labels to be living/dining/day room, chill/reading, current-lounge bedroom, and replacement bedroom.
- [ ] Write tests requiring the replacement bedroom west edge to align to the master-bedroom west wall.
- [ ] Write tests requiring proposed external walls/windows to use Design 1-like thickness and no extra proposed door marker at the new-bedroom/hall doorway.
- [ ] Write tests requiring transition furniture movement to start after structural progress has begun.
- [ ] Run the focused tests and verify they fail for the expected reasons.

### Task 2: Stage the transition animation

**Files:**
- Modify: `apps/desktop-ui/src/lib/designTransitions.ts`
- Modify: `apps/desktop-ui/src/BaseView.svelte`
- Modify: `apps/desktop-ui/src/PlanCanvas.svelte`

- [ ] Add structural/furniture stage helpers.
- [ ] Use structural progress for wall masks/floors/walls/openings.
- [ ] Use delayed/staggered furniture progress for furniture interpolation.
- [ ] Run focused transition/base-view tests and verify they pass.

### Task 3: Rewrite Design 2 2D overlay and vector model

**Files:**
- Modify: `apps/desktop-ui/src/lib/designStructuralTransitions.ts`
- Modify: `apps/desktop-ui/src/lib/planVectorModel.ts`

- [ ] Rename current lounge proposed use to bedroom.
- [ ] Rename rear/service-end room to living/dining/day room.
- [ ] Add retained-kitchen chill/reading zone without changing the renovated kitchen.
- [ ] Push replacement bedroom west edge to the master-bedroom west line.
- [ ] Correct wall masks, future wall thicknesses, windows, door/opening labels, and plan labels.
- [ ] Run focused structural/vector tests and verify they pass.

### Task 4: Re-seed Design 2 furniture

**Files:**
- Modify: `crates/home-design-core/src/furniture.rs`
- Modify: `crates/home-design-core/tests/furniture_contracts.rs`

- [ ] Place dining table/chairs and lounge seating in the rear living/dining/day room.
- [ ] Place softer chill/reading furniture near the retained kitchen/dining edge where available.
- [ ] Place bed/bedroom furniture in the current lounge bedroom and replacement bedroom.
- [ ] Keep service-room furniture within separated service rooms.
- [ ] Run Rust furniture contract tests and verify they pass.

### Task 5: Update scenario/review wording and verify

**Files:**
- Modify: `DATA/design_scenarios/back-side-living-sunroom-bedroom.json`
- Modify: relevant frontend tests.

- [ ] Update Design 2 description so it matches the revised whole-house concept.
- [ ] Run `npm --prefix apps/desktop-ui run test`.
- [ ] Run `npm --prefix apps/desktop-ui run build`.
- [ ] Run `cargo test`.
- [ ] Run `npm --prefix apps/desktop-ui run tauri -- build --debug`.
- [ ] Relaunch `target/debug/bundle/macos/Home Design.app`.
