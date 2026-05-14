# Home Design Baseline Model Design

## Purpose

Build an accurate current-state model of the house before exploring renovation options. The baseline model should reconcile the room measurements, exterior anchor measurements, wall thickness assumptions, satellite/roof evidence, and photo evidence into one structured source of truth.

The immediate goal is a dependable 2D current floor plan generated from data. Future renovation variants and 3D views should be derived from this same model rather than from hand-tuned drawing code.

Daylight and solar exposure should be included as part of the baseline. Renovation decisions should be able to account for which rooms receive morning, midday, and afternoon light, and how that changes across the four seasons.

## Context

The project currently contains:

- A measurement/source-of-truth brief at `CODE/House-Plan-Brief.md`.
- Many HEIC photos covering the exterior, interior rooms, deck, driveway, garage, sunroom, hallway, and wet areas.
- Satellite and outline reference images:
  - `36-Victors-satelite.png`
  - `House-Outline.png`
  - `House-Outline-Internal-walls.png`
- A sequence of Matplotlib scripts in `CODE/` that manually draw site and house plans.

The existing Matplotlib scripts are useful visual references but are too brittle for renovation exploration. They encode geometry as hand-tuned pixel coordinates and drawing commands. The next system should instead store geometry as measured or inferred data, then render plans from that data.

## Key Modelling Principle

Separate these concepts explicitly:

- Roof/eaves outline: visible from satellite and exterior photos.
- External finished wall line: inferred inward from roof/eaves and constrained by measurements.
- Internal room layout: constrained primarily by measured internal room dimensions.
- Confidence: every geometric item should say whether it is measured, inferred, visual, or unknown.
- Solar/daylight layer: orientation and room exposure should be represented so proposed layouts can be evaluated against natural light, not just geometry.

The satellite image should not be treated as the exact external wall outline because the roof has eaves. The exterior is brick with Rockcote, so exterior wall thickness is materially larger than a light framing assumption.

## Known Measurements And Assumptions

Site:

- Approximate property depth: `53.75m`
- Approximate property width: `16.75m`
- Street/road side is on the left of the plan.
- Property extends rightward/rearward from the street.

Wall assumptions:

- Exterior wall build-up: `0.29m` to `0.30m`; model default should be `0.30m`.
- Internal wall thickness: `0.14m`.
- Sunroom wall/frame should be modelled separately because it is a lighter glazed enclosure. Initial assumption: `0.08m` to `0.12m`, pending measurement.

External anchors:

- Long straight side run from master end to laundry/toilet end: approximately `16.1m`.
- Master bedroom street-facing exterior width: `4.77m`.
- Dining-room outside edge to entrance/laundry edge: `7.12m`.
- Laundry/toilet projection wall: `4.46m`.
- Combined external depth across that line: `11.58m`.

Internal room measurements are recorded in `CODE/House-Plan-Brief.md` and should be copied into the structured model rather than duplicated manually inside rendering code.

## Proposed Files

Create a new `DATA/` directory for source data:

- `DATA/house_model.json`
  - Structured model of site, walls, rooms, openings, reference layers, and confidence levels.

Create a new generated-output directory:

- `OUTPUT/`
  - Generated PNG/SVG/PDF plans.
  - This should not become the source of truth.

Create a new renderer module, exact location to be chosen during implementation:

- Reads `DATA/house_model.json`.
- Produces a clean 2D current-state plan.
- Optionally renders confidence overlays and satellite/roof reference overlays.
- Optionally renders daylight overlays showing likely morning, midday, and afternoon sun exposure.

## Model Shape

The model should contain:

- `units`: metres.
- `orientation`: road/front/rear/deck-side conventions.
- `site`: property dimensions and reference notes.
- `assumptions`: exterior wall thickness, internal wall thickness, sunroom frame thickness.
- `anchors`: measured external dimensions and their descriptions.
- `rooms`: room IDs, names, measured internal dimensions, ceiling heights, adjacency notes, confidence.
- `walls`: exterior and internal wall segments, with thickness and confidence.
- `openings`: doors, sliders, large openings, and windows, with known dimensions where available.
- `reference_layers`: satellite image, outline images, and any traced roof/eaves polygons.
- `daylight`: site orientation, sun path assumptions, room exposure notes, and per-room daylight confidence.

Where exact coordinates are not yet known, the model can use approximate placement but must label it as inferred or visual.

## Daylight And Solar Exposure

The model should include daylight as a decision layer because it will affect future renovation choices. The first implementation does not need a physically perfect lighting simulation, but it should provide a structured, inspectable estimate.

The daylight layer should capture:

- Site orientation from the existing plan convention and photo filenames.
- Which external walls and windows face north, east, south, and west.
- Likely morning, midday, and afternoon exposure per room.
- Seasonal variation across summer, autumn, winter, and spring.
- Shading notes from fences, hedges, garage, neighbouring buildings, eaves, and the sunroom glazing.
- Confidence levels, because some exposure is directly visible from photos while some is inferred.

The initial daylight output should be qualitative, but structured as a matrix:

- `high`, `medium`, or `low` expected daylight by room.
- Seasons: `summer`, `autumn`, `winter`, and `spring`.
- Time bands within each season: `morning`, `midday`, and `afternoon`.
- Optional notes for exceptional cases such as late afternoon glare, winter shade, or summer overheating.
- A short note explaining the main reason, such as "large north-facing glazing", "south-facing window toward fence", or "likely shaded by garage/hedge".

Example room-level daylight shape:

```json
{
  "summer": {
    "morning": "medium",
    "midday": "high",
    "afternoon": "high"
  },
  "autumn": {
    "morning": "medium",
    "midday": "medium",
    "afternoon": "medium"
  },
  "winter": {
    "morning": "low",
    "midday": "medium",
    "afternoon": "low"
  },
  "spring": {
    "morning": "medium",
    "midday": "high",
    "afternoon": "medium"
  }
}
```

Later, once the baseline geometry is stable, this can become more quantitative:

- Sun-path overlays by season and time band.
- Approximate shadow casting from eaves, garage, fences, hedges, and neighbouring structures.
- Comparison scoring for renovation options based on daylight gain or loss.

## Rendering Requirements

The first renderer should generate a 2D baseline plan with:

- External wall outline.
- Internal walls.
- Room labels.
- Key dimensions.
- Distinct styling for measured vs inferred geometry.
- Optional roof/eaves layer if available.
- Optional confidence overlay.
- Optional daylight overlay showing room exposure categories by selected season and time band.

The renderer should be deterministic: changing the model changes the plan; manual drawing tweaks should be avoided unless they become model data.

## Validation Requirements

The first generated baseline should be checked against these constraints:

- The long side run should reconcile with the measured `16.1m` external anchor.
- The combined external depth line should reconcile with `11.58m`.
- The master street-facing external width should reconcile with `4.77m`.
- Interior room dimensions should remain true to the brief.
- Exterior wall thickness should use `0.30m` unless a specific segment proves different.
- Internal wall thickness should use `0.14m`.
- The sunroom should remain explicitly lower-confidence until its external geometry is better measured.
- Daylight classifications should be traceable to room orientation, window positions, and photo evidence rather than treated as decoration.

Mismatches should be fixed in `DATA/house_model.json`, not by hand-adjusting the output drawing.

## Future Path

After the baseline 2D plan is coherent:

1. Add alternative design files such as `DATA/design_options/option-a.json`.
2. Add comparison rendering for current vs proposed.
3. Add basic editing in a browser app.
4. Add scoring or annotations for renovation difficulty, retained plumbing, daylight, circulation, and cost risk.
5. Extrude the stable 2D model into a simple 3D model with wall heights, openings, and room volumes.

Generated future-layout images should use the model as reference. They should not be used as the authority for actual dimensions or structure.

## Non-Goals For The First Implementation

- No full 3D walkthrough yet.
- No AI-generated renovation imagery yet.
- No automated architectural compliance checking.
- No structural engineering conclusions.
- No physically exact daylight simulation in the first implementation.
- No invented furniture or decorative details unless needed for scale.
- No direct replacement of the current Matplotlib history until the baseline renderer is producing useful output.

## Open Questions

- Exact sunroom exterior segment lengths and wall/frame thickness.
- Exact eave overhangs on each side.
- Exact window and door positions for many rooms.
- Exact garage placement relative to the main house.
- Exact latitude/longitude or confirmed address for precise sun-path calculations.
- Exact representative dates for `summer`, `autumn`, `winter`, and `spring` daylight snapshots.
- Whether the final interactive app should be Python-backed, TypeScript-only, or a hybrid.

## Approval Gate

Before implementation, review this design and confirm that the first coding step should be:

1. Create `DATA/house_model.json` from the known measurements and assumptions.
2. Build a deterministic 2D renderer from that model.
3. Add qualitative daylight/exposure fields for each room.
4. Generate and inspect the first baseline current-state plan with optional daylight overlay.
