# Home Design Calibration Report

## Wall Assumptions

- Exterior wall thickness: 0.3m
- Internal wall thickness: 0.14m
- Sunroom frame thickness: 0.1m

## External Anchors

- Long straight side run from master end to laundry/toilet end: 16.1m +/- 0.45m (measured_rough)
- Master bedroom exterior width parallel with street: 4.77m (measured_approx)
- Dining-room outside edge to entrance/laundry edge: 7.12m (measured)
- Laundry/toilet rear jut-out wall: 4.46m (measured)
- Combined external depth across dining/entrance/laundry line: 11.58m +/- 0.15m (derived_measured)

## Sunroom Hand Measurements

- Source: sunroom-dimensions.HEIC
- Long top/front run: 5m (hand_measured)
- Right side run: 4.14m (hand_measured)
- Lower short run: 1.55m (hand_measured)
- Lower short vertical return: 0.71m (hand_measured)
- Angled/inset segment: 1.86m (hand_measured)
- Inset horizontal segment: 1.2m (hand_measured)
- Left side run: 2.15m (hand_measured)
- Hallway/Sunroom inside edge to inside of sunroom NW window: 5.02m (direct_measured)
- Lounge/Sunroom inside edge to inside of sunroom west window: 4.07m (direct_measured)
- Layout status: measured_approx

## Calibrated Pixel Openings

- Source: CODE/Matplotlib-008-House-only-sunroom.py
- Count: 8
- deck_doors: slider at kitchen_dining (visual_reference)
- kitchen_window: window at kitchen_dining (visual_reference)
- sunroom_lounge_slider: slider at sunroom / lounge (visual_reference)
- sunroom_open_gap: opening at sunroom / lounge (visual_reference)
- hallway_to_sunroom_door_gap: door_gap at hallway / sunroom (visual_reference)
- sunroom_right_glazing: window at sunroom (visual_reference)
- sunroom_top_window: window at sunroom (visual_reference)
- sunroom_left_window: window at sunroom (visual_reference)

## Photo Evidence Checks

- sunroom_wraparound_glazing: photo_verified for sunroom_north_fixed_window, sunroom_path_side_fixed_window, sunroom_path_left_fixed_window, sunroom_street_side_fixed_window
  Evidence: Exterior and interior sunroom photos confirm fixed glazing around the sunroom perimeter, separate from the path-facing double doors.
  Photo: OUTPUT/jpeg_photos/From-Outside-front-looking-NE-towards-sunroom.jpg - Exterior front/NE view showing sunroom glazing and roof/eave relationship.
  Photo: OUTPUT/jpeg_photos/From-Outside-front-looking-NW-towards-sunroom.jpg - Exterior close view showing the large front-facing sunroom panes.
  Photo: OUTPUT/jpeg_photos/Inside-Sunroom-Looking-NW.jpg - Interior sunroom view showing the broad front glazing.
- sunroom_front_double_doors: photo_verified for sunroom_front_double_doors
  Evidence: The angled sunroom face that meets the front path is a pair of glazed doors rather than a fixed window panel.
  Photo: OUTPUT/jpeg_photos/From-Outside-front-looking-NE-towards-sunroom.jpg - Exterior front/NE view showing the paired doors on the angled sunroom face and their relationship to the path.
  Photo: OUTPUT/jpeg_photos/From-Outside-front-looking-NW-towards-sunroom.jpg - Exterior close view showing the adjacent fixed panes and the paired front doors.
- sunroom_lounge_slider: photo_verified for sunroom_lounge_slider, sunroom_open_gap
  Evidence: Interior sunroom photo confirms the large sliding/glazed connection from sunroom to lounge.
  Photo: OUTPUT/jpeg_photos/Inside-Sunroom-Looking-NE.jpg - Interior sunroom view looking through the slider into the lounge and dining area.
  Photo: OUTPUT/jpeg_photos/Inside-Sunroom-Looking-NW.jpg - Interior sunroom view showing the side glazing and slider context.
- lounge_photo_context: photo_context_verified for lounge, lounge_north_left_window, lounge_north_right_window, hallway_to_lounge_door, sunroom_lounge_slider
  Evidence: Lounge photos support the north-wall window context, the sliding connection to the sunroom, and the doorway back to the hallway. North-wall window positions use direct user measurements.
  Photo: OUTPUT/jpeg_photos/Inside-Lounge-looking-N.jpg - Lounge view toward the north wall and small window relationship.
  Photo: OUTPUT/jpeg_photos/Inside-Lounge-Looking-NE.jpg - Lounge view giving additional north/east wall context.
  Photo: OUTPUT/jpeg_photos/Inside-Lounge-Looking-SE.jpg - Lounge view confirming the hallway doorway relationship.
- deck_doors_and_kitchen_window: photo_verified for deck_doors, kitchen_window, dining_west_window, entrance_to_kitchen_dining_door
  Evidence: Exterior deck photo confirms the large deck door group and adjacent tall deck-side glazing. Interior kitchen/dining photos confirm this is the kitchen/dining deck-side wall, but the old kitchen_window label is treated as deck-side dining/kitchen glazing. Dining photos also support the measured small west/left-wall dining window. Kitchen-side photos support the narrow hinged door between the kitchen/dining area and entrance.
  Photo: OUTPUT/jpeg_photos/From-Outside-Looking-SW-to-Deck-double-doors.jpg - Exterior deck-side view for checking double-door placement.
  Photo: OUTPUT/jpeg_photos/Inside-Kitchen-Looking-NW-2.jpg - Interior kitchen/dining view showing the deck-side door/window wall.
  Photo: OUTPUT/jpeg_photos/Inside-Dining-Room-looking-N.jpg - Interior dining view giving context for the measured west/left-wall window.
  Photo: OUTPUT/jpeg_photos/Inside-Dining-Room-looking-NW.jpg - Interior dining view giving additional context for the measured north-wall window.
- entrance_laundry_back_entry: photo_verified for entrance, laundry, entrance_deck_slider, entrance_to_kitchen_dining_door, laundry_north_window, laundry_east_window
  Evidence: Entrance/back-entry photos confirm a glazed deck-side entrance leading directly to the laundry, with laundry bench, appliances, sink, the top/north laundry window, the right/east laundry window, and the kitchen/dining door relationship visible.
  Photo: OUTPUT/jpeg_photos/Inside-Entrance-Looking-NE.jpg - Interior entrance view showing deck-side glazing and open connection into laundry.
  Photo: OUTPUT/jpeg_photos/Inside-Entrance-Looking-into-back-entrance-2.jpg - Entrance/back-entry view showing glazed deck-side wall and narrow circulation zone.
  Photo: OUTPUT/jpeg_photos/Inside-Laundry-Looking-NE.jpg - Laundry view showing appliances, bench, sink, and exterior window.
  Photo: OUTPUT/jpeg_photos/Inside-Laundry-Looking-N.jpg - Laundry view showing the wide top/north window over the bench and sink.
  Photo: OUTPUT/jpeg_photos/Inside-Laundry-Looking-NW.jpg - Laundry view giving context for the side-wall window and room depth.
  Photo: OUTPUT/jpeg_photos/From-Deck-Looking-SE-to-laundry.jpg - Exterior deck-side view showing the laundry/entrance wall relationship.
- toilet_laundry_connection: photo_verified for toilet, laundry_to_toilet_door, toilet_frosted_window
  Evidence: Toilet photos confirm a small toilet room connected from the laundry, with frosted exterior window and compact fixture layout.
  Photo: OUTPUT/jpeg_photos/Inside-Laundry-Looking-SW.jpg - Laundry-side view toward the toilet connection.
  Photo: OUTPUT/jpeg_photos/Inside-Toilet-Looking-N.jpg - Toilet interior view showing doorway/frame relationship.
  Photo: OUTPUT/jpeg_photos/Inside-Toilet-Looking-S.jpg - Toilet interior view showing frosted window and fixture location.
  Photo: OUTPUT/jpeg_photos/Inside-Toilet-Looking-SW.jpg - Toilet interior view confirming compact plan and fixture position.
- hallway_spine_and_room_connections: photo_verified for hallway, hallway_to_entrance_laundry, hallway_to_lounge_door, hallway_to_sunroom_old_front_door, hallway_to_kitchen_dining_door, hallway_to_bathroom_sliding_door, hallway_to_master_bedroom_door, hallway_to_office_door
  Evidence: Hallway photos confirm the internal circulation spine from the lounge/office side toward the entrance/laundry end. User measurement confirms the old front door between the hallway and sunroom, opening into the hallway toward the master bedroom. Bathroom photos confirm the sliding bathroom door off the hallway, lounge photos confirm the hinged lounge doorway, kitchen/hall photos confirm the kitchen-side door aligned with the lounge/kitchen divider, office photos confirm the office doorway relationship, and master bedroom photos confirm the master doorway swing into the room.
  Photo: OUTPUT/jpeg_photos/Inside-hallway-looking-NE.jpg - Hallway view showing the bathroom sliding door on the side wall and the room/doorway relationship ahead.
  Photo: OUTPUT/jpeg_photos/Inside-Hallway-Looking-NE-2.jpg - Long hallway view toward the entrance/laundry end, showing the circulation spine and laundry beyond.
  Photo: OUTPUT/jpeg_photos/Inside-Hallway-looking-SW.jpg - Hallway reverse view toward the lounge/office side, confirming the opposite end of the circulation spine.
  Photo: OUTPUT/jpeg_photos/Inside-hallway-looking-SW-2.jpg - Closer reverse hallway view showing door/opening relationships along the hall.
  Photo: OUTPUT/jpeg_photos/Inside-Office-Looking-N.jpg - Office view looking through the office door toward the lounge/hallway relationship.
  Photo: OUTPUT/jpeg_photos/Inside-Bathroom-looking-N.jpg - Bathroom interior view showing the sliding door frame back to the hallway.
  Photo: OUTPUT/jpeg_photos/Inside-Bathroom-Looking-NW.jpg - Bathroom interior view confirming the shower position and sliding door relationship.
- master_bedroom_photo_context: photo_context_verified for master_bedroom, master_bedroom_wardrobe, hallway_to_master_bedroom_door, master_street_window, master_sunroom_window, master_rear_high_window
  Evidence: Master bedroom photos provide current-condition context for the room, its built-in wardrobe on the office-side internal wall, its hallway door, and its three window relationships: street/front side, sunroom side, and the rear high window above the bed headboard. The master bedroom window markers now include user-measured wall offsets.
  Photo: OUTPUT/jpeg_photos/Inside-Master-Bedroom-looking-SW.jpg - Master bedroom view toward the street/front-facing window.
  Photo: OUTPUT/jpeg_photos/Inside-Master-Bedroom-Looking-SW-2.jpg - Second master bedroom view confirming the street/front-facing window relationship.
  Photo: OUTPUT/jpeg_photos/Inside-Master-Bedroom-Looking-NW.jpg - Master bedroom view toward the sunroom-side window relationship.
  Photo: OUTPUT/jpeg_photos/Inside-Master-Bedroom-Looking-N.jpg - Master bedroom view giving additional context for the sunroom-side wall.
  Photo: OUTPUT/jpeg_photos/Inside-Master-Bedroom-Looking-S.jpg - Master bedroom view toward the rear high window above the bed headboard.
  Photo: OUTPUT/jpeg_photos/Inside-Master-Bedroom-Looking-S-2.jpg - Second master bedroom view confirming the rear high-window relationship above the bed headboard.
  Photo: OUTPUT/jpeg_photos/From-Outside-front-looking-SW-towards-road.jpg - Exterior front/street context for the master bedroom frontage.
- office_photo_context: photo_context_verified for office, office_se_window, hallway_to_office_door
  Evidence: Office photos confirm the current room context, hallway connection, and SE-facing window side. Window marker is approximate until offsets are measured.
  Photo: OUTPUT/jpeg_photos/Inside-Office-Looking-N.jpg - Office view back toward the hallway/door relationship.
  Photo: OUTPUT/jpeg_photos/Inside-Office-Looking-SE.jpg - Office view toward the SE-facing window side.
  Photo: OUTPUT/jpeg_photos/Inside-Office-looking-E.jpg - Office view giving additional exterior-window wall context.
  Photo: OUTPUT/jpeg_photos/Inside-Office-Looking-S.jpg - Office reverse view confirming room proportions and wall relationships.
- bathroom_photo_context: photo_context_verified for bathroom, bathroom_se_window, hallway_to_bathroom_sliding_door
  Evidence: Bathroom photos confirm the current room context, sliding door back to the hallway, and SE-facing window side. Window marker is approximate until offsets are measured.
  Photo: OUTPUT/jpeg_photos/Inside-Bathroom-looking-N.jpg - Bathroom view back toward the hallway sliding door.
  Photo: OUTPUT/jpeg_photos/Inside-Bathroom-Looking-NW.jpg - Bathroom view confirming shower/door relationship.
  Photo: OUTPUT/jpeg_photos/Inside-Bathroom-Looking-SE-2.jpg - Bathroom view toward the SE-facing window side.
  Photo: OUTPUT/jpeg_photos/Inside-Bathroom-Looking-SE-3.jpg - Second bathroom SE-facing view confirming window side context.
- bedroom2_photo_context: photo_context_verified for bedroom_2, bedroom2_se_window, bedroom2_entrance_internal_window, kitchen_dining_to_bedroom2_door
  Evidence: Bedroom 2 photos confirm current room context, the NW-side door back to the kitchen/dining edge, the internal window to the entrance wall, and the SE-facing exterior window side. SE window marker is approximate until offsets are measured.
  Photo: OUTPUT/jpeg_photos/Inside-Bedroom-2-Looking-SE.jpg - Bedroom 2 view toward the SE-facing window side.
  Photo: OUTPUT/jpeg_photos/Inside-Bedroom-2-Looking-S.jpg - Bedroom 2 view confirming the exterior/window wall relationship.
  Photo: OUTPUT/jpeg_photos/Inside-Bedroom-2-Looking-NW.jpg - Bedroom 2 reverse view confirming room proportions and opposite wall context.
  Photo: OUTPUT/jpeg_photos/Inside-Bedroom-2-Looking-W.jpg - Bedroom 2 side view giving additional wall relationship context.
- external_site_driveway_garage_deck_rear_garden: photo_verified for property_boundary, upper_side_driveway, front_diagonal_path, sunroom_front_steps, rear_timber_deck, cottage_end_deck, garage_concrete_pad, garage_cottage_side_path, garage_shed, cottage, boundary_hedges_and_fences
  Evidence: Satellite and outside photos confirm the main site topology: street-side driveway along the upper side of the section, a diagonal front path near the sunroom/front lawn, small timber steps outside the angled sunroom double doors, the timber deck outside the kitchen/dining and entrance/laundry side, a small cottage-end deck, the larger concrete area in front of the garage/cottage line, the narrow concrete path along the garage/cottage side, the current side-by-side garage/cottage relationship near the top boundary, and tall boundary hedges/fences that affect shade and privacy. Open grass/lawn remains the default ground context except where hardscape is explicitly mapped. External photos supersede the satellite where the cottage replaced part of the rear garage footprint.
  Photo: OUTPUT/jpeg_photos/From-Outside-front-looking-NE-towards-garage.jpg - Front/driveway view showing the concrete drive, side hedge, sunroom/house edge, and garage beyond.
  Photo: OUTPUT/jpeg_photos/From-Outside-side-looking-SW-down-driveway-3.jpg - Reverse driveway view showing driveway width, side hedge/fence, street relationship, and house frontage.
  Photo: OUTPUT/jpeg_photos/From-Deck-Looking-NE-to-back.jpg - Deck-side view showing hardscape, rear lawn, house side, and rear hedge/fence.
  Photo: OUTPUT/jpeg_photos/From-Outside-Back-looking-NW-to-garage-door.jpg - Garage/shed close view confirming roller-door position and adjacent concrete/fence relationship.
  Photo: OUTPUT/jpeg_photos/From-Outside-Back-Looking-NE-to-back-of-property.jpg - Rear garden view showing lawn, house side, hardscape edge, and tall boundary hedge shadows.
  Photo: OUTPUT/jpeg_photos/From-Outside-Back-of-section-looking-W.jpg - Rear section view showing the current cottage and its relationship to the house, deck-side hardscape, and lawn.
  Photo: OUTPUT/jpeg_photos/From-Outside-Back-of-section-looking-NW-to-back-of-cottage.jpg - Rear section view confirming the cottage as a current-condition element behind/alongside the older garage area.
  Photo: OUTPUT/jpeg_photos/From-Outside-front-looking-NE-towards-sunroom.jpg - Front sunroom view showing the small dark timber steps outside the angled double doors and their relationship to the concrete path.
  Photo: OUTPUT/jpeg_photos/From-Outside-side-looking-S-towards-sunroom.jpg - Side sunroom view showing the timber step edge between the sunroom glazing, lawn, and front concrete path.

## Current Structure

- Status: active_source_of_truth
- Method: Measured dimensions and photo evidence are preferred over historical Matplotlib drawing code. Legacy pixel layers remain available only for visual comparison while the current structure is migrated incrementally.
- Legacy comparison layers: reference_pixel_layout
- Spaces promoted: 11
  Space: sunroom (measured_approx; evidence: sunroom_wraparound_glazing)
  Space: lounge (measured_dimensions_inferred_position; evidence: sunroom_lounge_slider, lounge_photo_context)
  Space: kitchen_dining (measured_dimensions_photo_verified_openings; evidence: deck_doors_and_kitchen_window)
  Space: entrance (measured_dimensions_photo_verified; evidence: entrance_laundry_back_entry)
  Space: laundry (measured_dimensions_photo_verified; evidence: entrance_laundry_back_entry)
  Space: toilet (measured_dimensions_photo_verified; evidence: toilet_laundry_connection)
  Space: hallway (measured_dimensions_photo_verified; evidence: hallway_spine_and_room_connections)
  Space: master_bedroom (measured_dimensions_reference_position_photo_context; evidence: master_bedroom_photo_context)
  Space: office (measured_dimensions_reference_position_photo_context; evidence: office_photo_context, hallway_spine_and_room_connections)
  Space: bathroom (measured_dimensions_reference_position_photo_context; evidence: bathroom_photo_context, hallway_spine_and_room_connections)
  Space: bedroom_2 (measured_dimensions_reference_position_photo_context; evidence: bedroom2_photo_context)
- Built-ins recorded: 1
  Built-in: master_bedroom_wardrobe (built_in_wardrobe; measured_photo_context; evidence: master_bedroom_photo_context, office_photo_context)
- Features promoted: 30
  Feature: sunroom_lounge_slider (slider; photo_verified; evidence: sunroom_lounge_slider)
    Detail: width 3.15m
  Feature: sunroom_wraparound_glazing (window_group; photo_verified; evidence: sunroom_wraparound_glazing)
  Feature: sunroom_front_double_doors (door_group; photo_verified; evidence: sunroom_front_double_doors)
    Detail: swing outward_to_front_path
  Feature: lounge_north_left_window (window; measured_position_photo_context; evidence: lounge_photo_context)
    Detail: width 0.42m; offsets left 0.32m; right corner nub projection 0.47m
  Feature: lounge_north_right_window (window; measured_position_photo_context; evidence: lounge_photo_context)
    Detail: width 0.42m; offsets right 0.32m; right corner nub projection 0.47m
  Feature: deck_door_group (door_group; photo_verified; evidence: deck_doors_and_kitchen_window)
    Detail: width 1.62m; offsets top_right_inside_corner 1.14m, window_above_m 0.57m, wall_between_window_and_doors_m 0.12m
  Feature: deck_side_dining_window (window; measured_position_photo_context; evidence: deck_doors_and_kitchen_window)
    Detail: width 0.57m; offsets top_right_inside_corner 1.14m
  Feature: dining_west_window (window; measured_position_photo_context; evidence: deck_doors_and_kitchen_window)
    Detail: width 0.66m; offsets top_internal_corner 0.32m
  Feature: entrance_deck_slider (slider; photo_verified; evidence: entrance_laundry_back_entry)
    Detail: width 1.47m; offsets left_side_from_entrance_narrowing_corner 0.28m
  Feature: entrance_to_laundry_opening (opening; photo_verified; evidence: entrance_laundry_back_entry)
    Detail: width 0.74m
  Feature: laundry_north_window (window; measured_position_photo_context; evidence: entrance_laundry_back_entry)
    Detail: width 1.38m; offsets top_right_north_corner 0.22m
  Feature: laundry_east_window (window; measured_position_photo_context; evidence: entrance_laundry_back_entry)
    Detail: width 1.1m; offsets top_right_north_corner 0.95m
  Feature: laundry_to_toilet_door (door; photo_verified; evidence: toilet_laundry_connection)
    Detail: width 0.588m
  Feature: toilet_frosted_window (window; measured_position_photo_context; evidence: toilet_laundry_connection)
    Detail: width 0.52m; position centred
  Feature: hallway_to_entrance_laundry (opening; photo_verified; evidence: hallway_spine_and_room_connections)
  Feature: kitchen_dining_to_bedroom2_door (door; photo_verified; evidence: bedroom2_photo_context)
    Detail: width 0.81m
  Feature: entrance_to_kitchen_dining_door (door; photo_verified; evidence: entrance_laundry_back_entry, deck_doors_and_kitchen_window)
    Detail: width 0.73m
  Feature: hallway_to_lounge_door (door; photo_verified; evidence: hallway_spine_and_room_connections)
    Detail: width 0.81m; offsets right_jamb_from_kitchen_hallway_north_corner 1.41m
  Feature: hallway_to_sunroom_old_front_door (door; measured_user_confirmed; evidence: hallway_spine_and_room_connections)
    Detail: width 0.77m; swing opens_into_hallway_towards_master_bedroom
  Feature: hallway_to_kitchen_dining_door (door; photo_verified; evidence: hallway_spine_and_room_connections)
    Detail: width 0.81m
  Feature: hallway_to_bathroom_sliding_door (sliding_door; photo_verified; evidence: hallway_spine_and_room_connections)
    Detail: width 0.62m
  Feature: hallway_to_master_bedroom_door (door; photo_verified; evidence: hallway_spine_and_room_connections, master_bedroom_photo_context)
    Detail: width 0.81m
  Feature: hallway_to_office_door (door; photo_verified; evidence: hallway_spine_and_room_connections)
    Detail: width 0.81m
  Feature: master_street_window (window; measured_position_photo_context; evidence: master_bedroom_photo_context)
    Detail: width 2.15m; offsets top_left_west_corner 1.04m
  Feature: master_sunroom_window (window; measured_position_photo_context; evidence: master_bedroom_photo_context, sunroom_wraparound_glazing)
    Detail: width 2.14m; position centred
  Feature: master_rear_high_window (window; measured_position_photo_context; evidence: master_bedroom_photo_context)
    Detail: offsets left 1.32m, right 1.32m
  Feature: office_se_window (window; measured_position_photo_context; evidence: office_photo_context)
    Detail: width 1.07m; offsets left 0.87m, right 0.87m
  Feature: bathroom_se_window (window; measured_position_photo_context; evidence: bathroom_photo_context)
    Detail: width 1.1m; offsets left 0.27m, right 0.27m
  Feature: bedroom2_se_window (window; measured_position_photo_context; evidence: bedroom2_photo_context)
    Detail: width 2m; position centred
  Feature: bedroom2_entrance_internal_window (window; measured_position_photo_context; evidence: bedroom2_photo_context, entrance_laundry_back_entry)
    Detail: width 0.9m; offsets right 1.02m

## Current Site

- Status: active_site_source_of_truth
- Method: External property elements are migrated from the old Matplotlib-005 site sketch only after cross-checking against outside photos. This layer supports external renovation options and shadow/light reasoning.
- Legacy comparison layers: Matplotlib-005.py
- Site elements promoted: 11
  Site: property_boundary (boundary; dimensioned_from_legacy_site_plan; evidence: external_site_driveway_garage_deck_rear_garden)
  Site: upper_side_driveway (hardscape; satellite_photo_verified_approx; evidence: external_site_driveway_garage_deck_rear_garden)
  Site: front_diagonal_path (hardscape; satellite_photo_verified_approx; evidence: external_site_driveway_garage_deck_rear_garden)
  Site: sunroom_front_steps (deck; photo_verified_approx; evidence: external_site_driveway_garage_deck_rear_garden)
  Site: rear_timber_deck (deck; photo_verified_approx; evidence: external_site_driveway_garage_deck_rear_garden, deck_doors_and_kitchen_window, entrance_laundry_back_entry)
  Site: cottage_end_deck (deck; photo_verified_approx; evidence: external_site_driveway_garage_deck_rear_garden)
  Site: garage_shed (building; photo_verified_approx; evidence: external_site_driveway_garage_deck_rear_garden)
  Site: garage_concrete_pad (hardscape; satellite_photo_verified_approx; evidence: external_site_driveway_garage_deck_rear_garden)
  Site: garage_cottage_side_path (hardscape; photo_verified_approx; evidence: external_site_driveway_garage_deck_rear_garden)
  Site: cottage (building; photo_verified_satellite_outdated; evidence: external_site_driveway_garage_deck_rear_garden)
  Site: boundary_hedges_and_fences (planting; photo_verified_approx; evidence: external_site_driveway_garage_deck_rear_garden)
- Shadow sources promoted: 3
  Shadow source: boundary_hedges_and_fences (vegetation_and_fence; photo_verified_shadow_source; evidence: external_site_driveway_garage_deck_rear_garden)
  Shadow source: garage_shed (outbuilding; photo_verified_shadow_source; evidence: external_site_driveway_garage_deck_rear_garden)
  Shadow source: cottage (accessory_cottage; photo_verified_shadow_source; evidence: external_site_driveway_garage_deck_rear_garden)

## Layout Confidence

- Kitchen / Dining: dimensions measured; layout inferred
- Lounge: dimensions measured; layout inferred
- Sunroom: dimensions partly_measured; layout measured_approx
- Hallway: dimensions measured; layout inferred
- Master Bedroom: dimensions measured; layout inferred
- Office: dimensions measured; layout inferred
- Bathroom: dimensions measured; layout inferred
- Bedroom 2: dimensions measured; layout inferred
- Entrance: dimensions measured; layout inferred
- Laundry: dimensions measured; layout inferred
- Toilet: dimensions measured; layout inferred

## Daylight Coverage

- Kitchen / Dining: 12/12 season/time values (inferred)
- Lounge: 12/12 season/time values (inferred)
- Sunroom: 12/12 season/time values (visual)
- Hallway: 12/12 season/time values (visual)
- Master Bedroom: 12/12 season/time values (inferred)
- Office: 12/12 season/time values (inferred)
- Bathroom: 12/12 season/time values (inferred)
- Bedroom 2: 12/12 season/time values (inferred)
- Entrance: 12/12 season/time values (visual)
- Laundry: 12/12 season/time values (inferred)
- Toilet: 12/12 season/time values (visual)

## Geometry Sanity

- Inferred layout bounds: 15.5m x 10.98m
- Wall-adjusted internal target: 15.5m x 10.98m
- This bound is a drawing/model bound, not yet a verified exterior footprint.
- External anchors should be used to calibrate the next coordinate pass.

## Design Issues

- No second toilet (practical design issue): The current layout has only one toilet, accessed through the laundry. That creates a practical constraint for guests, shared use, and times when the toilet or laundry is occupied.
  Possible solution: Redo the bathroom layout to include a second toilet, subject to checking fixture clearances, plumbing route, waterproofing, ventilation, and whether storage or basin/shower positions need to change.

## Next Measurements

- Sunroom exterior segment lengths, including angled/inset door face.
- Eave overhang on at least one straight wall and one sunroom edge.
- Window positions and widths for the main daylight rooms.
- Garage-to-house distance and driveway/deck hardscape edges.
- A confirmed compass/site north reference for more precise sun-path work.
