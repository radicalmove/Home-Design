# Home Design Rust Desktop Explorer Design

## Purpose

Turn the Home Design project into a RADsuite-style Rust desktop app, starting with a useful Explorer milestone rather than a full rewrite.

The first milestone should open as a self-contained desktop app, show the current house base view, preserve the existing sunlight controls, and provide a 3D navigation tab. It should not require Python at runtime.

The larger product direction remains broader: furniture layers and editing, future design scenarios, cost estimates, animated transitions between options, movement and lifestyle assessments, and eventually garden layout design. Those should be enabled by the architecture, but not built in the first milestone.

## Context

The current project already has:

- `DATA/house_model.json` as the measured/photo-supported source of truth.
- Python model, validation, renderer, and CLI modules under `CODE/home_design/`.
- Generated HTML/SVG outputs under `OUTPUT/`.
- A reference style 2D plan with sunlight controls.
- A generated Three.js 3D house viewer.
- A basic scenario editor.
- A passing Python test suite.

RADsuite uses a Cargo workspace with separated Rust crates, a Tauri 2 desktop app, and a Svelte/Vite frontend. Home Design should follow that shape.

## Selected Approach

Use a RADsuite-style desktop shell first, backed by packaged generated views.

Milestone one should:

- Add a Rust Cargo workspace at the repo root.
- Add a core crate for stable project and manifest data contracts.
- Add a Tauri desktop crate for app commands and packaged asset access.
- Add a Svelte/Vite desktop UI.
- Package the current generated `OUTPUT/reference_plan.html` and `OUTPUT/house_3d.html` as app assets.
- Open one built-in house project.
- Default to the current 2D base/reference view.
- Provide a second mode/tab for 3D navigation.
- Avoid requiring Python at runtime.

Python remains a development-time generator until renderer logic is ported into Rust in later milestones.

## Alternatives Considered

### Rust Core First

Port the model parser, validation, 2D renderer, sunlight config, 3D config, and CLI to Rust before building the app UI.

This is cleaner internally but delays a usable desktop app. It also front-loads the lower-risk work while the main product risk remains the interactive planning interface.

### Full Interactive Rebuild First

Rebuild the 2D and 3D planner immediately as native Svelte and Three.js components.

This is likely where parts of the product should end up, but it discards too much working behaviour at the start and creates a large rewrite risk.

## Architecture

The first desktop milestone should use this structure:

- Root `Cargo.toml` workspace.
- `crates/home-design-core` for serializable data contracts:
  - app status
  - built-in project manifest
  - view descriptors
  - future scenario/layer placeholders
- `crates/home-design-desktop` for Tauri-facing commands:
  - get app status
  - list/load the built-in project manifest
  - resolve packaged view asset availability
- `apps/desktop-ui` for Svelte/Vite UI:
  - app shell
  - project/status loading
  - view tabs
  - embedded packaged view containers
- `apps/desktop-ui/src-tauri` for the Tauri app wrapper, matching RADsuite's frontend-owned Tauri layout if practical.

The first milestone should not attempt to port every Python renderer. It should create the shell and data contract that later ports can target.

## UI And Workflow

The first screen is a practical workspace, not a landing page.

Default workflow:

1. User opens the desktop app.
2. App loads the built-in current house project.
3. Main view shows the current 2D reference/base plan.
4. Existing sunlight controls remain usable inside that view.
5. User can switch to a 3D Navigation tab.
6. User can return to the base view without restarting the app.

First-milestone navigation should include room for later tabs or panels, but those later tools should not be exposed as broken controls.

Planned later areas:

- Fixed furniture layer.
- Moveable furniture layer.
- Object catalog grouped by type.
- Manual object editing: resize, recolour, move, draw, and rotate.
- Temporary metre measurements while resizing.
- Design scenario switching and animated transitions.
- Cost estimates.
- Movement/use heatmaps and lifestyle assessments.
- Garden design.

## Data Flow

Milestone one source of truth remains:

- `DATA/house_model.json`
- `OUTPUT/reference_plan.html`
- `OUTPUT/house_3d.html`

Runtime flow:

1. Svelte calls a Tauri command for app status and project manifest.
2. Rust returns a built-in project manifest.
3. Svelte renders the desktop shell and view tabs.
4. The selected packaged HTML view is loaded into a controlled container.
5. Embedded views own their existing interactions, including sunlight sliders and 3D pointer controls.
6. Missing assets are reported through shell state rather than failing silently.

The built-in project manifest should include:

- project id
- project name
- model/source version label
- base view descriptor
- 3D view descriptor
- packaged asset paths
- available view modes
- future placeholders for scenarios, layers, object catalogs, and analysis outputs

## Error Handling

The app should fail visibly and keep usable views available where possible.

- Missing base view: show a clear missing-asset message.
- Missing 3D view: keep the base view usable and mark 3D unavailable.
- Manifest load failure: show an app-level error instead of a blank window.
- WebGL failure: rely on the existing 3D viewer fallback inside the embedded view.
- Python absence: no runtime error, because Python is not a runtime dependency.

## Packaging

The app should package static generated views as local assets.

Development commands can regenerate those assets before packaging, but the installed app should not shell out to Python.

The initial implementation may copy generated HTML into the frontend public/assets area or include it as bundled Tauri resources. The final choice should follow whichever path best matches Tauri 2 asset loading and the RADsuite app layout.

## Testing

Keep the current Python tests as the renderer/model regression suite while Python remains the development generator.

Add new tests for the Rust desktop app:

- Core crate tests for the built-in project manifest.
- Desktop crate tests for app status and project loading commands.
- Asset availability tests for `reference_plan.html` and `house_3d.html`.
- TypeScript tests for frontend command wrappers and shell state.
- Frontend build/check commands.

Milestone one is complete when:

- Existing Python tests pass.
- Rust workspace tests pass.
- Frontend checks/build pass.
- The desktop app opens the base view.
- The app can switch to the 3D Navigation view.
- The app has no Python runtime dependency.

## Future Milestones

After the Explorer milestone:

1. Port stable model parsing and validation into Rust.
2. Replace packaged 2D view loading with Svelte-driven 2D rendering where needed.
3. Add fixed and moveable furniture layers.
4. Add furniture catalogs using top-down floor-plan symbols inspired by Planner 5D-style conventions.
5. Add object editing with live metre sizing feedback.
6. Add scenario manifests for current and future possible builds.
7. Add animated scenario transitions that move walls and furniture between states.
8. Add cost estimate data and summary panels per scenario.
9. Add movement heatmaps and room-use/lifestyle assessments.
10. Add garden/external layout modelling once the site baseline is more complete.

## Non-Goals For Milestone One

- No full renderer rewrite.
- No furniture editing tools.
- No scenario editing or animated transitions.
- No cost engine.
- No movement/lifestyle scoring engine.
- No garden designer.
- No photorealistic rendering.
- No structural engineering claims.

## Open Implementation Decisions

These should be settled during implementation planning:

- Exact workspace and crate names.
- Whether packaged HTML assets live under frontend `public/` or Tauri bundled resources.
- Whether the embedded views load through `iframe`, WebView navigation, or direct HTML injection.
- Whether the initial project manifest is hard-coded in Rust or loaded from a checked-in JSON file.
- How much of the existing generated HTML should be copied versus regenerated as part of a build step.
