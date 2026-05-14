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

