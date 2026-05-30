import unittest

from CODE.home_design.model import load_model
from CODE.home_design.reference_plan import (
    EXTERIOR_WALL_STROKE_PX,
    INTERIOR_WALL_STROKE_PX,
    REFERENCE_PX_PER_M,
    THIN_EXTERIOR_WALL_STROKE_PX,
    THIN_INTERIOR_WALL_STROKE_PX,
    TOILET_EXTERIOR_WALL_STROKE_PX,
    render_reference_plan_svg,
)


class ReferencePlanRenderTests(unittest.TestCase):
    def test_reference_plan_uses_layered_rendering_style(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('data-render-style="reference-plan"', svg)
        self.assertIn('id="reference-floor-layer"', svg)
        self.assertIn('id="reference-built-in-layer"', svg)
        self.assertIn('id="reference-passage-layer"', svg)
        self.assertIn('id="reference-wall-layer"', svg)
        self.assertIn('id="reference-opening-layer"', svg)
        self.assertIn('id="reference-label-layer"', svg)
        self.assertLess(svg.index('id="reference-floor-layer"'), svg.index('id="reference-built-in-layer"'))
        self.assertLess(svg.index('id="reference-built-in-layer"'), svg.index('id="reference-passage-layer"'))
        self.assertLess(svg.index('id="reference-passage-layer"'), svg.index('id="reference-wall-layer"'))
        self.assertLess(svg.index('id="reference-wall-layer"'), svg.index('id="reference-opening-layer"'))
        self.assertIn('data-ref-wall-class="exterior"', svg)
        self.assertIn('data-ref-wall-class="interior"', svg)
        self.assertIn(".wall-core, .wall-reference { fill: none; stroke-linecap: butt; stroke-linejoin: miter; }", svg)
        self.assertIn('.wall-core.exterior { stroke: #585b63; stroke-width: 8px;', svg)
        self.assertIn('.wall-core.interior { stroke: #585b63; stroke-width: 3.7px;', svg)
        self.assertNotIn("stroke-linecap: square", svg)
        self.assertNotIn('data-ref-wall-body="continuous"', svg)
        self.assertIn('id="wall-reference-layer"', svg)
        self.assertNotIn('id="wall-shadow-layer"', svg)
        self.assertNotIn('class="wall-shadow', svg)
        self.assertNotIn('filter: url(#raised-wall-shadow)', svg)
        self.assertNotIn('stroke: url(#wall-top-light)', svg)
        self.assertNotIn('class="wall-top', svg)

    def test_reference_plan_renders_master_bedroom_wardrobe_as_built_in(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('.ref-built-in.wardrobe { fill: #d9c39f;', svg)
        self.assertIn(
            'class="ref-built-in wardrobe" data-ref-built-in="master_bedroom_wardrobe" '
            'x="627.1" y="523.0" width="19.7" height="78.8"',
            svg,
        )
        self.assertNotIn('data-ref-built-in-lines="master_bedroom_wardrobe"', svg)
        self.assertIn(
            '<g class="ref-sliding-door" data-ref-sliding-door="master_bedroom_wardrobe:upper">',
            svg,
        )
        self.assertIn(
            'class="ref-sliding-door-panel sliding" data-ref-sliding-door-panel="master_bedroom_wardrobe:upper:sliding" '
            'x="626.9" y="527.0" width="1.8" height="20.7"',
            svg,
        )
        self.assertIn(
            'class="ref-sliding-door-panel fixed" data-ref-sliding-door-panel="master_bedroom_wardrobe:upper:fixed" '
            'x="628.7" y="541.1" width="1.8" height="16.8"',
            svg,
        )
        self.assertIn(
            '<g class="ref-sliding-door" data-ref-sliding-door="master_bedroom_wardrobe:lower">',
            svg,
        )
        self.assertIn(
            'class="ref-sliding-door-panel sliding" data-ref-sliding-door-panel="master_bedroom_wardrobe:lower:sliding" '
            'x="626.9" y="566.9" width="1.8" height="20.7"',
            svg,
        )
        self.assertIn(
            'class="ref-sliding-door-panel fixed" data-ref-sliding-door-panel="master_bedroom_wardrobe:lower:fixed" '
            'x="628.7" y="581.0" width="1.8" height="16.8"',
            svg,
        )
        self.assertIn(
            'class="ref-built-in-wardrobe-divider" data-ref-built-in-divider="master_bedroom_wardrobe" '
            'x="627.1" y="560.4" width="19.7" height="4.0"',
            svg,
        )
        self.assertIn(
            'data-ref-wall="master_office_wall" data-ref-wall-class="thin-interior" '
            'data-wall-thickness-m="0.125" '
            'd="M627.1 482.4 V494 M627.1 516 V527 M627.1 558 V567 M627.1 598 V601.8"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall="master_office_wall" data-ref-wall-class="interior" d="M608 485 V494 M608 516 V610"',
            svg,
        )

    def test_reference_plan_private_room_bottom_wall_matches_remeasured_depth(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        row_top_wall_y = 523.3
        row_bottom_wall_y = 601.8
        clear_depth_m = (
            row_bottom_wall_y
            - EXTERIOR_WALL_STROKE_PX / 2
            - row_top_wall_y
            - THIN_INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        bedroom2_clear_length_m = (
            902.8
            - INTERIOR_WALL_STROKE_PX / 2
            - 773.9
            - THIN_INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        bathroom_clear_width_m = (
            773.9
            - THIN_INTERIOR_WALL_STROKE_PX / 2
            - 727.1
            - THIN_INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        office_clear_width_m = (
            727.1
            - THIN_INTERIOR_WALL_STROKE_PX / 2
            - 646.8
            - THIN_INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        wardrobe_clear_width_m = (
            646.8
            - THIN_INTERIOR_WALL_STROKE_PX / 2
            - 627.1
            - THIN_INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        master_clear_width_m = (
            627.1
            - THIN_INTERIOR_WALL_STROKE_PX / 2
            - 533.9
            - EXTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        master_clear_depth_m = (
            601.8
            - EXTERIOR_WALL_STROKE_PX / 2
            - 482.4
            - EXTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        main_hallway_clear_width_m = (
            523
            - INTERIOR_WALL_STROKE_PX / 2
            - 484.6
            - INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        lounge_clear_width_m = (
            760.9
            - INTERIOR_WALL_STROKE_PX / 2
            - 659.1
            - INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        lounge_clear_depth_m = (
            484.6
            - INTERIOR_WALL_STROKE_PX / 2
            - 348.8
            - EXTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        kitchen_main_clear_width_m = (
            833.0
            - EXTERIOR_WALL_STROKE_PX / 2
            - 760.9
            - INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        kitchen_dining_clear_length_m = (
            523.3
            - THIN_INTERIOR_WALL_STROKE_PX / 2
            - 302.3
            - EXTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        bedroom2_door_left_x = 778.6
        kitchen_hall_wall_right_face_x = 760.9 + INTERIOR_WALL_STROKE_PX / 2
        bedroom2_to_kitchen_wall_m = (
            bedroom2_door_left_x - kitchen_hall_wall_right_face_x
        ) / REFERENCE_PX_PER_M

        self.assertAlmostEqual(clear_depth_m, 2.75, places=2)
        self.assertAlmostEqual(bedroom2_clear_length_m, 4.73, places=2)
        self.assertAlmostEqual(bathroom_clear_width_m, 1.64, places=2)
        self.assertAlmostEqual(office_clear_width_m, 2.90, places=2)
        self.assertAlmostEqual(wardrobe_clear_width_m, 0.62, places=2)
        self.assertAlmostEqual(master_clear_width_m, 3.30, places=2)
        self.assertAlmostEqual(master_clear_depth_m, 4.20, places=2)
        self.assertAlmostEqual(main_hallway_clear_width_m, 1.31, places=2)
        self.assertAlmostEqual(lounge_clear_width_m, 3.70, places=2)
        self.assertAlmostEqual(lounge_clear_depth_m, 4.90, places=2)
        self.assertAlmostEqual(kitchen_main_clear_width_m, 2.50, places=2)
        self.assertAlmostEqual(kitchen_dining_clear_length_m, 8.12, places=2)
        self.assertAlmostEqual(bedroom2_to_kitchen_wall_m, 0.60, places=2)
        self.assertIn('data-ref-wall="lounge_exterior" data-ref-wall-class="exterior" d="M659.1 348.8 H762.8"', svg)
        self.assertIn('class="ref-floor carpet" data-ref-room="office" x="646.8" y="523.0" width="80.3" height="78.8"', svg)
        self.assertIn('class="ref-floor tile" data-ref-room="bathroom" x="727.1" y="523.0" width="46.8" height="78.8"', svg)
        self.assertIn('class="ref-floor carpet" data-ref-room="bedroom_2" x="773.9" y="523.0" width="128.9" height="78.8"', svg)
        self.assertIn('class="ref-floor carpet" data-ref-room="master_bedroom" x="533.9" y="482.4" width="93.2" height="119.4"', svg)
        self.assertIn('class="ref-floor carpet" data-ref-room="hallway" points="627.1,482.4 760.9,482.4 760.9,523.0 627.1,523.0"', svg)
        self.assertIn('class="ref-floor vinyl-plank" data-ref-room="toilet" x="902.8" y="572.9" width="53.6" height="29.3"', svg)
        self.assertIn(
            'class="wall-core exterior structural" data-ref-wall-class="exterior" '
            'd="M659.1 348.8 H762.8 M663.1 348.8 V377.8 M663.1 460 V484.6 M758.8 348.8 V302.3 H833 V491.9 M956.4 487.3 V602.2 M902.8 601.8 H533.9 V482.4 H635.2 M655.4 482.4 H663.1"',
            svg,
        )
        self.assertNotIn('class="wall-core trimmed-exterior structural"', svg)
        self.assertIn(
            'data-ref-wall="private_rooms_south_wall" data-ref-wall-class="exterior" d="M533.9 601.8 H902.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window="office_se_window" data-window-context="exterior" '
            'x1="701.1" y1="601.8" x2="672.8" y2="601.8"',
            svg,
        )
        self.assertNotIn('data-ref-wall="private_rooms_south_wall" data-ref-wall-class="exterior" d="M518 610 H956.4"', svg)

    def test_reference_plan_uses_125mm_partition_stack_without_changing_room_clearances(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        selected_wall_thickness_px = THIN_INTERIOR_WALL_STROKE_PX
        bedroom2_clear_length_m = (
            902.8
            - INTERIOR_WALL_STROKE_PX / 2
            - 773.9
            - selected_wall_thickness_px / 2
        ) / REFERENCE_PX_PER_M
        bathroom_clear_width_m = (
            773.9
            - selected_wall_thickness_px / 2
            - 727.1
            - selected_wall_thickness_px / 2
        ) / REFERENCE_PX_PER_M
        office_clear_width_m = (
            727.1
            - selected_wall_thickness_px / 2
            - 646.8
            - selected_wall_thickness_px / 2
        ) / REFERENCE_PX_PER_M
        wardrobe_clear_width_m = (
            646.8
            - selected_wall_thickness_px / 2
            - 627.1
            - selected_wall_thickness_px / 2
        ) / REFERENCE_PX_PER_M
        master_clear_width_m = (
            627.1
            - selected_wall_thickness_px / 2
            - 533.9
            - EXTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        hallway_clear_length_m = (
            760.9
            - INTERIOR_WALL_STROKE_PX / 2
            - 627.1
            - EXTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M

        self.assertAlmostEqual(bedroom2_clear_length_m, 4.73, places=2)
        self.assertAlmostEqual(bathroom_clear_width_m, 1.64, places=2)
        self.assertAlmostEqual(office_clear_width_m, 2.90, places=2)
        self.assertAlmostEqual(wardrobe_clear_width_m, 0.62, places=2)
        self.assertAlmostEqual(master_clear_width_m, 3.30, places=2)
        self.assertAlmostEqual(hallway_clear_length_m, 4.82, places=2)
        for wall_id in [
            "master_office_wall",
            "wardrobe_office_wall",
            "office_bathroom_wall",
            "bathroom_bedroom2_wall",
        ]:
            self.assertIn(
                f'data-ref-wall="{wall_id}" data-ref-wall-class="thin-interior" '
                'data-wall-thickness-m="0.125"',
                svg,
            )

    def test_reference_plan_toilet_depth_uses_thin_bottom_external_strip(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        laundry_toilet_left_wall_x = 902.8
        laundry_toilet_right_wall_x = 956.4
        entrance_top_wall_y = 489.1
        entrance_bedroom2_wall_y = 523.3
        toilet_top_wall_y = 572.9
        toilet_bottom_wall_y = 602.2
        bedroom2_bottom_wall_outer_edge_y = 601.8 + EXTERIOR_WALL_STROKE_PX / 2
        toilet_wall_outer_edge_y = toilet_bottom_wall_y + TOILET_EXTERIOR_WALL_STROKE_PX / 2
        clear_width_m = (
            laundry_toilet_right_wall_x
            - EXTERIOR_WALL_STROKE_PX / 2
            - laundry_toilet_left_wall_x
            - INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        entrance_clear_depth_m = (
            entrance_bedroom2_wall_y
            - THIN_INTERIOR_WALL_STROKE_PX / 2
            - entrance_top_wall_y
            - THIN_EXTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        laundry_clear_depth_m = (
            toilet_top_wall_y
            - THIN_INTERIOR_WALL_STROKE_PX / 2
            - entrance_top_wall_y
            - THIN_EXTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        entrance_laundry_opening_start_y = 496.5
        entrance_laundry_opening_end_y = 516.1
        entrance_laundry_top_nub_m = (
            entrance_laundry_opening_start_y
            - entrance_top_wall_y
            - THIN_EXTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M
        entrance_laundry_opening_m = (
            entrance_laundry_opening_end_y - entrance_laundry_opening_start_y
        ) / REFERENCE_PX_PER_M
        entrance_laundry_bottom_nub_m = (
            entrance_bedroom2_wall_y
            - THIN_INTERIOR_WALL_STROKE_PX / 2
            - entrance_laundry_opening_end_y
        ) / REFERENCE_PX_PER_M
        clear_depth_m = (
            toilet_bottom_wall_y
            - TOILET_EXTERIOR_WALL_STROKE_PX / 2
            - toilet_top_wall_y
            - THIN_INTERIOR_WALL_STROKE_PX / 2
        ) / REFERENCE_PX_PER_M

        self.assertAlmostEqual(clear_width_m, 1.80, places=2)
        self.assertAlmostEqual(entrance_clear_depth_m, 1.16, places=2)
        self.assertAlmostEqual(laundry_clear_depth_m, 3.03, places=2)
        self.assertAlmostEqual(entrance_laundry_top_nub_m, 0.21, places=2)
        self.assertAlmostEqual(entrance_laundry_opening_m, 0.74, places=2)
        self.assertAlmostEqual(entrance_laundry_bottom_nub_m, 0.21, places=2)
        self.assertAlmostEqual(toilet_wall_outer_edge_y, bedroom2_bottom_wall_outer_edge_y, delta=0.1)
        self.assertAlmostEqual(clear_depth_m, 0.91, places=2)
        self.assertIn('class="ref-floor vinyl-plank" data-ref-room="toilet" x="902.8" y="572.9" width="53.6" height="29.3"', svg)
        self.assertIn('class="ref-floor vinyl-plank" data-ref-room="laundry" x="902.8" y="489.1" width="53.6" height="83.8"', svg)
        self.assertIn(
            'data-ref-wall="private_rooms_south_wall" data-ref-wall-class="exterior" d="M533.9 601.8 H902.8"',
            svg,
        )
        self.assertIn(
            'data-ref-wall="toilet_south_external_wall" data-ref-wall-class="toilet-exterior" '
            'data-wall-thickness-m="0.27" d="M900.6 602.2 H960.4"',
            svg,
        )
        self.assertIn('data-ref-wall="bedroom2_east_wall" data-ref-wall-class="interior" d="M902.8 516.1 V602.2"', svg)
        self.assertIn('data-ref-wall="laundry_toilet_exterior" data-ref-wall-class="exterior" d="M956.4 487.3 V602.2"', svg)
        self.assertIn(
            'data-ref-passage="entrance_to_laundry_opening" points="899.8,496.5 905.8,496.5 905.8,516.1 899.8,516.1"',
            svg,
        )
        self.assertNotIn('data-ref-wall-junction="laundry_top_right_square_corner"', svg)
        self.assertNotIn('data-ref-wall="private_rooms_south_wall" data-ref-wall-class="exterior" d="M518 601.8 H956.4"', svg)

    def test_reference_plan_renders_openings_as_cutouts_not_colored_markers(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('class="opening-cutout exterior timber threshold"', svg)
        self.assertIn('class="opening-cutout exterior deck threshold"', svg)
        self.assertIn('.opening-cutout.exterior { stroke-width: 9px;', svg)
        self.assertIn('.opening-cutout.interior { stroke-width: 5px;', svg)
        self.assertIn('.opening-cutout.timber { stroke: url(#vinyl-planks-vertical); }', svg)
        self.assertIn('.opening-cutout.deck { stroke: url(#deck-boards-subtle); }', svg)
        self.assertIn('.opening-cutout.threshold { stroke-width: 7px; }', svg)
        self.assertIn('class="ref-window-cutout exterior"', svg)
        self.assertIn('class="ref-window-cutout internal"', svg)
        self.assertIn('.ref-window-cutout.exterior { stroke-width: 8px;', svg)
        self.assertIn(
            '.ref-window-cutout.exterior[data-ref-window="laundry_north_window"] { stroke-width: 2px;',
            svg,
        )
        self.assertIn('.ref-window-cutout.internal { stroke-width: 4px;', svg)
        self.assertIn('.ref-sliding-door-panel { fill: #fffdf8; stroke: #111; stroke-width: 0.45; }', svg)
        self.assertIn('.ref-door-leaf { fill: none; stroke: #111; stroke-width: 1.4; stroke-linecap: round; }', svg)
        self.assertIn('.ref-door-arc { fill: none; stroke: #111; stroke-width: 1.1; stroke-dasharray: 4 4; stroke-linecap: round; }', svg)
        self.assertIn('.ref-door-leaf.photo-reference { stroke: #111; stroke-width: 1.8; stroke-linecap: butt; }', svg)
        self.assertIn('.ref-door-arc.photo-reference { stroke: #111; stroke-width: 0.95; }', svg)
        self.assertNotIn('.ref-door-leaf { fill: none; stroke: #575b60;', svg)
        self.assertNotIn('.ref-door-arc.photo-reference { stroke: #6f7478;', svg)
        self.assertNotIn('.ref-door-leaf { fill: none; stroke: #111; stroke-width: 1.4; stroke-linecap: round; stroke-dasharray:', svg)
        self.assertIn('.ref-pocket-door-panel { fill: #fffdf8; stroke: #2f3134; stroke-width: 0.45; }', svg)
        self.assertIn('.ref-pocket-door-casing { fill: #2f3134; stroke: none; }', svg)
        self.assertIn('.ref-pocket-door-slot { fill: #fffdf8; stroke: none; }', svg)
        self.assertIn('class="ref-window-guide"', svg)
        self.assertIn('data-window-context="exterior"', svg)
        self.assertIn('data-window-context="internal"', svg)
        self.assertIn('data-ref-window="sunroom_wraparound_glazing" data-window-context="internal"', svg)
        self.assertNotIn('data-ref-window="sunroom_wraparound_glazing" data-window-context="exterior"', svg)

    def test_reference_plan_wall_strokes_follow_measured_wall_thickness(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('.wall-core.exterior { stroke: #585b63; stroke-width: 8px; }', svg)
        self.assertIn('.wall-core.interior { stroke: #585b63; stroke-width: 3.7px; }', svg)
        self.assertIn('.wall-core.thin-exterior { stroke: #585b63; stroke-width: 3.7px; }', svg)
        self.assertIn('.wall-core.trimmed-exterior { stroke: #585b63; stroke-width: 6px; }', svg)
        self.assertIn('.wall-core.toilet-exterior { stroke: #585b63; stroke-width: 7.2px; }', svg)
        self.assertIn('.wall-core.thin-interior { stroke: #585b63; stroke-width: 3.3px; }', svg)
        self.assertNotIn('.wall-core.exterior { stroke: #585b63; stroke-width: 12px; }', svg)
        self.assertIn(
            'data-ref-window="deck_side_dining_window" data-window-context="exterior" '
            'x1="833.0" y1="332.5" x2="833.0" y2="347.7"',
            svg,
        )
        self.assertIn(
            'data-ref-window="master_street_window" data-window-context="exterior" '
            'x1="534.9" y1="514.0" x2="534.9" y2="571.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window="lounge_north_left_window" data-window-context="exterior" '
            'x1="675.8" y1="348.8" x2="687.2" y2="348.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="lounge_north_left_window" data-window-context="exterior" '
            'x1="675.8" y1="346.8" x2="687.2" y2="346.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window="lounge_north_right_window" data-window-context="exterior" '
            'x1="742.7" y1="348.8" x2="731.3" y2="348.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="lounge_north_right_window" data-window-context="exterior" '
            'x1="742.7" y1="350.8" x2="731.3" y2="350.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window="dining_west_window" data-window-context="exterior" '
            'x1="758.8" y1="316.8" x2="758.8" y2="334.3"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="dining_west_window" data-window-context="exterior" '
            'x1="760.8" y1="316.8" x2="760.8" y2="334.3"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="dining_west_window" data-window-context="exterior" '
            'x1="756.8" y1="316.8" x2="756.8" y2="334.3"',
            svg,
        )
        self.assertIn(
            'data-ref-wall="lounge_sunroom_wall" data-ref-wall-class="exterior" '
            'd="M663.1 348.8 V377.8"',
            svg,
        )
        self.assertIn(
            'data-ref-wall="lounge_sunroom_lower_wall_trim" data-ref-wall-class="exterior" '
            'd="M663.1 460 V484.6"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall="lounge_sunroom_lower_wall_trim" data-ref-wall-class="exterior" '
            'd="M663.1 460 V482.4"',
            svg,
        )
        self.assertIn(
            'data-ref-wall-junction="sunroom_lounge_upper_wall_fill" '
            'x="659.1" y="344.8" width="8.0" height="8.0"',
            svg,
        )
        self.assertIn(
            'data-ref-wall-junction="sunroom_lounge_lower_wall_fill" '
            'x="659.1" y="460.0" width="8.0" height="24.6"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall-junction="sunroom_lounge_lower_wall_fill" '
            'x="659.1" y="460.0" width="8.0" height="22.4"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall-junction="sunroom_lounge_lower_wall_fill" '
            'x="660.1" y="460.0" width="6.0" height="22.4"',
            svg,
        )
        self.assertNotIn('data-ref-wall-junction="lounge_north_wall_left_underside_fill"', svg)
        self.assertNotIn(
            'data-ref-wall-junction="sunroom_lounge_upper_wall_fill" '
            'x="655.1" y="348.8" width="8.0" height="29.0"',
            svg,
        )
        self.assertNotIn('data-ref-wall="lounge_exterior" data-ref-wall-class="exterior" d="M655.1 348.8 H762.8"', svg)
        self.assertNotIn('data-ref-wall="lounge_exterior" data-ref-wall-class="exterior" d="M657.2 348.8 H762.8"', svg)
        self.assertNotIn(
            'data-ref-wall-junction="sunroom_lounge_upper_wall_fill" '
            'x="655.1" y="344.8" width="20.7" height="33.0"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall="lounge_sunroom_wall" data-ref-wall-class="exterior" '
            'd="M659.1 348.8 V377.8 M659.1 460 V482.4"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall="lounge_sunroom_wall" data-ref-wall-class="exterior" '
            'd="M663.1 348.8 V377.8 M659.1 460 V482.4"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall-junction="sunroom_lounge_upper_wall_fill" '
            'x="659.1" y="344.8" width="16.7" height="33.0"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall-junction="sunroom_lounge_upper_wall_fill" '
            'x="657.2" y="348.8" width="9.9" height="29.0"',
            svg,
        )
        self.assertNotIn(
            'class="wall-core exterior structural" data-ref-wall-class="exterior" '
            'd="M659.1 348.8 H762.8 M758.8 348.8 V302.3 H833 V491.9 M956.4 487.3 V602.2 M902.8 601.8 H532.4 V482.4 H634 M654.4 482.4 H667.1"',
            svg,
        )
        self.assertNotIn('data-ref-wall="lounge_sunroom_wall" data-ref-wall-class="interior"', svg)
        self.assertIn(
            'data-ref-window-guide="master_street_window" data-window-context="exterior" '
            'x1="536.9" y1="514.0" x2="536.9" y2="571.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="master_street_window" data-window-context="exterior" '
            'x1="532.9" y1="514.0" x2="532.9" y2="571.0"',
            svg,
        )
        self.assertNotIn(
            'data-ref-window="master_street_window" data-window-context="exterior" '
            'x1="518.0" y1="513.8" x2="518.0" y2="581.2"',
            svg,
        )
        self.assertNotIn(
            'data-ref-window="master_street_window" data-window-context="exterior" '
            'x1="518.0" y1="528.0" x2="518.0" y2="588.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window="master_rear_high_window" data-window-context="exterior" '
            'x1="589.6" y1="601.8" x2="571.4" y2="601.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="master_rear_high_window" data-window-context="exterior" '
            'x1="589.6" y1="603.8" x2="571.4" y2="603.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="master_rear_high_window" data-window-context="exterior" '
            'x1="589.6" y1="599.8" x2="571.4" y2="599.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window="office_se_window" data-window-context="exterior" '
            'x1="701.1" y1="601.8" x2="672.8" y2="601.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window="bathroom_se_window" data-window-context="exterior" '
            'x1="765.1" y1="601.8" x2="735.9" y2="601.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window="bedroom2_se_window" data-window-context="exterior" '
            'x1="864.8" y1="601.8" x2="811.7" y2="601.8"',
            svg,
        )
        self.assertIn(
            'data-ref-window="bedroom2_entrance_internal_window" data-window-context="internal" '
            'x1="878.7" y1="523.3" x2="854.4" y2="523.3"',
            svg,
        )
        self.assertNotIn('data-ref-window-guide="bedroom2_entrance_internal_window"', svg)
        self.assertIn(
            'data-ref-window="toilet_frosted_window" data-window-context="exterior" '
            'x1="956.4" y1="580.7" x2="956.4" y2="594.4"',
            svg,
        )
        self.assertNotIn('x1="940.0" y1="586.0" x2="940.0" y2="606.0"', svg)
        self.assertIn(
            'data-ref-window="laundry_north_window" data-window-context="exterior" '
            'x1="914.0" y1="489.1" x2="950.6" y2="489.1"',
            svg,
        )
        self.assertNotIn('data-ref-window-guide="laundry_north_window"', svg)
        self.assertIn(
            'data-ref-window="laundry_east_window" data-window-context="exterior" '
            'x1="956.4" y1="514.3" x2="956.4" y2="543.5"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="laundry_east_window" data-window-context="exterior" '
            'x1="958.4" y1="514.3" x2="958.4" y2="543.5"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="laundry_east_window" data-window-context="exterior" '
            'x1="954.4" y1="514.3" x2="954.4" y2="543.5"',
            svg,
        )
        for expected_sunroom_window in [
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="610.0" y1="346.7" x2="655.2" y2="346.7"',
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="606.0" y1="354.7" x2="606.0" y2="393.6"',
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="556.0" y1="442.3" x2="568.0" y2="442.3"',
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="549.2" y1="446.3" x2="549.2" y2="473.5"',
        ]:
            self.assertIn(expected_sunroom_window, svg)
        self.assertNotIn(
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="549.2" y1="442.3" x2="568.0" y2="442.3"',
            svg,
        )
        self.assertNotIn(
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="549.2" y1="446.3" x2="549.2" y2="477.9"',
            svg,
        )
        lounge_sunroom_inside_x = 663.1 - EXTERIOR_WALL_STROKE_PX / 2
        west_window_inside_x = 549.2 + 2.0
        self.assertAlmostEqual((lounge_sunroom_inside_x - west_window_inside_x) / REFERENCE_PX_PER_M, 4.07, places=2)
        lounge_external_wall_y = 348.8
        sunroom_top_wall_y = 346.7
        self.assertAlmostEqual(
            sunroom_top_wall_y - INTERIOR_WALL_STROKE_PX / 2,
            lounge_external_wall_y - EXTERIOR_WALL_STROKE_PX / 2,
            places=1,
        )
        self.assertNotIn(
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="606.0" y1="357.4" x2="659.1" y2="357.4"',
            svg,
        )
        self.assertNotIn(
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="536.0" y1="458.0" x2="536.0" y2="482.0"',
            svg,
        )
        self.assertNotIn(
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="606.0" y1="357.4" x2="655.2" y2="357.4"',
            svg,
        )
        self.assertNotIn(
            'data-ref-window="sunroom_wraparound_glazing" data-window-context="internal" '
            'x1="593.0" y1="413.0" x2="555.0" y2="449.0"',
            svg,
        )
        self.assertIn('data-ref-opening="sunroom_front_double_doors"', svg)
        self.assertNotIn('data-ref-opening-cutout="sunroom_front_double_doors"', svg)
        self.assertIn(
            'class="ref-door-leaf double-door" data-ref-door-leaf="sunroom_front_double_doors:upper" '
            'd="M 606.0 401.6 L 585.6 382.6"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf double-door" data-ref-door-leaf="sunroom_front_double_doors:lower" '
            'd="M 568.0 442.3 L 547.6 423.3"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc double-door" data-ref-door-arc="sunroom_front_double_doors:upper" '
            'd="M 585.6 382.6 A 27.8 27.8 0 0 0 587.0 422.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc double-door" data-ref-door-arc="sunroom_front_double_doors:lower" '
            'd="M 547.6 423.3 A 27.8 27.8 0 0 1 587.0 422.0"',
            svg,
        )
        self.assertIn('<g class="ref-sliding-door" data-ref-sliding-door="entrance_deck_slider">', svg)
        self.assertIn(
            'class="ref-sliding-door-panel sliding" data-ref-sliding-door-panel="entrance_deck_slider:sliding" '
            'x="841.9" y="486.9" width="26.7" height="1.8"',
            svg,
        )
        self.assertIn(
            'class="ref-sliding-door-panel fixed" data-ref-sliding-door-panel="entrance_deck_slider:fixed" '
            'x="860.5" y="489.1" width="21.3" height="1.8"',
            svg,
        )
        self.assertNotIn('x="836.0" y="486.9" width="31.0" height="1.8"', svg)
        self.assertNotIn('x="847.1" y="493.8" width="24.0" height="1.8"', svg)
        self.assertNotIn('x="855.7" y="495.0" width="26.5" height="1.8"', svg)
        self.assertNotIn('x="866.0" y="495.0" width="16.2" height="1.8"', svg)
        self.assertNotIn('x="857.8" y="497.0" width="24.4" height="1.8"', svg)
        self.assertNotIn('class="ref-sliding-door-wall-cap"', svg)
        self.assertNotIn('class="ref-sliding-door-track"', svg)
        self.assertNotIn('class="ref-sliding-door-offset"', svg)
        self.assertNotIn('class="ref-sliding-door-end"', svg)
        self.assertNotIn('class="ref-sliding-door-backing"', svg)
        self.assertNotIn('data-ref-sliding-door-track="entrance_deck_slider:lower"', svg)
        self.assertNotIn('x="828.0" y="494.1" width="8.0" height="3.8"', svg)
        self.assertNotIn('x="836.0" y="492.8" width="46.2" height="5.0"', svg)
        self.assertNotIn('x="832.0" y="492.2" width="12.0" height="4.8"', svg)
        self.assertNotIn('x1="836.0" y1="494.2" x2="882.2" y2="494.2"', svg)
        self.assertNotIn('x1="836.0" y1="497.8" x2="882.2" y2="497.8"', svg)
        self.assertNotIn('x="850.6" y="492.6" width="23.1" height="3.0"', svg)
        self.assertNotIn('data-ref-window="entrance_deck_slider"', svg)
        self.assertIn('<g class="ref-sliding-door" data-ref-sliding-door="sunroom_lounge_slider">', svg)
        self.assertLess(
            svg.index('data-ref-window="sunroom_wraparound_glazing"'),
            svg.index('<g class="ref-sliding-door" data-ref-sliding-door="sunroom_lounge_slider">'),
        )
        self.assertIn(
            'class="ref-sliding-door-panel sliding" data-ref-sliding-door-panel="sunroom_lounge_slider:sliding" '
            'x="662.4" y="377.8" width="1.8" height="55.1"',
            svg,
        )
        self.assertIn(
            'class="ref-sliding-door-panel fixed" data-ref-sliding-door-panel="sunroom_lounge_slider:fixed" '
            'x="664.2" y="417.8" width="1.8" height="42.2"',
            svg,
        )
        self.assertNotIn(
            'class="ref-sliding-door-panel sliding" data-ref-sliding-door-panel="sunroom_lounge_slider:sliding" '
            'x="641.3" y="388.0" width="1.8" height="85.6"',
            svg,
        )
        self.assertNotIn(
            'class="ref-sliding-door-panel fixed" data-ref-sliding-door-panel="sunroom_lounge_slider:fixed" '
            'x="643.1" y="388.0" width="1.8" height="85.6"',
            svg,
        )
        self.assertNotIn(
            'class="ref-sliding-door-panel fixed" data-ref-sliding-door-panel="sunroom_lounge_slider:fixed" '
            'x="644.5" y="429.7" width="1.8" height="43.9"',
            svg,
        )
        self.assertNotIn(
            'class="ref-sliding-door-panel fixed" data-ref-sliding-door-panel="sunroom_lounge_slider:fixed" '
            'x="643.1" y="429.7" width="1.8" height="43.9"',
            svg,
        )
        self.assertNotIn('data-ref-window="sunroom_lounge_slider"', svg)
        self.assertNotIn('x1="643.5" y1="388.0" x2="643.5" y2="454.0"', svg)
        self.assertNotIn('data-ref-wall-junction="sunroom_lounge_slider_top_cap"', svg)
        self.assertNotIn('data-ref-wall-junction="sunroom_lounge_slider_bottom_cap"', svg)
        self.assertIn(
            'data-ref-wall-junction="sunroom_lounge_upper_wall_fill" '
            'x="659.1" y="344.8" width="8.0" height="8.0"',
            svg,
        )
        self.assertNotIn('data-ref-wall-junction="lounge_north_wall_left_underside_fill"', svg)
        self.assertIn(
            'data-ref-wall-junction="sunroom_lounge_lower_wall_fill" '
            'x="659.1" y="460.0" width="8.0" height="24.6"',
            svg,
        )
        self.assertIn(
            'data-ref-window="master_sunroom_window" data-window-context="exterior" '
            'x1="608.9" y1="482.4" x2="552.1" y2="482.4"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="master_sunroom_window" data-window-context="exterior" '
            'x1="608.9" y1="484.4" x2="552.1" y2="484.4"',
            svg,
        )
        self.assertIn(
            'data-ref-window-guide="master_sunroom_window" data-window-context="exterior" '
            'x1="608.9" y1="480.4" x2="552.1" y2="480.4"',
            svg,
        )
        self.assertNotIn(
            'data-ref-window="master_sunroom_window" data-window-context="exterior" '
            'x1="591.2" y1="490.0" x2="534.8" y2="490.0"',
            svg,
        )
        self.assertNotIn(
            'data-ref-window="master_sunroom_window" data-window-context="exterior" '
            'x1="604.0" y1="485.0" x2="552.0" y2="485.0"',
            svg,
        )
        self.assertNotIn('data-ref-window="master_sunroom_window" data-window-context="internal"', svg)
        self.assertNotIn('class="ref-window-glass"', svg)
        self.assertNotIn("ref-slider-track", svg)
        self.assertIn('class="ref-door-leaf double-door"', svg)
        self.assertIn('class="ref-door-arc double-door"', svg)
        self.assertIn('data-ref-opening="deck_side_dining_window"', svg)
        self.assertIn('data-ref-passage="hallway_to_entrance_laundry"', svg)
        self.assertIn('data-ref-passage="entrance_to_laundry_opening" points="899.8,496.5 905.8,496.5 905.8,516.1 899.8,516.1"', svg)
        self.assertIn(
            'class="opening-cutout exterior timber threshold" data-ref-opening-cutout="deck_door_group" '
            'data-opening-context="exterior" data-opening-part="interior-floor" '
            'x1="829.5" y1="350.8" x2="829.5" y2="393.8"',
            svg,
        )
        self.assertIn(
            'class="opening-cutout exterior deck threshold" data-ref-opening-cutout="deck_door_group" '
            'data-opening-context="exterior" data-opening-part="deck-floor" '
            'x1="836.0" y1="350.8" x2="836.0" y2="393.8"',
            svg,
        )
        self.assertNotIn(
            'class="opening-cutout exterior" data-ref-opening-cutout="deck_door_group"',
            svg,
        )
        self.assertNotIn(
            'class="opening-cutout exterior timber" data-ref-opening-cutout="deck_door_group" '
            'data-opening-context="exterior" x1="822.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf double-door" data-ref-door-leaf="deck_door_group:upper" '
            'd="M 833.0 350.8 L 854.5 350.8"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf double-door" data-ref-door-leaf="deck_door_group:lower" '
            'd="M 833.0 393.8 L 854.5 393.8"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc double-door" data-ref-door-arc="deck_door_group:upper" '
            'd="M 854.5 350.8 A 21.5 21.5 0 0 1 833.0 372.3"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc double-door" data-ref-door-arc="deck_door_group:lower" '
            'd="M 854.5 393.8 A 21.5 21.5 0 0 0 833.0 372.3"',
            svg,
        )
        self.assertNotIn('data-ref-door-leaf="deck_door_group:upper" d="M 822.0 338.0 L 793.0 338.0"', svg)
        self.assertNotIn('data-ref-door-arc="deck_door_group:upper" d="M 793.0 338.0', svg)
        self.assertNotIn('data-ref-door-leaf="deck_door_group" d="M 822.0 338.0 L 801.0 367.0"', svg)
        self.assertNotIn('data-ref-door-arc="deck_door_group" d="M 822.0 338.0 Q 794.0 338.0 794.0 371.0"', svg)
        self.assertNotIn('data-ref-opening-cutout="hallway_to_office_door"', svg)
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="hallway_to_office_door" '
            'd="M 717.3 523.0 L 717.3 544.8"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="hallway_to_office_door" '
            'd="M 695.5 523.0 A 21.8 21.8 0 0 0 717.3 544.8"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="hallway_to_master_bedroom_door" '
            'd="M 627.1 516.0 L 605.1 516.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="hallway_to_master_bedroom_door" '
            'd="M 627.1 494.0 A 22.0 22.0 0 0 0 605.1 516.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="hallway_to_lounge_door" '
            'd="M 701.5 484.6 L 701.5 462.6"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="hallway_to_lounge_door" '
            'd="M 723.5 484.6 A 22.0 22.0 0 0 0 701.5 462.6"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="hallway_to_sunroom_old_front_door" '
            'd="M 635.2 482.4 L 635.2 502.6"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="hallway_to_sunroom_old_front_door" '
            'd="M 655.4 482.4 A 20.2 20.2 0 0 1 635.2 502.6"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="hallway_to_kitchen_dining_door" '
            'd="M 760.9 493.0 L 738.9 493.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="hallway_to_kitchen_dining_door" '
            'd="M 760.9 515.0 A 22.0 22.0 0 0 1 738.9 493.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="kitchen_dining_to_bedroom2_door" '
            'd="M 778.6 523.3 L 778.6 545.3"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="kitchen_dining_to_bedroom2_door" '
            'd="M 800.6 523.3 A 22.0 22.0 0 0 1 778.6 545.3"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="entrance_to_kitchen_dining_door" '
            'd="M 803.7 519.5 L 783.9 519.5"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="entrance_to_kitchen_dining_door" '
            'd="M 803.7 499.7 A 19.8 19.8 0 0 0 783.9 519.5"',
            svg,
        )
        self.assertNotIn('data-ref-door-leaf="entrance_to_kitchen_dining_door" d="M 784.0 519.5 L 764.2 519.5"', svg)
        self.assertNotIn('data-ref-door-arc="entrance_to_kitchen_dining_door" d="M 784.0 499.7 A 19.8 19.8', svg)
        self.assertNotIn('data-ref-door-leaf="entrance_to_kitchen_dining_door" d="M 786.5 521.9 L 766.7 521.9"', svg)
        self.assertNotIn('data-ref-door-arc="entrance_to_kitchen_dining_door" d="M 786.5 502.1 A 19.8 19.8', svg)
        self.assertNotIn('data-ref-door-leaf="entrance_to_kitchen_dining_door" d="M 789.5 520.9 L 769.7 520.9"', svg)
        self.assertNotIn('data-ref-door-arc="entrance_to_kitchen_dining_door" d="M 789.5 501.1 A 19.8 19.8', svg)
        self.assertNotIn('data-ref-door-leaf="entrance_to_kitchen_dining_door" d="M 789.5 522.0 L 767.5 522.0"', svg)
        self.assertNotIn('data-ref-door-arc="entrance_to_kitchen_dining_door" d="M 789.5 500.0 A 22.0 22.0', svg)
        self.assertNotIn('data-ref-door-leaf="entrance_to_kitchen_dining_door" d="M 789.5 519.5 L 769.7 519.5"', svg)
        self.assertNotIn('data-ref-door-arc="entrance_to_kitchen_dining_door" d="M 789.5 499.7 A 19.8 19.8', svg)
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="laundry_to_toilet_door" '
            'd="M 908.8 572.9 L 908.8 588.9"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="laundry_to_toilet_door" '
            'd="M 924.8 572.9 A 16.0 16.0 0 0 1 908.8 588.9"',
            svg,
        )
        self.assertNotIn('data-ref-door-leaf="laundry_to_toilet_door" d="M 890.0 580.0', svg)
        self.assertIn(
            '<g class="ref-pocket-door" data-ref-pocket-door="hallway_to_bathroom_sliding_door">',
            svg,
        )
        self.assertNotIn('data-ref-opening-cutout="hallway_to_bathroom_sliding_door"', svg)
        self.assertIn(
            'class="ref-pocket-door-panel" data-ref-pocket-door-panel="hallway_to_bathroom_sliding_door" '
            'x="727.4" y="522.0" width="22.0" height="2.0"',
            svg,
        )
        self.assertIn(
            'class="ref-pocket-door-casing" data-ref-pocket-door-casing="hallway_to_bathroom_sliding_door" '
            'x="743.4" y="520.3" width="30.5" height="5.4"',
            svg,
        )
        self.assertIn(
            'class="ref-pocket-door-slot" data-ref-pocket-door-slot="hallway_to_bathroom_sliding_door" '
            'x="746.4" y="522.0" width="24.5" height="2.0"',
            svg,
        )
        self.assertNotIn('class="ref-pocket-door-recess"', svg)
        self.assertNotIn('data-ref-window="hallway_to_bathroom_sliding_door"', svg)
        self.assertNotIn('data-ref-opening-cutout="hallway_to_master_bedroom_door"', svg)
        self.assertNotIn('data-ref-opening-cutout="hallway_to_lounge_door"', svg)
        self.assertNotIn('data-ref-opening-cutout="hallway_to_sunroom_old_front_door"', svg)
        self.assertNotIn('data-ref-opening-cutout="hallway_to_kitchen_dining_door"', svg)
        self.assertNotIn('data-ref-opening-cutout="kitchen_dining_to_bedroom2_door"', svg)
        self.assertNotIn('data-ref-opening-cutout="entrance_to_kitchen_dining_door"', svg)
        self.assertNotIn('data-ref-opening-cutout="laundry_to_toilet_door"', svg)
        self.assertNotIn('<line class="ref-opening-jamb" x1="608.0" y1="488.5" x2="608.0" y2="497.5"/>', svg)
        self.assertNotIn('<line class="ref-opening-jamb" x1="608.0" y1="512.5" x2="608.0" y2="521.5"/>', svg)
        self.assertNotIn('<line class="ref-opening-jamb" x1="680.0" y1="518.5" x2="680.0" y2="527.5"/>', svg)
        self.assertNotIn('<line class="ref-opening-jamb" x1="656.0" y1="518.5" x2="656.0" y2="527.5"/>', svg)
        self.assertNotIn('data-ref-opening-cutout="hallway_to_office_door" data-opening-context="interior" x1="648.0" y1="523.0" x2="608.0" y2="523.0"', svg)
        self.assertNotIn('data-ref-door-leaf="hallway_to_office_door" d="M 648.0 526.0 L 677.0 505.0"', svg)
        self.assertIn('data-ref-door-leaf="laundry_to_toilet_door"', svg)
        self.assertNotIn("#7956b3", svg)
        self.assertNotIn("arch-opening-line", svg)
        self.assertNotIn("ref-opening-cap", svg)
        self.assertNotIn("ref-open-threshold", svg)

    def test_reference_plan_uses_curated_wall_network_for_kitchen_hallway_junction(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('id="reference-wall-layer" data-source="curated-matplotlib-wall-network"', svg)
        self.assertIn('data-ref-wall="lounge_kitchen_divider"', svg)
        self.assertIn('data-ref-wall="kitchen_east_wall"', svg)
        self.assertIn('data-ref-wall="master_west_wall"', svg)
        self.assertIn('data-ref-wall="lounge_exterior"', svg)
        self.assertIn('data-ref-wall="hallway_north_wall"', svg)
        self.assertIn('data-ref-wall="hallway_sunroom_right_jamb"', svg)
        self.assertIn('data-ref-wall="hallway_south_wall"', svg)
        self.assertIn('data-ref-wall="bedroom2_north_wall"', svg)
        self.assertNotIn('data-ref-wall="bedroom2_laundry_jamb_nub"', svg)
        self.assertIn('data-ref-wall="entrance_laundry_wall"', svg)
        self.assertIn('data-ref-wall="bedroom2_east_wall"', svg)
        self.assertIn('data-ref-wall="entrance_deck_wall"', svg)
        self.assertIn('data-ref-wall="kitchen_entrance_return_wall"', svg)
        self.assertIn('data-ref-wall="private_rooms_south_wall"', svg)
        self.assertIn('data-ref-wall="sunroom_glazing_frame"', svg)
        self.assertIn(
            'data-ref-wall="sunroom_glazing_frame" data-ref-wall-class="interior" '
            'd="M549.2 483.4 V442.3 H568 M606 401.6 V346.7 H663.1"',
            svg,
        )
        self.assertNotIn('V343.3 H663.1', svg)
        self.assertNotIn('V357.4 H667.1 V377.8 M667.1 460 V483.4', svg)
        self.assertNotIn('data-ref-wall="sunroom_glazing_frame" data-ref-wall-class="interior" d="M536 486 H646 V360 H597 V408 L552 452 H536 Z"', svg)
        self.assertNotIn('data-ref-wall="sunroom_glazing_frame" data-ref-wall-class="interior" d="M536 486 H646 V462.6', svg)
        self.assertNotIn('data-ref-wall="lounge_sunroom_wall" data-ref-wall-class="interior" d="M638 358 V485"', svg)
        self.assertNotIn('data-ref-wall="sunroom_exterior" data-ref-wall-class="exterior"', svg)
        self.assertIn('data-ref-wall="master_sunroom_old_external_wall"', svg)
        self.assertIn('data-ref-wall="master_sunroom_old_external_wall" data-ref-wall-class="exterior" d="M533.9 482.4 H627.1"', svg)
        self.assertNotIn('id="reference-post-opening-wall-cap-layer"', svg)
        self.assertNotIn('.post-opening-wall-cap', svg)
        self.assertNotIn('data-ref-post-opening-wall-cap="sunroom_master_corner_square_cap"', svg)
        self.assertIn(
            'data-ref-wall="master_office_wall" data-ref-wall-class="thin-interior" '
            'data-wall-thickness-m="0.125" '
            'd="M627.1 482.4 V494 M627.1 516 V527 M627.1 558 V567 M627.1 598 V601.8"',
            svg,
        )
        self.assertIn('data-ref-wall="lounge_exterior" data-ref-wall-class="exterior" d="M659.1 348.8 H762.8"', svg)
        self.assertNotIn('data-ref-wall="lounge_exterior" data-ref-wall-class="exterior" d="M659.1 348.8 H758.4"', svg)
        self.assertNotIn('data-ref-wall="lounge_exterior" data-ref-wall-class="exterior" d="M638 358 H742"', svg)
        self.assertIn('data-ref-wall="hallway_north_wall" data-ref-wall-class="exterior" d="M627.1 482.4 H635.2"', svg)
        self.assertIn('data-ref-wall="hallway_sunroom_right_jamb" data-ref-wall-class="exterior" d="M655.4 482.4 H663.1"', svg)
        self.assertNotIn('data-ref-wall="hallway_north_wall_trimmed_return"', svg)
        self.assertNotIn('data-ref-wall="hallway_north_wall" data-ref-wall-class="exterior" d="M627.1 482.4 H635.2 M655.4 482.4 H668"', svg)
        self.assertNotIn('data-ref-wall="hallway_north_wall" data-ref-wall-class="exterior" d="M627.1 482.4 H644"', svg)
        self.assertIn('data-ref-wall="lounge_hallway_wall" data-ref-wall-class="interior" d="M663.1 484.6 H701.5 M723.5 484.6 H760.9"', svg)
        self.assertNotIn('data-ref-wall="lounge_hallway_wall" data-ref-wall-class="interior" d="M663.1 484.6 H683 M705 484.6 H760.9"', svg)
        self.assertNotIn('data-ref-wall="lounge_hallway_wall" data-ref-wall-class="interior" d="M655.4 484.6 H701.5 M723.5 484.6 H760.9"', svg)
        self.assertNotIn('data-ref-wall="lounge_hallway_wall" data-ref-wall-class="interior" d="M660.1 484.6 H701.5 M723.5 484.6 H760.9"', svg)
        self.assertNotIn('data-ref-wall="lounge_hallway_wall" data-ref-wall-class="interior" d="M659.1 484.6 H701.5 M723.5 484.6 H760.9"', svg)
        self.assertNotIn('data-ref-wall="hallway_north_wall" data-ref-wall-class="exterior" d="M608 485 H642"', svg)
        self.assertNotIn('data-ref-wall="hallway_north_wall" data-ref-wall-class="exterior" d="M608 485 H639"', svg)
        self.assertNotIn('data-ref-wall="hallway_north_wall" data-ref-wall-class="exterior" d="M608 485 H638"', svg)
        self.assertNotIn('data-ref-wall="lounge_hallway_wall" data-ref-wall-class="interior" d="M638 489 H683 M705 489 H745.5"', svg)
        self.assertIn('data-ref-wall="hallway_kitchen_door_wall" data-ref-wall-class="interior" d="M760.9 515 V523"', svg)
        self.assertIn('data-ref-wall="dining_west_external_wall"', svg)
        self.assertIn('data-ref-wall="dining_west_external_wall" data-ref-wall-class="exterior" d="M758.8 302.3 V348.8"', svg)
        self.assertNotIn('data-ref-wall="dining_west_external_wall" data-ref-wall-class="exterior" d="M758.8 314 V358"', svg)
        self.assertIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M758.8 348.8 V302.3 H833 V491.9"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M758.8 358 V314 H833 V491.9"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M758.8 358 V314 H833 V493.6"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M758.8 358 V314 H833 V495.9"', svg)
        self.assertNotIn('data-ref-wall="dining_west_external_wall" data-ref-wall-class="exterior" d="M757.4 314 V358"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M757.4 358 V314 H833 V495.9"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M757.4 358 V314 H833 V491.6"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 358 V314 H822 V498"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 358 V314 H822 V500"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 358 V314 H822 V502.8"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 358 V314 H822 V496"', svg)
        self.assertIn(
            'data-ref-wall="kitchen_lounge_nub" data-ref-wall-class="interior" '
            'data-wall-projection-m="0.47" d="M760.9 348.8 V361.3"',
            svg,
        )
        self.assertIn('data-ref-wall="entrance_deck_wall" data-ref-wall-class="thin-exterior" data-wall-thickness-m="0.14" d="M834.3 489.1 H841.9 M881.8 489.1 H956.4"', svg)
        self.assertNotIn('data-ref-wall="entrance_deck_wall" data-ref-wall-class="thin-exterior" data-wall-thickness-m="0.14" d="M834.3 489.1 H836 M882.2 489.1 H956.4"', svg)
        self.assertIn('data-ref-wall="kitchen_entrance_return_wall" data-ref-wall-class="thin-interior" data-wall-thickness-m="0.13" d="M834.3 489.1 V495.9 H803.7"', svg)
        self.assertNotIn('data-ref-wall="kitchen_entrance_return_wall" data-ref-wall-class="thin-interior" data-wall-thickness-m="0.13" d="M824 496 V502.8 H789.5"', svg)
        self.assertNotIn('data-ref-wall="kitchen_entrance_return_wall" data-ref-wall-class="thin-interior" data-wall-thickness-m="0.13" d="M822 496 V502.8 H789.5"', svg)
        self.assertIn('data-ref-room="entrance" points="803.7,495.9 834.3,495.9 834.3,489.1 902.8,489.1 902.8,523.3 803.7,523.3"', svg)
        self.assertIn(
            'data-ref-room="kitchen_dining" points="758.8,302.3 833.0,302.3 833.0,489.1 834.3,489.1 834.3,495.9 803.7,495.9 803.7,523.3 760.9,523.0 760.9,348.8 758.8,348.8"',
            svg,
        )
        self.assertNotIn("784.0,523.0 758.0,523.0 758.0,500.0 742.0,500.0", svg)
        self.assertNotIn("784.0,523.0 742.0,523.0", svg)
        self.assertIn('class="ref-floor carpet" data-ref-room="lounge" x="659.1" y="348.8" width="101.8" height="133.6"', svg)
        self.assertIn('class="ref-floor carpet" data-ref-room="hallway" points="627.1,482.4 760.9,482.4 760.9,523.0 627.1,523.0"', svg)
        self.assertNotIn('class="ref-floor carpet" data-ref-room="hallway" points="608.0,485.0 742.0,485.0 742.0,523.0 608.0,523.0"', svg)
        self.assertNotIn('class="ref-floor carpet" data-ref-room="hallway" x="608.0" y="485.0" width="150.0" height="38.0"', svg)
        self.assertIn(
            'class="opening-passage-fill vinyl-plank" data-ref-passage="hallway_to_entrance_laundry" '
            'points="760.9,495.9 803.7,495.9 803.7,523.3 760.9,523.3"',
            svg,
        )
        self.assertNotIn(
            'class="opening-passage-fill vinyl-plank" data-ref-passage="hallway_to_entrance_laundry" '
            'points="758.0,500.0 803.7,500.0 803.7,523.0 758.0,523.0"',
            svg,
        )
        self.assertNotIn('data-ref-room="entrance" points="789.5,496.0 890.0,496.0 890.0,523.0 789.5,523.0"', svg)
        self.assertIn('data-ref-room="laundry" x="902.8" y="489.1" width="53.6" height="83.8"', svg)
        self.assertNotIn('data-ref-wall="laundry_north_wall" data-ref-wall-class="interior" d="M890 500 H940"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 314 H822 V496 H800"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 365 V314 H822 V496 H800"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 365 V314 H822 V496"', svg)
        self.assertNotIn('data-ref-wall="dining_west_external_wall" data-ref-wall-class="exterior" d="M742 314 V365"', svg)
        self.assertIn(
            'class="wall-core exterior structural" data-ref-wall-class="exterior" '
            'd="M659.1 348.8 H762.8 M663.1 348.8 V377.8 M663.1 460 V484.6 M758.8 348.8 V302.3 H833 V491.9 M956.4 487.3 V602.2 M902.8 601.8 H533.9 V482.4 H635.2 M655.4 482.4 H663.1"',
            svg,
        )
        self.assertNotIn('class="wall-core trimmed-exterior structural"', svg)
        self.assertIn('.wall-core.thin-exterior { stroke: #585b63; stroke-width: 3.7px;', svg)
        self.assertIn('class="wall-core thin-exterior structural" data-ref-wall-class="thin-exterior" d="M834.3 489.1 H841.9 M881.8 489.1 H956.4"', svg)
        self.assertIn('.wall-core.toilet-exterior { stroke: #585b63; stroke-width: 7.2px;', svg)
        self.assertIn('class="wall-core toilet-exterior structural" data-ref-wall-class="toilet-exterior" d="M900.6 602.2 H960.4"', svg)
        self.assertIn('.wall-junction-cap { fill: #585b63;', svg)
        self.assertIn(
            'data-ref-wall-junction="entrance_return_thin_square_end" '
            'x="801.9" y="494.3" width="35.1" height="3.3"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall-junction="entrance_return_thin_square_end" '
            'x="803.7" y="494.3" width="30.6" height="3.3"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall-junction="entrance_return_thin_square_end" '
            'x="801.9" y="494.3" width="32.4" height="3.3"',
            svg,
        )
        self.assertIn(
            'data-ref-wall-junction="kitchen_entrance_external_wall_flat_bottom" '
            'x="829.0" y="302.3" width="8.0" height="193.6"',
            svg,
        )
        self.assertNotIn(
            'data-ref-wall-junction="kitchen_bedroom2_door_jamb_square_corner" '
            'x="800.4"',
            svg,
        )
        self.assertNotIn('data-ref-wall-junction="entrance_return_square_wall"', svg)
        self.assertNotIn('x="803.7" y="489.1" width="30.6" height="6.8"', svg)
        self.assertNotIn('data-ref-wall-junction="entrance_narrowing_square_corner"', svg)
        self.assertNotIn('data-ref-wall-junction="laundry_top_right_square_corner"', svg)
        self.assertNotIn('data-ref-wall-junction="entrance_narrowing_vertical_closure"', svg)
        self.assertNotIn('data-ref-wall-junction="sunroom_lounge_slider_top_cap"', svg)
        self.assertNotIn('data-ref-wall-junction="sunroom_lounge_slider_bottom_cap"', svg)
        self.assertNotIn('data-ref-wall-junction="entrance_narrowing_return_join"', svg)
        self.assertNotIn('data-ref-wall-junction="entrance_narrowing_return_join" x="818.0" y="496.0" width="6.0" height="6.8"', svg)
        self.assertNotIn('data-ref-wall-junction="entrance_narrowing_return_join" x="818.0" y="496.0" width="6.0" height="8.8"', svg)
        self.assertNotIn('data-ref-wall-junction="laundry_top_right_square_corner" x="934.0" y="490.0" width="12.0" height="12.0"', svg)
        self.assertNotIn('data-ref-wall="entrance_deck_wall" data-ref-wall-class="exterior" d="M822 496 H836 M882.2 496 H940"', svg)
        self.assertNotIn("M877 496 H940 M638 485 H532.4 V601.8 H940 V496", svg)
        self.assertIn('d="M663.1 484.6 H701.5 M723.5 484.6 H760.9"', svg)
        self.assertIn('d="M627.1 523 H695.5 M717.3 523 H727.1 M743.4 523 H773.9"', svg)
        self.assertIn('data-ref-wall="wardrobe_office_wall" data-ref-wall-class="thin-interior" data-wall-thickness-m="0.125" d="M646.8 523 V601.8"', svg)
        self.assertIn('data-ref-wall="office_bathroom_wall" data-ref-wall-class="thin-interior" data-wall-thickness-m="0.125" d="M727.1 521.2 V601.8"', svg)
        self.assertNotIn('data-ref-wall="office_bathroom_wall" data-ref-wall-class="interior" d="M688 523 V610"', svg)
        self.assertIn('data-ref-wall="entrance_laundry_wall" data-ref-wall-class="interior" d="M902.8 489.1 V496.5"', svg)
        self.assertIn('data-ref-wall="bedroom2_east_wall" data-ref-wall-class="interior" d="M902.8 516.1 V602.2"', svg)
        self.assertNotIn('data-ref-wall="bedroom2_east_wall" data-ref-wall-class="interior" d="M890 524.1 V610"', svg)
        self.assertNotIn('data-ref-wall="bedroom2_east_wall" data-ref-wall-class="interior" d="M890 520.5 V610"', svg)
        self.assertNotIn('data-ref-wall="bedroom2_east_wall" data-ref-wall-class="interior" d="M890 500 V610"', svg)
        self.assertNotIn("M890 500 V610", svg)
        self.assertIn('data-ref-wall="bedroom2_north_wall" data-ref-wall-class="thin-interior" d="M773.9 523.3 H778.6 M800.6 523.3 H902.8"', svg)
        self.assertNotIn('data-ref-wall="bedroom2_north_wall" data-ref-wall-class="interior" d="M758 523 H762 M784 523 H890"', svg)
        self.assertNotIn('data-ref-wall="bedroom2_laundry_jamb_nub"', svg)
        self.assertNotIn('data-ref-wall="bedroom2_north_wall" data-ref-wall-class="interior" d="M758 523 H762 M784 523 H880"', svg)
        self.assertNotIn('data-ref-wall="bedroom2_laundry_jamb_nub" data-ref-wall-class="interior" d="M885 523 H890"', svg)
        self.assertNotIn('data-ref-manual-openings="open-plan-room-gaps"', svg)
        self.assertNotIn('data-ref-passage="kitchen_to_hallway_gap"', svg)
        self.assertIn('data-ref-wall="lounge_kitchen_divider"', svg)
        self.assertIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M760.9 392.4 V493"', svg)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M745.72 395 V493"', svg)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M745.73 395 V493"', svg)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M745.74 395 V493"', svg)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M745.75 395 V493"', svg)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M746 395 V493"', svg)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M747 395 V493"', svg)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M748 395 V493"', svg)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M742 395 V493"', svg)
        self.assertNotIn('data-ref-wall="hallway_kitchen_door_wall" data-ref-wall-class="interior" d="M746 515 V523"', svg)
        self.assertNotIn('data-ref-wall="hallway_kitchen_door_wall" data-ref-wall-class="interior" d="M747 515 V523"', svg)
        self.assertNotIn('data-ref-wall="hallway_kitchen_door_wall" data-ref-wall-class="interior" d="M748 515 V523"', svg)
        self.assertNotIn('data-ref-wall="hallway_kitchen_door_wall" data-ref-wall-class="interior" d="M742 515 V523"', svg)
        self.assertIn('.wall-core.thin-interior { stroke: #585b63; stroke-width: 3.3px;', svg)
        self.assertIn(
            'class="wall-core interior structural" data-ref-wall-class="interior" '
            'd="M549.2 483.4 V442.3 H568 M606 401.6 V346.7 H663.1',
            svg,
        )
        self.assertIn("M760.9 348.8 V361.3", svg)
        self.assertNotIn("M745.72 358 V370.8", svg)
        self.assertNotIn("M745.73 358 V370.8", svg)
        self.assertNotIn("M745.74 358 V370.8", svg)
        self.assertNotIn("M745.75 358 V370.8", svg)
        self.assertNotIn("M746 358 V370.8", svg)
        self.assertNotIn("M747 358 V370.8", svg)
        self.assertNotIn("M748 358 V370.8", svg)
        self.assertIn('class="wall-core thin-interior structural" data-ref-wall-class="thin-interior" d="M834.3 489.1 V495.9 H803.7 M773.9 523.3 H778.6 M800.6 523.3 H902.8 M627.1 482.4 V494 M627.1 516 V527 M627.1 558 V567 M627.1 598 V601.8 M646.8 523 V601.8 M727.1 521.2 V601.8 M773.9 523 V601.8 M902.8 572.9 H908.8 M924.8 572.9 H956.4"', svg)
        self.assertIn('data-ref-wall="laundry_toilet_wall" data-ref-wall-class="thin-interior" data-wall-thickness-m="0.12" d="M902.8 572.9 H908.8 M924.8 572.9 H956.4"', svg)
        self.assertNotIn('data-ref-wall="laundry_toilet_wall" data-ref-wall-class="interior" d="M906.4 580 H912.4 M928.4 580 H956.4"', svg)
        self.assertIn('data-ref-wall="kitchen_entrance_door_wall" data-ref-wall-class="interior" d="M803.7 495.9 V499.7 M803.7 519.5 V523.3"', svg)
        self.assertNotIn('data-ref-wall="kitchen_entrance_door_wall" data-ref-wall-class="interior" d="M784 495.9 V499.7 M784 519.5 V523.3"', svg)
        self.assertNotIn('data-ref-wall="kitchen_entrance_door_wall" data-ref-wall-class="interior" d="M786.5 500 V502.1 M786.5 521.9 V523"', svg)
        self.assertNotIn('data-ref-wall="kitchen_entrance_door_wall" data-ref-wall-class="interior" d="M789.5 500 V501.1 M789.5 520.9 V523"', svg)
        self.assertNotIn('data-ref-wall="kitchen_entrance_door_wall" data-ref-wall-class="interior" d="M789.5 500 V501 M789.5 522 V523"', svg)
        entrance_local_px_per_m = 22 / 0.81
        self.assertAlmostEqual((902.8 - 834.3) / entrance_local_px_per_m, 2.52, places=2)
        self.assertAlmostEqual((834.3 - 803.7) / entrance_local_px_per_m, 1.13, places=2)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M742 395 V500"', svg)
        self.assertNotIn('d="M742 314 V365 M742 395 V500"', svg)
        self.assertNotIn('data-ref-passage="lounge_to_kitchen_gap"', svg)
        self.assertNotIn('data-ref-wall-space="kitchen_dining"', svg)

    def test_reference_plan_uses_subdued_room_labels_and_materials(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('pattern id="vinyl-planks-vertical"', svg)
        self.assertIn('pattern id="carpet-light-brown"', svg)
        self.assertIn('pattern id="tile-soft"', svg)
        self.assertIn('<rect width="22" height="46" fill="#bda684"/>', svg)
        self.assertIn('<rect width="18" height="18" fill="#efe4d2"/>', svg)
        self.assertIn('.ref-floor.vinyl-plank { fill: url(#vinyl-planks-vertical); }', svg)
        self.assertIn('.ref-floor.carpet { fill: url(#carpet-light-brown); }', svg)
        self.assertIn('.ref-floor.tile { fill: url(#tile-soft); }', svg)
        for room_id in ["kitchen_dining", "entrance", "laundry", "toilet"]:
            self.assertIn(f'class="ref-floor vinyl-plank" data-ref-room="{room_id}"', svg)
        for room_id in ["sunroom", "lounge", "hallway", "master_bedroom", "office", "bedroom_2"]:
            self.assertIn(f'class="ref-floor carpet" data-ref-room="{room_id}"', svg)
        self.assertIn('class="ref-floor tile" data-ref-room="bathroom"', svg)
        self.assertIn('class="opening-passage-fill vinyl-plank"', svg)
        self.assertIn('pattern id="deck-boards-subtle"', svg)
        self.assertIn(
            'class="ref-site deck" data-ref-site="sunroom_front_steps" '
            'points="606.0,401.6 568.0,442.3 563.0,437.3 601.0,396.6"',
            svg,
        )
        self.assertIn(
            'class="ref-site deck" data-ref-site="sunroom_front_steps" '
            'points="601.0,396.6 563.0,437.3 558.0,432.3 596.0,391.6"',
            svg,
        )
        self.assertIn('pattern id="lawn-soft"', svg)
        self.assertIn('class="ref-room-label"', svg)
        self.assertIn("font-size: 9px;", svg)
        self.assertIn(".ref-room-label, .ref-site-label { text-anchor: middle; dominant-baseline: middle; font-weight: 500; }", svg)
        self.assertNotIn("paint-order: stroke", svg)
        self.assertIn('class="ref-room-label" x="710.0" y="389.4"', svg)
        self.assertIn('class="ref-room-label" x="580.5" y="512.0"', svg)
        self.assertIn('class="ref-room-label" x="687.0" y="554.0"', svg)
        self.assertIn(">Kitchen / Dining<", svg)
        self.assertNotIn(">Rear Timber Deck<", svg)

    def test_reference_plan_includes_metric_scale_bar_near_house(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('id="reference-scale-layer"', svg)
        self.assertIn('data-scale-source="internal-measured-spans"', svg)
        self.assertIn('data-scale-metres="2"', svg)
        self.assertIn('data-scale-px="53.0"', svg)
        self.assertIn('data-scale-px-per-m="26.5"', svg)
        self.assertNotIn('data-scale-source="internal-door-0.81m"', svg)
        self.assertNotIn('data-scale-px="54.3"', svg)
        self.assertIn('<text class="ref-scale-label" x="1065.0" y="614.0">Internal room scale</text>', svg)
        self.assertIn('<text class="ref-scale-label" x="1038.5" y="640.0">0</text>', svg)
        self.assertIn('<text class="ref-scale-label" x="1065.0" y="640.0">1 m</text>', svg)
        self.assertIn('<text class="ref-scale-label" x="1091.5" y="640.0">2 m</text>', svg)
        self.assertIn('<line class="ref-scale-line" x1="1038.5" y1="628.0" x2="1091.5" y2="628.0"/>', svg)
        self.assertIn('<line class="ref-scale-tick" x1="1038.5" y1="624.0" x2="1038.5" y2="632.0"/>', svg)
        self.assertIn('<line class="ref-scale-tick" x1="1065.0" y1="624.0" x2="1065.0" y2="632.0"/>', svg)
        self.assertIn('<line class="ref-scale-tick" x1="1091.5" y1="624.0" x2="1091.5" y2="632.0"/>', svg)
        self.assertNotIn('<line class="ref-scale-line" x1="958.0" y1="628.0" x2="1011.0" y2="628.0"/>', svg)

    def test_reference_plan_includes_hidden_dimension_layer(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('id="reference-dimension-layer"', svg)
        self.assertIn('style="display:none"', svg)
        self.assertLess(svg.index('id="reference-dimension-layer"'), svg.index('id="reference-label-layer"'))

    def test_reference_plan_dimension_layer_contains_external_and_internal_metres(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('data-ref-dimension-kind="external"', svg)
        self.assertIn('data-ref-dimension-kind="internal"', svg)
        self.assertIn('data-ref-dimension="overall-master-to-laundry"', svg)
        self.assertIn('data-ref-dimension="master-bedroom-clear-width"', svg)
        self.assertIn(">16.10 m<", svg)
        self.assertIn(">3.30 m<", svg)

    def test_reference_plan_dimension_layer_marks_approximate_dimensions(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('data-ref-dimension-confidence="measured"', svg)
        self.assertIn('data-ref-dimension-confidence="approximate"', svg)
        self.assertIn('class="ref-dimension-label approximate"', svg)

    def test_reference_plan_includes_orientation_compass_near_scale(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('id="reference-orientation-layer"', svg)
        self.assertIn('data-north-angle-deg="37.5"', svg)
        self.assertIn('data-plan-right-bearing-deg="52.5"', svg)
        self.assertIn('data-orientation-confidence="estimated_from_cadastral_map"', svg)
        self.assertIn('<title>North arrow estimated from parcel-line angle in the cadastral map screenshot; plan right is approximately NE.</title>', svg)
        self.assertIn('<line class="ref-compass-axis" x1="1055.3" y1="590.7" x2="1074.7" y2="565.3"/>', svg)
        self.assertIn('<polygon class="ref-compass-arrow" points="1074.7,565.3 1073.5,570.7 1069.9,567.9"/>', svg)
        self.assertIn('<text class="ref-compass-label primary" x="1080.2" y="558.2">N</text>', svg)
        self.assertIn('<text class="ref-compass-label" x="1084.8" y="593.2">E</text>', svg)
        self.assertIn('<text class="ref-compass-label" x="1049.8" y="597.8">S</text>', svg)
        self.assertIn('<text class="ref-compass-label" x="1045.2" y="562.8">W</text>', svg)
        self.assertNotIn('<line class="ref-compass-axis" x1="974.8" y1="590.7" x2="994.2" y2="565.3"/>', svg)

    def test_reference_plan_omits_furniture_until_layout_is_ready(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertNotIn('id="furniture-layer"', svg)
        self.assertNotIn('data-furniture=', svg)
        self.assertNotIn('class="furniture', svg)
        self.assertNotIn(".furniture", svg)
        self.assertNotIn('filter id="object-soft-shadow"', svg)
