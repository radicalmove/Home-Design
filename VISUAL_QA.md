# Visual QA Gate

Rendered visual inspection is mandatory for visual changes.

This project is a graphical house-design tool. A change can pass coordinate tests, source tests, and builds while still being visually wrong. Do not claim a visual change is complete from tests alone.

## When This Applies

Use this gate for any change affecting:

- 2D Plan, Design scenario plans, transitions, room labels, dimensions, sunlight, or layers
- Furniture Editor symbols, furniture placement, controls, labels, zoom, panning, or editing handles
- 3D Navigation geometry, materials, furniture, windows, doors, navigation, camera, or photo-matching
- Design Review snippets, movement maps, heatmaps, or rendered plan evidence
- CSS or layout that changes visible spacing, controls, panels, or typography

## Required Workflow

1. Identify the affected visual surface and the adjacent areas that could be disturbed.
2. Find the reference view: Design 1, a previous screenshot, project photo, model measurement, or the specific user screenshot.
3. Add or update relationship tests before implementation where practical. Prefer assertions such as "top wall aligns with Bedroom 2" over isolated magic numbers.
4. Make the minimal implementation change.
5. Run focused tests, full frontend tests, `git diff --check`, and the Svelte build.
6. Render the actual app or generated asset and inspect it visually.
7. Compare against Design 1 or the relevant reference view before finalising.
8. Report what was visually checked in the final response, including any residual uncertainty.

## Visual Checklist

Check the changed area and at least one surrounding area for:

- wall continuity
- wall thickness consistency
- window and door style
- door swing, door opening, and doorway position
- missing wall gaps or unwanted wall gaps
- flooring continuity where walls are removed or rooms combine
- room label placement and duplicate labels
- furniture crossing walls, blocking doors, or sitting off-plan
- furniture layer toggles and label toggles
- dimension labels, sunlight overlays, and other temporary overlays
- zoom/pan behaviour at normal zoom and a high zoom level
- transition animation ordering if a future design is involved
- 3D window transparency, door treatment, wall openings, floor/wall alignment, and photo-viewpoint plausibility

## Project-Specific Views

For 2D scenario work, inspect at minimum:

- Design 1 2D Plan as the baseline
- affected future design 2D Plan at 100 percent
- affected future design with Fixed, Moveable, Furniture Labels, and Room Labels toggled as relevant
- transition start, middle, and end if structural changes or furniture movements are changed

For furniture work, inspect:

- Furniture Editor at 100 percent
- a high zoom level around the selected object
- all relevant layer and label toggle states

For 3D work, inspect:

- default overview
- at least one close viewpoint near the changed area
- relevant project photos when the change is photo-driven

## Final Response Evidence

When finishing a visual change, include a short verification note:

```text
Visual QA: inspected <view/area> against <reference>; checked wall continuity, window/door style, label placement, and adjacent-room effects.
```

If the app cannot be rendered, say that plainly and do not present the visual change as fully verified.
