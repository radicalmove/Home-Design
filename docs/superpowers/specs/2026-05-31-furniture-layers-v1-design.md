# Furniture Layers V1 Design

## Purpose

Add the first native editing milestone to the Rust desktop app: a 2D furniture editor for the current house.

This milestone should make the app useful for trying furniture and fixture placements without starting structural redesign work yet. It should preserve the current/base house view as the architectural reference, add independently toggleable fixed and moveable furniture layers, and save the edited layout persistently through the Rust/Tauri app.

The feature is deliberately scoped to furniture and fixture layout. Wall removal, extensions, future scenario switching, animated build transitions, cost estimates, movement heatmaps, lifestyle scoring, and garden design remain later milestones.

## Context

The current Rust desktop app already has:

- a RADsuite-style Cargo workspace
- `crates/home-design-core` with shared serializable contracts
- `crates/home-design-desktop` with Tauri-facing commands
- `apps/desktop-ui` with the Svelte desktop shell
- a packaged base/reference plan view with sunlight controls
- a packaged Three.js 3D navigation view
- Rust model loading and validation against `DATA/house_model.json`

The existing Python scenario editor proves the rough editing idea but should not be the long-term implementation surface. It is generated HTML and not integrated into the app state model. The new work should move editing into the native Svelte app and use Rust for typed persistence.

The previous explorer design listed the next milestones as fixed/moveable furniture layers, object catalogs, and manual editing with live metre sizing. This spec covers that sequence as one focused v1.

## Selected Approach

Build a native Svelte/SVG furniture editor inside the desktop app, with typed Rust contracts and JSON persistence.

The app should add a `Furniture Editor` view alongside `Base View` and `3D Navigation`. The editor shows the current plan as a locked background and renders editable furniture objects above it. Users can toggle fixed and moveable layers, select an object, move it, resize it, rotate it, recolour it, create a custom rectangular object, and add standard objects from a catalog.

This is the right next step because it creates the state model needed for later scenario work while staying small enough to test well. It also avoids embedding another generated HTML editor that would become hard to connect to future cost, heatmap, and scenario systems.

## Alternatives Considered

### Extend The Existing Python Scenario Editor

This would be the fastest way to expose more controls because the generated editor already supports editable objects and JSON import/export.

The downside is that it keeps core product behaviour outside the Rust desktop app. It would make persistence, future scenario comparison, and shared UI state harder. It is useful as a reference, not as the target architecture.

### Rewrite The Full 2D Renderer Now

This would replace the packaged base plan with a fully native Svelte renderer for rooms, walls, openings, sunlight, and furniture.

That is likely valuable later, but it is too broad for this step. The existing base/reference view is already useful and includes sunlight controls. V1 should layer editing over a locked reference rather than rewrite the whole plan renderer.

## User Workflow

1. User opens the desktop app.
2. User selects `Furniture Editor`.
3. The editor loads the current house furniture layout from persisted app data, or seeds the default current-house layout if no saved layout exists.
4. The locked current/base plan is visible underneath the editable overlay.
5. User toggles `Fixed` and `Moveable` layers independently.
6. User selects an object from the plan or object list.
7. User edits object geometry and style:
   - move by dragging
   - resize with handles
   - rotate with a control or numeric input
   - recolour with a colour input
   - duplicate or delete
8. While resizing, a temporary dimension badge shows width and depth in metres.
9. User adds new objects from a grouped catalog.
10. Changes are saved persistently and restored when the app is reopened.

V1 should keep the base plan locked. The user should not be able to accidentally edit walls, openings, room labels, or sunlight controls from inside the furniture editor.

The existing `Base View` remains the place for the current sunlight/time-of-year controls in this milestone. The furniture editor should not remove or regress those controls, and its data model should not prevent later scenario-specific light comparison.

## Visual Style

Furniture and fixtures should follow the practical top-down floor-plan language from the Planner 5D floor-plan symbols reference:

https://planner5d.com/blog/floor-plan-symbols-and-abbreviations/

The relevant conventions for this app are:

- beds, couches, chairs, tables, and desks are drawn from above
- tables and desks use simple rectangular or circular forms
- built-in shelving and cabinetry are drawn in or labelled
- kitchen appliances and bathroom/laundry fixtures use compact plan symbols plus abbreviations
- common labels include CAB, REF, D/W, TLT, SHWR, LAV, W, and D

This app should not copy Planner 5D art assets. It should use the same general architectural-symbol approach: clean top-down silhouettes, restrained colours, clear outlines, and short abbreviations where a detailed icon would be noisy.

Fixed furniture should read as part of the house fabric but remain editable. Moveable furniture should read as placed objects. A selected object should have a clear outline and handles without making the underlying plan hard to inspect.

## Object Model

Add typed furniture layout contracts to `home-design-core`.

Core concepts:

- `FurnitureLayout`: one persisted layout for a project and scenario.
- `FurnitureLayerKind`: `fixed` or `moveable`.
- `FurnitureObject`: one placed object on the plan.
- `FurnitureCatalog`: grouped standard object definitions.
- `FurnitureCatalogItem`: reusable template for adding a new object.
- `PlanTransform`: conversion metadata between plan pixels and metres.

Extend the existing app view contract with a native furniture-editor mode rather than treating the editor as another packaged HTML iframe. The view descriptor can still appear in the same navigation model, but the Svelte shell should render the native editor component when that mode is selected.

Suggested persisted object fields:

- `id`: stable string id
- `catalog_id`: optional source catalog item id
- `layer`: `fixed` or `moveable`
- `type`: semantic type such as cabinet, appliance, wardrobe, sofa, bed, desk, table, bookcase, chair, toilet, shower, vanity, washer, dryer
- `label`: display name
- `abbreviation`: optional short plan label
- `x_m`: centre x position in metres in house-plan coordinates
- `y_m`: centre y position in metres in house-plan coordinates
- `width_m`: object width in metres
- `depth_m`: object depth in metres
- `rotation_deg`: clockwise rotation
- `colour`: hex colour
- `locked`: optional object-level lock for seeded objects that should be protected later
- `notes`: optional human-readable notes
- `evidence`: optional pointer to current model evidence or seeded source

Use metres as the canonical persisted unit. The UI can render in SVG pixels, but save/load should not depend on the current viewport size.

## Initial Seed Layout

If no saved furniture layout exists, the app should seed a current-house-first layout from known current objects and fixtures.

Seed fixed objects should include:

- kitchen cabinets/counter runs
- built-in wardrobes or closets where represented in the current model
- fixed bathroom fixtures such as toilet, shower, bath, vanity if they are available in the model
- laundry fixtures/appliances where treated as fixed for planning

Seed moveable objects should include:

- lounge sofa
- dining table
- Bedroom 2 bed
- office desk
- bookcase/storage where supported by current data

The existing Python scenario editor and presentation plan can be used as a starting placement reference, but the seeded Rust/Svelte layout should be stored in the new typed format.

Seeded object confidence should be explicit. Approximate placements should stay editable and carry a note rather than pretending to be measured furniture data.

## Catalog

V1 catalog should be current-house-first, with enough reusable objects to make editing useful immediately.

Catalog groups:

- Kitchen and built-ins: base cabinet, tall cabinet, overhead cabinet, pantry, bench/counter, island, refrigerator, dishwasher, oven/cooktop
- Bathroom and laundry: toilet, shower, bath, vanity/lavatory, washer, dryer, linen storage
- Lounge and dining: sofa, armchair, coffee table, TV/unit, dining table, dining chair, sideboard
- Bedroom and office: single bed, queen bed, wardrobe, desk, office chair, bookcase
- Custom objects: generic rectangle for manually drawn furniture or built-in blocks
- Outdoor placeholders: deck furniture or external markers can remain deferred unless already useful for current layouts

Each catalog item should define a default width/depth in metres, layer kind, abbreviation where useful, colour, and symbol kind. Users should be able to add an item and then edit the placed instance.

## UI Components

Add focused frontend components rather than growing `App.svelte` into a large editor.

Suggested components:

- `FurnitureEditorView.svelte`: owns editor layout, loading state, save state, and high-level interactions.
- `PlanCanvas.svelte`: renders locked plan background and editable SVG overlay.
- `FurnitureLayerControls.svelte`: toggles fixed/moveable visibility and editability.
- `FurnitureCatalogPanel.svelte`: catalog groups and add-object actions.
- `FurnitureObjectInspector.svelte`: selected object controls.
- `DimensionBadge.svelte`: temporary metre sizing feedback while resizing.
- `furnitureGeometry.ts`: hit testing, coordinate conversion, resize math, rotation helpers.
- `furnitureSymbols.ts`: maps object type/symbol kind to Svelte/SVG rendering data.
- `furnitureStore.ts`: app-side load/save state wrapper around Tauri commands.

The editor should avoid nested card-heavy layout. It should feel like a working tool: plan canvas in the main area, compact controls in the side panel, predictable toggles and icon buttons.

For the locked background, prefer the generated `reference_plan.svg` or equivalent SVG content over an iframe. That allows the editable overlay to share one SVG coordinate system with the plan. If the implementation uses a packaged HTML view as a fallback, the furniture overlay must still have a tested coordinate transform and must not depend on DOM access inside an iframe.

## Data Flow

Runtime load flow:

1. Svelte calls `loadFurnitureLayout(project_id, scenario_id)`.
2. Rust resolves the app data file for the built-in project.
3. If a saved file exists, Rust parses and validates it.
4. If no file exists, Rust returns the seeded current-house layout and marks it as unsaved/default.
5. Svelte renders the canvas and controls.

Runtime save flow:

1. User edits objects in Svelte state.
2. Svelte debounces or explicitly triggers save.
3. Svelte calls `saveFurnitureLayout(layout)`.
4. Rust validates object ids, dimensions, layer kinds, colours, and finite numeric geometry.
5. Rust writes JSON to app data using an atomic write pattern.
6. Svelte shows saved/error state.

The first implementation can save one current-house layout for the built-in project. The schema should include `scenario_id` now, using `current`, so future design options do not require a breaking data migration.

## Persistence

Persist user edits under the app data directory rather than modifying `DATA/house_model.json`.

Reasoning:

- `DATA/house_model.json` remains the measured/photo-supported house model.
- Furniture edits are user planning state and should be safe to change often.
- Future scenarios can have separate layout files without muddying the baseline model.

Suggested file shape:

- directory: Tauri app data for `Home Design`
- file: `projects/current-house/scenarios/current/furniture-layout.json`

For development and testing, commands should allow the storage root to be injected or isolated so tests do not read/write the user app data directory.

## Editing Behaviour

V1 interactions:

- Click/tap object to select.
- Drag selected object body to move.
- Drag corner/edge handles to resize.
- Show width/depth in metres while resizing.
- Rotate via inspector numeric input.
- Recolour from inspector.
- Toggle fixed/moveable layer visibility.
- Add object from catalog.
- Duplicate selected object.
- Delete selected object.

Manual drawing is represented in v1 by adding a generic rectangle object from the catalog and resizing/recolouring it. That satisfies the immediate need to draw custom furniture or built-in blocks without introducing freehand geometry. A more advanced freehand or polygon drawing mode should wait until after scenario/wall editing has its own model.

Constraints:

- Dimensions must stay positive and above a minimum useful size.
- Objects should remain selectable even if visually small.
- Handles should not shift layout when they appear.
- Editing one layer should not accidentally edit hidden objects on another layer.
- Resize feedback must use metres, not pixels.

## Coordinate System

The persisted layout should use metres in a house-plan coordinate space.

The current generated 3D viewer uses a reference conversion based on `PIXEL_TO_METRE = 0.81 / 22.0` and a reference pixel origin. V1 can reuse that calibration initially, but should put the conversion metadata in a named `PlanTransform` so it can be improved later without rewriting editor logic.

The UI should keep conversion code in one tested helper. Tests should cover:

- metres to SVG pixels
- SVG pixels to metres
- width/depth conversion
- resize geometry under rotation if rotation-aware resizing is included

V1 should support pointer resizing for unrotated and rotated objects only if the geometry helper keeps the behaviour predictable. If rotation-aware pointer resizing becomes a risk during implementation, rotated objects can still be resized through numeric width/depth fields while pointer handles remain available for unrotated objects.

## Error Handling

The editor should fail visibly and preserve data.

- Layout load failure: show an error panel, keep base app navigation available, and offer reset-to-seed only after confirmation.
- Save failure: keep unsaved local edits in memory and show a clear error state.
- Invalid saved JSON: refuse to overwrite automatically; report the validation issue.
- Missing catalog: keep existing layout visible but disable add-object controls.
- Missing plan background: show the furniture overlay area with an unavailable-base warning.
- Unsupported object type: render a generic labelled rectangle rather than dropping the object.

Rust validation should reject invalid numeric values, invalid colours, duplicate ids, unknown layer kinds, and non-positive dimensions.

## Testing

Add tests at the same layers as the existing Rust desktop work.

Core crate tests:

- default seed layout contains fixed and moveable objects
- catalog groups include current-house-first object types
- layout validation rejects duplicate ids and invalid dimensions
- layout round-trips through JSON
- canonical units are metres

Desktop crate tests:

- load command returns saved layout when file exists
- load command returns seeded layout when no saved layout exists
- save command writes valid JSON
- invalid saved JSON is reported without overwriting
- test storage root is isolated from real app data

Frontend tests:

- command wrappers call expected Tauri commands
- layer visibility/editability state works
- coordinate conversion helpers are reversible within tolerance
- dimension badge uses metre values while resizing
- catalog add action creates an object on the selected layer
- selection, move, resize, recolour, duplicate, and delete reducers work

End-to-end/manual verification:

- desktop app opens
- base view still works
- 3D navigation still works
- furniture editor loads seeded objects
- fixed and moveable layers toggle independently
- resizing shows live metre dimensions
- edits persist after app restart

## Acceptance Criteria

Furniture Layers V1 is complete when:

- `Furniture Editor` is available in the desktop app.
- The current/base plan is visible as a locked background.
- Fixed and moveable furniture layers can be toggled independently.
- A seeded current-house layout appears on first run.
- A grouped object catalog is available.
- Users can add, select, move, resize, rotate, recolour, duplicate, and delete furniture objects.
- Resize feedback displays temporary dimensions in metres.
- Layout edits are saved persistently through Rust/Tauri and reload after restart.
- The implementation has focused Rust and frontend tests.
- Existing base view, sunlight controls, and 3D navigation remain usable.

## Non-Goals

- No wall editing.
- No removing walls.
- No extensions.
- No multi-scenario switching.
- No animated transitions between current and future builds.
- No new sunlight simulation inside the furniture editor.
- No cost estimation engine.
- No movement heatmap or lifestyle scoring engine.
- No garden designer.
- No structural or building-code assessment.
- No replacement of the existing base/reference plan renderer.

## Future Fit

This schema should prepare the app for later scenario work.

Future scenarios can reuse the same `FurnitureLayout` structure with different `scenario_id` values. Scenario transitions can interpolate object positions, dimensions, rotations, and visibility between layouts. Cost estimates can reference catalog ids and scenario object changes. Movement heatmaps can read furniture footprint geometry as obstacles or attractors. Lifestyle assessments can use room labels, furniture types, light settings, and scenario metadata.

Garden design should remain separate until the external site model is more complete, but the same layer/catalog/editing pattern can later apply to outdoor objects.
