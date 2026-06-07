# Reference Plan Sunlight Overlay Design

## Purpose

Add an interactive sunlight mode to the Reference Style Plan HTML so the 2D house model can show where direct natural light is likely to enter over a selected time of year and time of day.

This is a planning overlay, not a physically exact daylight simulation. It should use real solar position calculations for Christchurch, New Zealand, combine those angles with the model's recorded compass orientation, and render an understandable 2D light/dark overlay on the existing plan.

## Context

The project already has:

- A current source-of-truth model at `DATA/house_model.json`.
- A Reference Style Plan renderer in `CODE/home_design/reference_plan.py`.
- A Reference Style Plan HTML wrapper in `CODE/home_design/reference_plan_viewer.py`.
- Existing qualitative daylight fields in `DATA/house_model.json`.
- A recorded compass orientation in `DATA/house_model.json`: plan-right is approximately `52.5` degrees clockwise from true north and north points slightly up-right on the straightened plan.

The existing daylight model is room-level and qualitative. The requested feature is more spatial: use sliders to show the sun direction and rough patches of direct light entering through windows and glazed openings.

## User-Approved Scope

The first implementation should be interactive only in the Reference Style Plan HTML.

Controls should sit below the property boundary / in the lower control area, not as a separate app and not as static generated snapshots.

The mode should include:

- A sunlight on/off toggle.
- A horizontal year slider with `16` evenly spaced points across the year.
- A horizontal time-of-day slider from `4:00am` to `10:00pm` in `30` minute steps.
- Year labels that combine Southern Hemisphere season and month.
- A darkened plan when the sun is below the horizon.
- A sun-direction marker around the fringe of the plan.
- Rough light polygons/rays showing where direct sun enters and lands in the house.

## Solar Calculation

Use Christchurch, New Zealand as the location:

- Latitude: approximately `-43.53333`
- Longitude: approximately `172.63333`

NOAA's solar calculator documentation defines solar azimuth as degrees clockwise from north and solar elevation as degrees up from the horizon. That matches the data shape needed for this plan: compute sun azimuth/elevation from local date/time/location, then rotate azimuth into the SVG coordinate system using the recorded plan orientation. NREL's Solar Position Algorithm is the higher-precision reference for a later upgrade.

For the first implementation, a compact JavaScript solar-position formula is acceptable if tests verify that the function exists and the output wiring is deterministic. The feature does not need sub-degree precision.

## Plan Direction Conversion

The model records:

- `orientation.compass.plan_right_bearing_degrees = 52.5`
- `orientation.compass.north_arrow_degrees_clockwise_from_plan_up = 37.5`

Use this to convert world azimuth to plan coordinates.

Solar azimuth describes the direction toward the sun. Direct sunlight entering the house travels in the opposite direction. The overlay should therefore:

1. Compute the sun azimuth from north.
2. Convert that azimuth into SVG x/y direction using the model's compass orientation.
3. Use the reverse vector for light travel from an opening into the plan.

If solar elevation is `<= 0`, mark the plan as no direct natural light and darken the house/site overlay.

## Light Entry Openings

The first implementation should include light through:

- Exterior windows.
- Exterior glazed doors / sliders.
- Sunroom-to-lounge slider.
- Entrance deck slider.
- Interior window between entrance and Bedroom 2.

Use the current structure features from `DATA/house_model.json` and the existing opening centerline logic where possible. The overlay should not infer new openings from room names or labels.

The minimum required entry feature IDs are:

- `sunroom_wraparound_glazing`
- `sunroom_front_double_doors`
- `lounge_north_left_window`
- `lounge_north_right_window`
- `deck_door_group`
- `deck_side_dining_window`
- `dining_west_window`
- `entrance_deck_slider`
- `laundry_north_window`
- `laundry_east_window`
- `toilet_frosted_window`
- `master_street_window`
- `master_rear_high_window`
- `master_sunroom_window`
- `office_se_window`
- `bathroom_se_window`
- `bedroom2_se_window`
- `sunroom_lounge_slider`
- `bedroom2_entrance_internal_window`

If a feature is missing from the model, the renderer should omit it from the sunlight config rather than fail.

## Light Rendering

The overlay should be visually legible on top of the reference plan:

- Add a dark translucent layer when sunlight mode is active.
- Add warm translucent polygons for direct sunlight zones.
- Keep room labels and wall/opening symbols readable.
- Draw a small sun-direction indicator on the plan fringe with the current azimuth/elevation.
- Show a no-direct-light state when the sun is below the horizon.

The first version can approximate light as projected trapezoids or long polygons from each eligible opening. It does not need to clip perfectly against every wall. The important first behaviour is directionally correct light entering from the correct openings.

## Deferred Accuracy Layers

Do not implement blockers in the first pass.

Later versions can add:

- Garage/shed and cottage shadow blockers.
- Hedges/fences and boundary planting.
- Eaves, roof overhangs, pergolas, and awnings.
- Window head heights and sill heights.
- Wall height, ceiling height, and 3D obstruction.
- Room-by-room clipping so light stops at solid internal walls.

The first implementation should keep the data shape open enough to add blockers later as separate geometry, not as hard-coded special cases.

## Data Flow

The Reference Style Plan HTML should embed a compact sunlight config generated from the model:

- Location metadata.
- Orientation metadata.
- Year slider points.
- Time slider bounds and step.
- Eligible opening centerlines and target IDs.
- Floor/room polygons useful for future clipping and visual context.

The browser JavaScript should:

1. Read the embedded config.
2. Listen to the sunlight toggle and both sliders.
3. Compute local date/time from the selected slider positions.
4. Compute solar azimuth/elevation.
5. Convert sun direction into plan coordinates.
6. Update the dark layer, light polygons, direction marker, and status text.

## Error Handling

If sunlight mode is off, the overlay should be hidden and should not change the base plan.

If the sun is below the horizon, the overlay should show the darkened plan and a no-direct-natural-light status.

If orientation metadata is missing, the control should still render but show an unavailable status and avoid drawing misleading rays.

If there are no eligible openings, the control should show a no-openings status and avoid drawing light polygons.

## Testing

Add focused tests around generated HTML rather than browser pixel output in the first pass:

- The Reference Style Plan HTML includes the sunlight toggle and two range sliders.
- The HTML includes embedded sunlight config with Christchurch latitude/longitude and `plan_right_bearing_degrees`.
- The config includes representative exterior and internal light-entry openings.
- The JavaScript includes functions for solar position, azimuth-to-plan conversion, and overlay update.
- The below-horizon branch is present and exposes a no-direct-natural-light status.

Existing tests for reference plan rendering, model validation, and viewer HTML should continue to pass.

## Non-Goals

- No physically exact daylight simulation.
- No static CLI sunlight snapshot output yet.
- No 3D sun/shadow model yet.
- No external blockers yet.
- No generated images.
- No renovation scoring based on daylight yet.

## Approval Gate

After this spec is reviewed, implementation should proceed as a tests-first change to the Reference Style Plan viewer and supporting rendering helpers.
