# Furniture Ordering And Zoom Design

## Purpose

Add precise visual stacking control to the furniture editor so overlapping objects can be arranged intentionally, such as showing a chair tucked under a desk.

Also raise the furniture editor zoom ceiling from 1000% to 2000% so small objects and tight placements can be edited more accurately.

This milestone is deliberately scoped to the existing furniture editor. It should not introduce scenario editing, structural editing, or a separate layer-management panel.

## Context

The furniture editor currently persists furniture layouts through the Rust/Tauri command path and edits them in the Svelte UI. Object position, size, rotation, colour, layer, and L-shaped dimensions already save persistently and participate in undo/redo history.

The current canvas renders furniture from `layout.objects`. SVG draw order determines visual stacking, so objects drawn later appear above objects drawn earlier. This makes ordering a natural extension of the existing layout model rather than a rendering rewrite.

The editor already has selected-object controls in the inspector and compact toolbar controls for history and zoom. Adding order controls to the selected-object inspector fits the existing workflow: select an item, adjust its properties, and save through the same layout commit path.

## Selected Approach

Use a persistent global stacking order on each furniture object.

Add an integer `z_index` field to furniture objects. The canvas sorts visible objects by `z_index` before rendering, with higher values drawn later and therefore shown on top. This order is global across fixed and moveable furniture, so any object can be placed above or below any other visible object when needed.

Expose four ordering actions for the selected object:

- Send to Back
- Send Backward
- Bring Forward
- Bring to Front

These actions should update the selected object through the existing `commitLayout` path so ordering changes are saved persistently and included in undo/redo history.

Raise the furniture zoom clamp so the editor supports 2000% maximum zoom. Existing zoom-relative handles and wall-distance labels should continue to use screen-pixel-derived SVG units so they remain usable at high zoom.

## Alternatives Considered

### Reorder By Array Position Only

The app could skip a new field and reorder `layout.objects` directly. That matches SVG rendering mechanics and is simple.

The downside is that order becomes implicit. It is harder to reason about persisted data, migrations, tests, and future object-list UI. A visible `z_index` makes the stored layout clearer and gives later tooling a stable field to use.

### Separate Fixed And Moveable Ordering

The app could sort fixed and moveable furniture independently and always render one layer above the other.

That preserves the current fixed/moveable distinction, but it blocks useful arrangements where a moveable object should sit partly under a fixed object or vice versa. The user confirmed global ordering is acceptable, so the feature should provide direct control across all furniture.

### Full Object Layers Panel

A Photoshop-style object list with drag-to-reorder would be powerful and may be useful later.

It is more UI than this step needs. The immediate workflow is one selected object at a time, so inspector buttons are the smaller, more discoverable first implementation. The persistent `z_index` model keeps a future object-list panel possible.

## User Workflow

1. User opens the furniture editor.
2. User selects an object on the plan, such as a chair.
3. User uses order controls in the object inspector.
4. The selected object moves visually above or below overlapping furniture.
5. The change is saved automatically with the furniture layout.
6. User can undo and redo the ordering change with the existing controls or keyboard shortcuts.

New and duplicated objects should appear at the front by default because newly placed objects usually need immediate selection and editing. They can then be moved backward if they need to sit underneath another item.

The order buttons should be disabled when no object is selected. Boundary actions should be harmless: sending the back-most object backward or bringing the front-most object forward should leave the layout unchanged.

## Data Model

Extend `FurnitureObject` with:

- `z_index`: integer

Normalisation should support existing saved layouts that do not yet have `z_index`. When loading a legacy layout, assign order values based on existing array order so the visual result remains unchanged. The first object should receive the lowest order and later objects progressively higher order.

Because Rust owns the persisted furniture contract, the Rust `FurnitureObject` struct must be backwards-compatible with existing saved JSON. Implementation should either deserialize through a legacy-compatible intermediate type or use a serde default strategy that allows missing `z_index` values to load, then normalise the layout before returning it to the UI. Adding a required Rust field without this migration path is not acceptable because it would make existing saved furniture layouts fail to parse.

When adding or duplicating an object, assign it a `z_index` above the current maximum. If the layout is empty, start with `0`.

Ordering functions should keep order values deterministic and integer-only. They may either swap adjacent `z_index` values or compact the whole layout after a reorder. The important behaviour is stable visual order, easy testing, and no accidental changes to geometry or layer.

## UI Design

Add an `Order` control group to the selected-object inspector near the existing object actions. Use compact buttons with clear labels or icon-plus-tooltip treatment consistent with the current editor controls.

Button behaviour:

- `Send to Back`: selected object receives the lowest global order.
- `Send Backward`: selected object swaps with the nearest object immediately below it.
- `Bring Forward`: selected object swaps with the nearest object immediately above it.
- `Bring to Front`: selected object receives the highest global order.

The controls should affect hidden objects too because ordering is global layout data. However, the selected object must remain selected after the action.

## Rendering

Create a derived sorted furniture list before rendering. The sort should use:

1. `z_index`
2. fallback to current array position for legacy data or equal order values

Visible-layer filtering should still respect the fixed and moveable toggles. Ordering should not change an object's fixed/moveable layer.

## Persistence And History

Ordering changes should use the same layout commit path as move, resize, rotate, recolour, duplicate, delete, and layer changes.

Expected persistence behaviour:

- ordering saves automatically through the existing debounced furniture layout save
- ordering restores when the app is reopened
- undo and redo include ordering changes
- existing saved layouts without `z_index` load without losing their previous visual stacking

## Zoom

Raise the furniture editor maximum zoom from 1000% to 2000%.

Existing interaction expectations should remain:

- mouse wheel zoom still works
- toolbar zoom controls still clamp correctly
- reset zoom still returns to the normal view
- resize handles remain similar on-screen size across zoom levels
- wall-distance labels remain similar on-screen size across zoom levels

No other views need a zoom change in this milestone.

## Testing

Add or update tests for:

- furniture object normalisation assigns `z_index` to legacy layouts
- Rust layout loading accepts saved JSON objects that do not yet include `z_index`
- adding and duplicating furniture puts new objects at the front
- ordering helpers move a selected object backward, forward, to back, and to front
- ordering changes do not change object geometry, colour, layer, or selection
- the canvas renders from a sorted object list rather than raw layout order
- the object inspector exposes ordering controls
- ordering goes through existing commit/history wiring
- the zoom clamp accepts 2000% and labels it correctly

Run the existing frontend verification path after implementation:

- `npm run test`
- `npm run build`
- `git diff --check`
- `npm run tauri -- build --debug`

## Non-Goals

- No object list panel in this milestone.
- No drag-to-reorder layers panel.
- No scenario-specific ordering rules.
- No structural layer ordering.
- No change to base view zoom.
- No change to fixed/moveable layer visibility semantics.
