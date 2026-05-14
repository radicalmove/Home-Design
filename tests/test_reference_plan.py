import unittest

from CODE.home_design.model import load_model
from CODE.home_design.reference_plan import render_reference_plan_svg


class ReferencePlanRenderTests(unittest.TestCase):
    def test_reference_plan_uses_layered_rendering_style(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('data-render-style="reference-plan"', svg)
        self.assertIn('id="reference-floor-layer"', svg)
        self.assertIn('id="reference-passage-layer"', svg)
        self.assertIn('id="reference-wall-layer"', svg)
        self.assertIn('id="reference-opening-layer"', svg)
        self.assertIn('id="reference-label-layer"', svg)
        self.assertLess(svg.index('id="reference-floor-layer"'), svg.index('id="reference-passage-layer"'))
        self.assertLess(svg.index('id="reference-passage-layer"'), svg.index('id="furniture-layer"'))
        self.assertLess(svg.index('id="furniture-layer"'), svg.index('id="reference-wall-layer"'))
        self.assertLess(svg.index('id="reference-wall-layer"'), svg.index('id="reference-opening-layer"'))
        self.assertIn('data-ref-wall-class="exterior"', svg)
        self.assertIn('data-ref-wall-class="interior"', svg)
        self.assertIn(".wall-core, .wall-reference { fill: none; stroke-linecap: butt; stroke-linejoin: miter; }", svg)
        self.assertIn('.wall-core.exterior { stroke: #585b63; stroke-width: 12px;', svg)
        self.assertIn('.wall-core.interior { stroke: #585b63; stroke-width: 5px;', svg)
        self.assertNotIn("stroke-linecap: square", svg)
        self.assertNotIn('data-ref-wall-body="continuous"', svg)
        self.assertIn('id="wall-reference-layer"', svg)
        self.assertNotIn('id="wall-shadow-layer"', svg)
        self.assertNotIn('class="wall-shadow', svg)
        self.assertNotIn('filter: url(#raised-wall-shadow)', svg)
        self.assertNotIn('stroke: url(#wall-top-light)', svg)
        self.assertNotIn('class="wall-top', svg)

    def test_reference_plan_renders_openings_as_cutouts_not_colored_markers(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('class="opening-cutout exterior"', svg)
        self.assertIn('.opening-cutout.exterior { stroke-width: 13px;', svg)
        self.assertIn('.opening-cutout.interior { stroke-width: 7px;', svg)
        self.assertIn('class="ref-window-cutout exterior"', svg)
        self.assertIn('class="ref-window-cutout internal"', svg)
        self.assertIn('.ref-window-cutout.exterior { stroke-width: 8px;', svg)
        self.assertIn('.ref-window-cutout.internal { stroke-width: 4px;', svg)
        self.assertIn('.ref-door-leaf.photo-reference { stroke: #2f3134; stroke-width: 1.8; stroke-linecap: butt; }', svg)
        self.assertIn('.ref-door-arc.photo-reference { stroke: #6f7478; stroke-width: 0.95; }', svg)
        self.assertIn('.ref-pocket-door-panel { fill: #fffdf8; stroke: #2f3134; stroke-width: 0.45; }', svg)
        self.assertIn('.ref-pocket-door-casing { fill: #2f3134; stroke: none; }', svg)
        self.assertIn('.ref-pocket-door-slot { fill: #fffdf8; stroke: none; }', svg)
        self.assertIn('class="ref-window-guide"', svg)
        self.assertIn('data-window-context="exterior"', svg)
        self.assertIn('data-window-context="internal"', svg)
        self.assertIn('data-ref-window="sunroom_wraparound_glazing" data-window-context="internal"', svg)
        self.assertNotIn('data-ref-window="sunroom_wraparound_glazing" data-window-context="exterior"', svg)
        self.assertIn(
            'data-ref-window="deck_side_dining_window" data-window-context="exterior" '
            'x1="822.0" y1="410.0" x2="822.0" y2="484.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window="master_street_window" data-window-context="exterior" '
            'x1="518.0" y1="528.0" x2="518.0" y2="588.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window="office_se_window" data-window-context="exterior" '
            'x1="675.0" y1="610.0" x2="625.0" y2="610.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window="bathroom_se_window" data-window-context="exterior" '
            'x1="746.0" y1="610.0" x2="704.0" y2="610.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window="bedroom2_se_window" data-window-context="exterior" '
            'x1="862.0" y1="610.0" x2="790.0" y2="610.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window="toilet_frosted_window" data-window-context="exterior" '
            'x1="940.0" y1="586.0" x2="940.0" y2="606.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window="entrance_deck_slider" data-window-context="exterior" '
            'x1="877.0" y1="496.0" x2="836.0" y2="496.0"',
            svg,
        )
        self.assertIn(
            'data-ref-window="master_sunroom_window" data-window-context="internal" '
            'x1="604.0" y1="485.0" x2="552.0" y2="485.0"',
            svg,
        )
        self.assertNotIn('class="ref-window-glass"', svg)
        self.assertNotIn("ref-slider-track", svg)
        self.assertIn('class="ref-door-leaf"', svg)
        self.assertIn('class="ref-door-arc"', svg)
        self.assertIn('data-ref-opening="deck_side_dining_window"', svg)
        self.assertIn('data-ref-passage="hallway_to_entrance_laundry"', svg)
        self.assertIn('data-ref-passage="entrance_to_laundry_opening" points="887.0,504.0 893.0,504.0 893.0,524.1 887.0,524.1"', svg)
        self.assertIn('data-ref-door-leaf="deck_door_group" d="M 822.0 338.0 L 801.0 367.0"', svg)
        self.assertIn('data-ref-door-arc="deck_door_group" d="M 822.0 338.0 Q 794.0 338.0 794.0 371.0"', svg)
        self.assertNotIn('data-ref-opening-cutout="hallway_to_office_door"', svg)
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="hallway_to_office_door" '
            'd="M 679.0 523.0 L 679.0 545.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="hallway_to_office_door" '
            'd="M 657.0 523.0 A 22.0 22.0 0 0 0 679.0 545.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="hallway_to_master_bedroom_door" '
            'd="M 608.0 516.0 L 586.0 516.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="hallway_to_master_bedroom_door" '
            'd="M 608.0 494.0 A 22.0 22.0 0 0 0 586.0 516.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="hallway_to_lounge_door" '
            'd="M 683.0 489.0 L 683.0 467.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="hallway_to_lounge_door" '
            'd="M 705.0 489.0 A 22.0 22.0 0 0 0 683.0 467.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="hallway_to_kitchen_dining_door" '
            'd="M 742.0 493.0 L 720.0 493.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="hallway_to_kitchen_dining_door" '
            'd="M 742.0 515.0 A 22.0 22.0 0 0 1 720.0 493.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="kitchen_dining_to_bedroom2_door" '
            'd="M 762.0 523.0 L 762.0 545.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="kitchen_dining_to_bedroom2_door" '
            'd="M 784.0 523.0 A 22.0 22.0 0 0 1 762.0 545.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="entrance_to_kitchen_dining_door" '
            'd="M 784.0 522.0 L 762.0 522.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="entrance_to_kitchen_dining_door" '
            'd="M 784.0 500.0 A 22.0 22.0 0 0 0 762.0 522.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-leaf photo-reference" data-ref-door-leaf="laundry_to_toilet_door" '
            'd="M 896.0 580.0 L 896.0 596.0"',
            svg,
        )
        self.assertIn(
            'class="ref-door-arc photo-reference" data-ref-door-arc="laundry_to_toilet_door" '
            'd="M 912.0 580.0 A 16.0 16.0 0 0 1 896.0 596.0"',
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
            'x="706.0" y="522.0" width="22.0" height="2.0"',
            svg,
        )
        self.assertIn(
            'class="ref-pocket-door-casing" data-ref-pocket-door-casing="hallway_to_bathroom_sliding_door" '
            'x="722.0" y="520.3" width="36.0" height="5.4"',
            svg,
        )
        self.assertIn(
            'class="ref-pocket-door-slot" data-ref-pocket-door-slot="hallway_to_bathroom_sliding_door" '
            'x="725.0" y="522.0" width="30.0" height="2.0"',
            svg,
        )
        self.assertNotIn('class="ref-pocket-door-recess"', svg)
        self.assertNotIn('data-ref-window="hallway_to_bathroom_sliding_door"', svg)
        self.assertNotIn('data-ref-opening-cutout="hallway_to_master_bedroom_door"', svg)
        self.assertNotIn('data-ref-opening-cutout="hallway_to_lounge_door"', svg)
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
        self.assertIn('data-ref-wall="hallway_south_wall"', svg)
        self.assertIn('data-ref-wall="bedroom2_north_wall"', svg)
        self.assertIn('data-ref-wall="entrance_laundry_wall"', svg)
        self.assertIn('data-ref-wall="entrance_deck_wall"', svg)
        self.assertIn('data-ref-wall="kitchen_entrance_return_wall"', svg)
        self.assertIn('data-ref-wall="private_rooms_south_wall"', svg)
        self.assertIn('data-ref-wall="sunroom_glazing_frame"', svg)
        self.assertIn('data-ref-wall="sunroom_glazing_frame" data-ref-wall-class="interior" d="M536 486 H646 V360 H597 V408 L552 452 H536 Z"', svg)
        self.assertNotIn('data-ref-wall="sunroom_exterior" data-ref-wall-class="exterior"', svg)
        self.assertIn('data-ref-wall="master_sunroom_old_external_wall"', svg)
        self.assertIn('data-ref-wall="master_sunroom_old_external_wall" data-ref-wall-class="exterior" d="M518 485 H608"', svg)
        self.assertIn('data-ref-wall="master_office_wall" data-ref-wall-class="interior" d="M608 485 V494 M608 516 V610"', svg)
        self.assertIn('data-ref-wall="hallway_north_wall" data-ref-wall-class="exterior" d="M608 485 H638"', svg)
        self.assertIn('data-ref-wall="lounge_hallway_wall" data-ref-wall-class="interior" d="M638 489 H683 M705 489 H742"', svg)
        self.assertIn('data-ref-wall="hallway_kitchen_door_wall" data-ref-wall-class="interior" d="M742 515 V523"', svg)
        self.assertIn('data-ref-wall="dining_west_external_wall"', svg)
        self.assertIn('data-ref-wall="dining_west_external_wall" data-ref-wall-class="exterior" d="M742 314 V365"', svg)
        self.assertIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 365 V314 H822 V496"', svg)
        self.assertIn('data-ref-wall="entrance_deck_wall" data-ref-wall-class="exterior" d="M822 496 H836 M877 496 H940"', svg)
        self.assertIn('data-ref-wall="kitchen_entrance_return_wall" data-ref-wall-class="interior" d="M822 496 H784"', svg)
        self.assertNotIn('data-ref-wall="laundry_north_wall" data-ref-wall-class="interior" d="M890 500 H940"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 314 H822 V496 H800"', svg)
        self.assertNotIn('data-ref-wall="kitchen_east_wall" data-ref-wall-class="exterior" d="M742 365 V314 H822 V496 H800"', svg)
        self.assertIn(
            'class="wall-core exterior structural" data-ref-wall-class="exterior" '
            'd="M638 358 H742 M742 365 V314 H822 V496 M822 496 H836 M877 496 H940 V610 H518 V485 H638"',
            svg,
        )
        self.assertNotIn("M877 496 H940 M638 485 H518 V610 H940 V496", svg)
        self.assertIn('d="M638 489 H683 M705 489 H742"', svg)
        self.assertIn('d="M608 523 H657 M679 523 H688 M722 523 H758"', svg)
        self.assertIn('d="M890 500 V504 M890 524.1 V580"', svg)
        self.assertIn('d="M758 523 H762 M784 523 H890"', svg)
        self.assertNotIn('data-ref-manual-openings="open-plan-room-gaps"', svg)
        self.assertNotIn('data-ref-passage="kitchen_to_hallway_gap"', svg)
        self.assertIn('data-ref-wall="lounge_kitchen_divider"', svg)
        self.assertIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M742 395 V493"', svg)
        self.assertIn('data-ref-wall="laundry_toilet_wall" data-ref-wall-class="interior" d="M890 580 H896 M912 580 H940"', svg)
        self.assertIn('data-ref-wall="kitchen_entrance_door_wall" data-ref-wall-class="interior" d="M784 500 V501 M784 522 V523"', svg)
        self.assertNotIn('data-ref-wall="lounge_kitchen_divider" data-ref-wall-class="interior" d="M742 395 V500"', svg)
        self.assertNotIn('d="M742 314 V365 M742 395 V500"', svg)
        self.assertNotIn('data-ref-passage="lounge_to_kitchen_gap"', svg)
        self.assertNotIn('data-ref-wall-space="kitchen_dining"', svg)

    def test_reference_plan_uses_subdued_room_labels_and_materials(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('pattern id="floorboards-subtle"', svg)
        self.assertIn('fill="#f4eee8"', svg)
        self.assertIn('stroke="#dfcdb6" stroke-width="0.45" opacity="0.28"', svg)
        self.assertIn('pattern id="deck-boards-subtle"', svg)
        self.assertIn('pattern id="lawn-soft"', svg)
        self.assertIn('class="ref-room-label"', svg)
        self.assertIn("font-size: 9px;", svg)
        self.assertIn(".ref-room-label, .ref-site-label { text-anchor: middle; dominant-baseline: middle; font-weight: 500; }", svg)
        self.assertNotIn("paint-order: stroke", svg)
        self.assertIn('class="ref-room-label" x="690.0" y="392.0"', svg)
        self.assertIn('class="ref-room-label" x="563.0" y="512.0"', svg)
        self.assertIn(">Kitchen / Dining<", svg)
        self.assertNotIn(">Rear Timber Deck<", svg)

    def test_reference_plan_includes_metric_scale_bar_near_house(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('id="reference-scale-layer"', svg)
        self.assertIn('data-scale-source="internal-door-0.81m"', svg)
        self.assertIn('data-scale-metres="2"', svg)
        self.assertIn('data-scale-px="54.3"', svg)
        self.assertIn('<text class="ref-scale-label" x="985.2" y="621.0">2 m</text>', svg)
        self.assertIn('<line class="ref-scale-line" x1="958.0" y1="628.0" x2="1012.3" y2="628.0"/>', svg)

    def test_reference_plan_shows_subdued_furniture_for_visual_context(self):
        model = load_model("DATA/house_model.json")
        svg = render_reference_plan_svg(model)

        self.assertIn('id="furniture-layer"', svg)
        self.assertIn('data-furniture="dining_table"', svg)
        self.assertIn('data-furniture="lounge_seating"', svg)
        self.assertIn('data-furniture="garage_car_pair"', svg)
        self.assertIn('data-furniture="kitchen_island"', svg)
        self.assertIn('cx="868" cy="438" r="12"', svg)
        self.assertIn('x="894" y="456" width="34" height="20"', svg)
        self.assertNotIn('x="918" y="424" width="42" height="22"', svg)
        self.assertIn(".furniture", svg)
        self.assertIn('filter id="object-soft-shadow"', svg)
        self.assertNotIn('data-furniture="kitchen_cabinetry"', svg)
