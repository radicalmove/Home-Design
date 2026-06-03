# Home Design

Working model and generated reference plans for the current house layout, photo evidence, daylight notes, and future renovation scenarios.

## Repository Layout

- `DATA/house_model.json` is the current source of truth for measured rooms, site elements, openings, photo evidence, and daylight annotations.
- `CODE/home_design/` contains the renderers, validators, viewers, and CLI.
- `tests/` contains regression tests for the model and generated plans.
- `OUTPUT/` contains generated review artifacts. The HTML/SVG outputs and compact JPEG evidence set are tracked; scratch PNG renders are ignored.
- Top-level `.HEIC`, `.png`, `.pptx`, and `.pdf` files are original or working reference material from the survey process.

## Common Commands

Validate the model:

```bash
python3 -m CODE.home_design.cli validate
```

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Regenerate the current reference plan:

```bash
python3 -m CODE.home_design.cli reference-plan --output OUTPUT/reference_plan.html
python3 -m CODE.home_design.cli reference-plan --output OUTPUT/reference_plan.svg
```

Serve the folder locally:

```bash
python3 -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765/OUTPUT/reference_plan.html
```

## Desktop App

The first Rust desktop milestone follows the RADsuite pattern: a Rust/Tauri shell with a Svelte/Vite UI. The current generated 2D and 3D views are packaged into `apps/desktop-ui/public/views/` so the app does not need Python at runtime.

Install frontend dependencies:

```bash
npm install --prefix apps/desktop-ui
```

Run Rust checks:

```bash
cargo fmt --all --check
cargo test --workspace
```

Run frontend checks:

```bash
npm run test --prefix apps/desktop-ui
npm run build --prefix apps/desktop-ui
```

Run the desktop app in development:

```bash
npm run tauri --prefix apps/desktop-ui -- dev
```

Regenerate packaged view assets during development:

```bash
python3 -m CODE.home_design.cli reference-plan --output OUTPUT/reference_plan.html
python3 -m CODE.home_design.cli house-3d --output OUTPUT/house_3d.html
python3 -m CODE.home_design.cli report --output OUTPUT/calibration_report.html
mkdir -p apps/desktop-ui/public/views
cp OUTPUT/reference_plan.html apps/desktop-ui/public/views/reference_plan.html
cp OUTPUT/house_3d.html apps/desktop-ui/public/views/house_3d.html
cp OUTPUT/calibration_report.html apps/desktop-ui/public/views/calibration_report.html
mkdir -p apps/desktop-ui/public/vendor/three@0.160.0/build
mkdir -p apps/desktop-ui/public/vendor/three@0.160.0/examples
cp apps/desktop-ui/node_modules/three/build/three.module.js apps/desktop-ui/public/vendor/three@0.160.0/build/three.module.js
cp -R apps/desktop-ui/node_modules/three/examples/jsm apps/desktop-ui/public/vendor/three@0.160.0/examples/
perl -0pi -e 's#https://cdn.jsdelivr.net/npm/three@0\.160\.0/#/vendor/three@0.160.0/#g' apps/desktop-ui/public/views/house_3d.html
```
