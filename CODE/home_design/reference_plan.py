from __future__ import annotations

from html import escape
from math import cos, hypot, radians, sin
from typing import Any

from .model import HouseModel
from .presentation_plan import CANVAS_HEIGHT, CANVAS_WIDTH, ROOM_LABELS, SITE_LABELS


OPENING_TYPES = {"window", "window_group", "slider", "door_group", "door", "sliding_door", "opening"}
WALL_THICKNESS_OVERRIDES_M = {
    "entrance_deck_wall": "0.14",
    "kitchen_entrance_return_wall": "0.13",
    "master_office_wall": "0.125",
    "wardrobe_office_wall": "0.125",
    "office_bathroom_wall": "0.125",
    "bathroom_bedroom2_wall": "0.125",
    "laundry_toilet_wall": "0.12",
    "toilet_south_external_wall": "0.27",
}

WALL_PROJECTION_OVERRIDES_M = {
    "kitchen_lounge_nub": "0.47",
}
VINYL_PLANK_ROOM_IDS = {"kitchen_dining", "entrance", "laundry", "toilet"}
TILE_ROOM_IDS = {"bathroom"}
VINYL_PLANK_PASSAGE_IDS = {"entrance_to_laundry_opening", "hallway_to_entrance_laundry"}
WALL_JUNCTION_CAPS = [
    ("sunroom_lounge_upper_wall_fill", 659.1, 344.8, 8.0, 8.0),
    ("sunroom_lounge_lower_wall_fill", 659.1, 460.0, 8.0, 24.6),
    ("entrance_return_thin_square_end", 801.9, 494.3, 35.1, 3.3),
    ("kitchen_entrance_external_wall_flat_bottom", 829.0, 302.3, 8.0, 193.6),
]

LABEL_OVERRIDES = {
    "lounge": (710.0, 389.4),
    "kitchen_dining": (796.5, 372.0),
    "master_bedroom": (580.5, 512.0),
    "office": (687.0, 554.0),
    "bedroom_2": (838.4, 592.0),
    "laundry": (929.6, 558.0),
    "hallway": (684.0, 504.0),
}

CURATED_WALL_PATHS = [
    ("sunroom_glazing_frame", "interior", "M549.2 483.4 V442.3 H568 M606 401.6 V346.7 H663.1"),
    ("lounge_exterior", "exterior", "M659.1 348.8 H762.8"),
    ("lounge_sunroom_wall", "exterior", "M663.1 348.8 V377.8"),
    ("lounge_sunroom_lower_wall_trim", "exterior", "M663.1 460 V484.6"),
    ("master_sunroom_old_external_wall", "exterior", "M533.9 482.4 H627.1"),
    ("hallway_north_wall", "exterior", "M627.1 482.4 H635.2"),
    ("hallway_sunroom_right_jamb", "exterior", "M655.4 482.4 H663.1"),
    ("lounge_hallway_wall", "interior", "M663.1 484.6 H701.5 M723.5 484.6 H760.9"),
    ("kitchen_east_wall", "exterior", "M758.8 348.8 V302.3 H833 V491.9"),
    ("entrance_deck_wall", "thin-exterior", "M834.3 489.1 H841.9 M881.8 489.1 H956.4"),
    ("kitchen_entrance_return_wall", "thin-interior", "M834.3 489.1 V495.9 H803.7"),
    ("private_rooms_south_wall", "exterior", "M533.9 601.8 H902.8"),
    ("toilet_south_external_wall", "toilet-exterior", "M900.6 602.2 H960.4"),
    ("bedroom2_east_wall", "interior", "M902.8 516.1 V602.2"),
    ("master_west_wall", "exterior", "M533.9 482.4 V601.8"),
    ("dining_west_external_wall", "exterior", "M758.8 302.3 V348.8"),
    ("kitchen_lounge_nub", "interior", "M760.9 348.8 V361.3"),
    ("lounge_kitchen_divider", "interior", "M760.9 392.4 V493"),
    ("hallway_south_wall", "interior", "M627.1 523 H695.5 M717.3 523 H727.1 M743.4 523 H773.9"),
    ("hallway_kitchen_door_wall", "interior", "M760.9 515 V523"),
    ("bedroom2_north_wall", "thin-interior", "M773.9 523.3 H778.6 M800.6 523.3 H902.8"),
    ("master_office_wall", "thin-interior", "M627.1 482.4 V494 M627.1 516 V527 M627.1 558 V567 M627.1 598 V601.8"),
    ("wardrobe_office_wall", "thin-interior", "M646.8 523 V601.8"),
    ("office_bathroom_wall", "thin-interior", "M727.1 521.2 V601.8"),
    ("bathroom_bedroom2_wall", "thin-interior", "M773.9 523 V601.8"),
    ("entrance_laundry_wall", "interior", "M902.8 489.1 V496.5"),
    ("laundry_toilet_wall", "thin-interior", "M902.8 572.9 H908.8 M924.8 572.9 H956.4"),
    ("kitchen_entrance_door_wall", "interior", "M803.7 495.9 V499.7 M803.7 519.5 V523.3"),
    ("laundry_toilet_exterior", "exterior", "M956.4 487.3 V602.2"),
]

VISIBLE_WALL_PATHS = {
    "exterior": [
        "M659.1 348.8 H762.8",
        "M663.1 348.8 V377.8",
        "M663.1 460 V484.6",
        "M758.8 348.8 V302.3 H833 V491.9",
        "M956.4 487.3 V602.2 M902.8 601.8 H533.9 V482.4 H635.2 M655.4 482.4 H663.1",
    ],
}

INTERNAL_OPENING_IDS = {
    "sunroom_front_double_doors",
    "sunroom_wraparound_glazing",
    "sunroom_lounge_slider",
    "hallway_to_lounge_door",
    "hallway_to_sunroom_old_front_door",
    "hallway_to_kitchen_dining_door",
    "hallway_to_bathroom_sliding_door",
    "hallway_to_master_bedroom_door",
    "hallway_to_office_door",
    "kitchen_dining_to_bedroom2_door",
    "entrance_to_kitchen_dining_door",
    "laundry_to_toilet_door",
    "bedroom2_entrance_internal_window",
}

INTERNAL_DOOR_WIDTH_PX = 22.0
INTERNAL_SCALE_SPANS_PX_M = (
    (22.0, 0.81),  # Standard internal door.
    (46.2, 1.70),  # Entrance sliding door span.
    (34.5, 1.27),  # Legacy entrance calibration span retained for the averaged scale marker.
    (6.8, 0.25),  # Entrance widening return.
    (20.1, 0.74),  # Entrance to laundry opening.
    (16.0, 0.588),  # Toilet door.
    (82.2, 3.15),  # Sunroom to lounge sliding door.
    (127.0, 4.87),  # Sunroom/living wall sequence.
)
REFERENCE_PX_PER_M = sum(px for px, _ in INTERNAL_SCALE_SPANS_PX_M) / sum(
    metres for _, metres in INTERNAL_SCALE_SPANS_PX_M
)
EXTERIOR_WALL_STROKE_PX = round(REFERENCE_PX_PER_M * 0.30, 1)
INTERIOR_WALL_STROKE_PX = round(REFERENCE_PX_PER_M * 0.14, 1)
THIN_EXTERIOR_WALL_STROKE_PX = round(REFERENCE_PX_PER_M * 0.14, 1)
TRIMMED_EXTERIOR_WALL_STROKE_PX = 6.0
THIN_INTERIOR_WALL_STROKE_PX = round(REFERENCE_PX_PER_M * 0.125, 1)
TOILET_EXTERIOR_WALL_STROKE_PX = round(REFERENCE_PX_PER_M * 0.27, 1)
EXTERIOR_WALL_HALF_PX = EXTERIOR_WALL_STROKE_PX / 2
INTERIOR_WALL_HALF_PX = INTERIOR_WALL_STROKE_PX / 2
THIN_EXTERIOR_WALL_HALF_PX = THIN_EXTERIOR_WALL_STROKE_PX / 2
THIN_INTERIOR_WALL_HALF_PX = THIN_INTERIOR_WALL_STROKE_PX / 2
TOILET_EXTERIOR_WALL_HALF_PX = TOILET_EXTERIOR_WALL_STROKE_PX / 2
POCKET_DOOR_IDS = {"hallway_to_bathroom_sliding_door"}
POCKET_DOOR_POCKET_CENTERLINES = {
    "hallway_to_bathroom_sliding_door": (743.4, 523.0, 773.9, 523.0),
}

PHOTO_REFERENCE_DOOR_IDS = {
    "hallway_to_lounge_door",
    "hallway_to_sunroom_old_front_door",
    "hallway_to_kitchen_dining_door",
    "hallway_to_master_bedroom_door",
    "hallway_to_office_door",
    "kitchen_dining_to_bedroom2_door",
    "entrance_to_kitchen_dining_door",
    "laundry_to_toilet_door",
}
PHOTO_REFERENCE_HORIZONTAL_DOWN_DOOR_IDS = {
    "hallway_to_office_door",
    "kitchen_dining_to_bedroom2_door",
    "laundry_to_toilet_door",
    "hallway_to_sunroom_old_front_door",
}
PHOTO_REFERENCE_HORIZONTAL_UP_DOOR_IDS = {"hallway_to_lounge_door"}
PHOTO_REFERENCE_VERTICAL_LEFT_DOOR_IDS = {"hallway_to_master_bedroom_door"}
PHOTO_REFERENCE_VERTICAL_LEFT_UPPER_HINGE_DOOR_IDS = {
    "hallway_to_kitchen_dining_door",
}
PHOTO_REFERENCE_VERTICAL_LEFT_LOWER_HINGE_DOOR_IDS = {
    "entrance_to_kitchen_dining_door",
}
PHOTO_REFERENCE_VERTICAL_RIGHT_DOOR_IDS: set[str] = set()
DOUBLE_DOOR_GROUP_IDS = {"deck_door_group", "sunroom_front_double_doors"}
DOOR_GROUP_IDS_WITHOUT_CUTOUT = {"sunroom_front_double_doors"}
TIMBER_OPENING_CUTOUT_IDS = {"deck_door_group"}
SLIDING_DOOR_SYMBOL_IDS = {"entrance_deck_slider", "sunroom_lounge_slider"}

OPENING_CENTERLINE_OVERRIDES = {
    "deck_door_group": [(833.0, 350.8, 833.0, 393.8)],
    "deck_side_dining_window": [(833.0, 332.5, 833.0, 347.7)],
    "entrance_deck_slider": [(881.8, 489.1, 841.9, 489.1)],
    "sunroom_front_double_doors": [(606.0, 401.6, 568.0, 442.3)],
    "sunroom_wraparound_glazing": [
        (610.0, 346.7, 655.2, 346.7),
        (606.0, 354.7, 606.0, 393.6),
        (556.0, 442.3, 568.0, 442.3),
        (549.2, 446.3, 549.2, 473.5),
    ],
    "lounge_north_left_window": [(675.8, 348.8, 687.2, 348.8)],
    "lounge_north_right_window": [(742.7, 348.8, 731.3, 348.8)],
    "dining_west_window": [(758.8, 316.8, 758.8, 334.3)],
    "laundry_north_window": [(914.0, 489.1, 950.6, 489.1)],
    "laundry_east_window": [(956.4, 514.3, 956.4, 543.5)],
    "toilet_frosted_window": [(956.4, 580.7, 956.4, 594.4)],
    "master_street_window": [(534.9, 514.0, 534.9, 571.0)],
    "master_rear_high_window": [(589.6, 601.8, 571.4, 601.8)],
    "master_sunroom_window": [(608.9, 482.4, 552.1, 482.4)],
    "hallway_to_lounge_door": [(701.5, 484.6, 723.5, 484.6)],
    "hallway_to_sunroom_old_front_door": [(635.2, 482.4, 655.4, 482.4)],
    "hallway_to_kitchen_dining_door": [(760.9, 493.0, 760.9, 515.0)],
    "hallway_to_bathroom_sliding_door": [(727.1, 523.0, 743.4, 523.0)],
    "hallway_to_master_bedroom_door": [(627.1, 494.0, 627.1, 516.0)],
    "hallway_to_office_door": [(717.3, 523.0, 695.5, 523.0)],
    "kitchen_dining_to_bedroom2_door": [(778.6, 523.3, 800.6, 523.3)],
    "entrance_to_kitchen_dining_door": [(803.7, 499.7, 803.7, 519.5)],
    "laundry_to_toilet_door": [(908.8, 572.9, 924.8, 572.9)],
    "office_se_window": [(701.1, 601.8, 672.8, 601.8)],
    "bathroom_se_window": [(765.1, 601.8, 735.9, 601.8)],
    "bedroom2_se_window": [(864.8, 601.8, 811.7, 601.8)],
    "bedroom2_entrance_internal_window": [(878.7, 523.3, 854.4, 523.3)],
}

WINDOW_GUIDE_OFFSET_PX = 2.0

def _dimension_annotation(
    dimension_id: str,
    kind: str,
    label: str,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    offset_x: float,
    offset_y: float,
    confidence: str,
    source: str,
) -> dict[str, Any]:
    return {
        "id": dimension_id,
        "kind": kind,
        "label": label,
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "offset_x": offset_x,
        "offset_y": offset_y,
        "confidence": confidence,
        "source": source,
    }


DIMENSION_ANNOTATIONS = [
    _dimension_annotation("overall-master-to-laundry", "external", "16.10 m", 533.9, 617.8, 960.4, 617.8, 0.0, 44.0, "measured", "anchor:long_side_master_to_laundry"),
    _dimension_annotation("overall-external-depth", "external", "11.58 m", 984.4, 302.3, 984.4, 602.2, 44.0, 0.0, "measured", "anchor:combined_external_depth"),
    _dimension_annotation("sunroom-approx-span", "external", "~4.87 m", 533.9, 326.0, 663.1, 326.0, 0.0, -24.0, "approximate", "room:sunroom.reference_position"),
    _dimension_annotation("kitchen-dining-clear-length", "internal", "8.12 m", 833.0 - EXTERIOR_WALL_HALF_PX, 302.3 + EXTERIOR_WALL_HALF_PX, 833.0 - EXTERIOR_WALL_HALF_PX, 523.3 - THIN_INTERIOR_WALL_HALF_PX, 34.0, 0.0, "measured", "room:kitchen_dining.length"),
    _dimension_annotation("kitchen-dining-clear-width", "internal", "2.50 m", 760.9 + INTERIOR_WALL_HALF_PX, 302.3 + EXTERIOR_WALL_HALF_PX, 833.0 - EXTERIOR_WALL_HALF_PX, 302.3 + EXTERIOR_WALL_HALF_PX, 0.0, -32.0, "measured", "room:kitchen_dining.width"),
    _dimension_annotation("lounge-clear-length", "internal", "4.90 m", 659.1 + INTERIOR_WALL_HALF_PX, 348.8 + EXTERIOR_WALL_HALF_PX, 659.1 + INTERIOR_WALL_HALF_PX, 484.6 - INTERIOR_WALL_HALF_PX, 0.0, 0.0, "measured", "room:lounge.length"),
    _dimension_annotation("lounge-clear-width", "internal", "3.70 m", 659.1 + INTERIOR_WALL_HALF_PX, 348.8 + EXTERIOR_WALL_HALF_PX, 760.9 - INTERIOR_WALL_HALF_PX, 348.8 + EXTERIOR_WALL_HALF_PX, 0.0, -24.0, "measured", "room:lounge.width"),
    _dimension_annotation("hallway-clear-length", "internal", "4.80 m", 627.1 + EXTERIOR_WALL_HALF_PX, 484.6 + INTERIOR_WALL_HALF_PX, 760.9 - INTERIOR_WALL_HALF_PX, 484.6 + INTERIOR_WALL_HALF_PX, 0.0, -22.0, "measured", "room:hallway.length"),
    _dimension_annotation("hallway-clear-width", "internal", "1.30 m", 627.1 + EXTERIOR_WALL_HALF_PX, 484.6 + INTERIOR_WALL_HALF_PX, 627.1 + EXTERIOR_WALL_HALF_PX, 523.0 - INTERIOR_WALL_HALF_PX, -20.0, 0.0, "measured", "room:hallway.width"),
    _dimension_annotation("master-bedroom-clear-length", "internal", "3.30 m", 533.9 + EXTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, 627.1 - THIN_INTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, 0.0, 22.0, "measured", "room:master_bedroom.length"),
    _dimension_annotation("master-bedroom-clear-width", "internal", "4.20 m", 533.9 + EXTERIOR_WALL_HALF_PX, 482.4 + EXTERIOR_WALL_HALF_PX, 533.9 + EXTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, -28.0, 0.0, "measured", "room:master_bedroom.width"),
    _dimension_annotation("wardrobe-bay-depth", "built_in", "0.62 m", 627.1 + THIN_INTERIOR_WALL_HALF_PX, 609.5, 646.8 - THIN_INTERIOR_WALL_HALF_PX, 609.5, 0.0, 16.0, "measured", "built_in:master_bedroom_wardrobe"),
    _dimension_annotation("office-clear-length", "internal", "2.90 m", 646.8 + THIN_INTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, 727.1 - THIN_INTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, 0.0, 22.0, "measured", "room:office.length"),
    _dimension_annotation("office-clear-width", "internal", "2.75 m", 646.8 + THIN_INTERIOR_WALL_HALF_PX, 523.0 + THIN_INTERIOR_WALL_HALF_PX, 646.8 + THIN_INTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, -15.7, 0.0, "measured", "room:office.width"),
    _dimension_annotation("bathroom-clear-length", "internal", "1.64 m", 727.1 + THIN_INTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, 773.9 - THIN_INTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, 0.0, 22.0, "measured", "room:bathroom.length"),
    _dimension_annotation("bathroom-clear-width", "internal", "2.75 m", 773.9 - THIN_INTERIOR_WALL_HALF_PX, 523.0 + THIN_INTERIOR_WALL_HALF_PX, 773.9 - THIN_INTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, 15.7, 0.0, "measured", "room:bathroom.width"),
    _dimension_annotation("bedroom-2-clear-length", "internal", "4.73 m", 773.9 + THIN_INTERIOR_WALL_HALF_PX, 546.0, 902.8 - INTERIOR_WALL_HALF_PX, 546.0, 0.0, -16.0, "measured", "room:bedroom_2.length"),
    _dimension_annotation("bedroom-2-clear-width", "internal", "2.75 m", 902.8 - INTERIOR_WALL_HALF_PX, 523.3 + THIN_INTERIOR_WALL_HALF_PX, 902.8 - INTERIOR_WALL_HALF_PX, 601.8 - EXTERIOR_WALL_HALF_PX, -16.2, 0.0, "measured", "room:bedroom_2.width"),
    _dimension_annotation("entrance-clear-length", "internal", "3.70 m", 803.7 + THIN_INTERIOR_WALL_HALF_PX, 489.1 + THIN_EXTERIOR_WALL_HALF_PX, 902.8 - INTERIOR_WALL_HALF_PX, 489.1 + THIN_EXTERIOR_WALL_HALF_PX, 0.0, -19.9, "measured", "room:entrance.length"),
    _dimension_annotation("entrance-clear-width", "internal", "1.16 m", 902.8 - INTERIOR_WALL_HALF_PX, 489.1 + THIN_EXTERIOR_WALL_HALF_PX, 902.8 - INTERIOR_WALL_HALF_PX, 523.3 - THIN_INTERIOR_WALL_HALF_PX, 17.9, 0.0, "measured", "room:entrance.width"),
    _dimension_annotation("laundry-clear-length", "internal", "3.03 m", 956.4 - EXTERIOR_WALL_HALF_PX, 489.1 + THIN_EXTERIOR_WALL_HALF_PX, 956.4 - EXTERIOR_WALL_HALF_PX, 572.9 - THIN_INTERIOR_WALL_HALF_PX, 28.0, 0.0, "measured", "room:laundry.length"),
    _dimension_annotation("laundry-clear-width", "internal", "1.80 m", 902.8 + INTERIOR_WALL_HALF_PX, 489.1 + THIN_EXTERIOR_WALL_HALF_PX, 956.4 - EXTERIOR_WALL_HALF_PX, 489.1 + THIN_EXTERIOR_WALL_HALF_PX, 0.0, -29.9, "measured", "room:laundry.width"),
    _dimension_annotation("toilet-clear-length", "internal", "0.91 m", 956.4 - EXTERIOR_WALL_HALF_PX, 572.9 + THIN_INTERIOR_WALL_HALF_PX, 956.4 - EXTERIOR_WALL_HALF_PX, 602.2 - TOILET_EXTERIOR_WALL_HALF_PX, 28.0, 0.0, "measured", "room:toilet.length"),
    _dimension_annotation("toilet-clear-width", "internal", "1.80 m", 902.8 + INTERIOR_WALL_HALF_PX, 602.2 - TOILET_EXTERIOR_WALL_HALF_PX, 956.4 - EXTERIOR_WALL_HALF_PX, 602.2 - TOILET_EXTERIOR_WALL_HALF_PX, 0.0, 23.6, "measured", "room:toilet.width"),
]

def render_reference_plan_svg(model: HouseModel) -> str:
    current_structure = model.raw.get("current_structure", {})
    current_site = model.raw.get("current_site", {})
    spaces = current_structure.get("spaces", [])
    built_ins = current_structure.get("built_ins", [])
    features = current_structure.get("features", [])
    site_elements = current_site.get("elements", [])

    parts = [
        f'<svg id="presentation-plan" data-render-style="reference-plan" xmlns="http://www.w3.org/2000/svg" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}">',
        "<defs>",
        _reference_defs(),
        "</defs>",
        "<style>",
        _reference_css(),
        "</style>",
        '<rect width="100%" height="100%" fill="#f6f4ef"/>',
        _render_site_layer(site_elements),
        _render_floor_layer(spaces),
        _render_built_in_layer(built_ins),
        _render_passage_layer(features),
        _render_wall_layer(),
        _render_opening_layer(features),
        _render_scale_layer(),
        _render_orientation_layer(model.raw.get("orientation", {})),
        _render_dimension_layer(),
        _render_label_layer(spaces, site_elements),
        "</svg>",
    ]
    return "\n".join(parts)


def _reference_defs() -> str:
    return """
<pattern id="vinyl-planks-vertical" width="22" height="46" patternUnits="userSpaceOnUse">
  <rect width="22" height="46" fill="#bda684"/>
  <path d="M7 0 V46 M15 0 V46" stroke="#92785c" stroke-width="0.55" opacity="0.62"/>
  <path d="M0 15 H7 M15 31 H22" stroke="#a48b6a" stroke-width="0.5" opacity="0.55"/>
</pattern>
<pattern id="carpet-light-brown" width="18" height="18" patternUnits="userSpaceOnUse">
  <rect width="18" height="18" fill="#efe4d2"/>
  <path d="M3 5 H5 M8 12 H10 M13 7 H15 M1 15 H2" stroke="#d9c4a5" stroke-width="0.45" opacity="0.32"/>
  <path d="M5 2 H6 M11 4 H13 M15 14 H16" stroke="#fbf4ea" stroke-width="0.4" opacity="0.42"/>
</pattern>
<pattern id="deck-boards-subtle" width="22" height="22" patternUnits="userSpaceOnUse">
  <rect width="22" height="22" fill="#9a5f33"/>
  <path d="M0 5 H22 M0 13 H22 M0 21 H22" stroke="#764721" stroke-width="0.8" opacity="0.55"/>
</pattern>
<pattern id="lawn-soft" width="26" height="26" patternUnits="userSpaceOnUse">
  <rect width="26" height="26" fill="#79b764"/>
  <path d="M4 22 L10 4 M17 25 L21 7" stroke="#5da04c" stroke-width="1.1" opacity="0.35"/>
</pattern>
<pattern id="pavers-soft" width="38" height="27" patternUnits="userSpaceOnUse">
  <rect width="38" height="27" fill="#ddd8cd"/>
  <path d="M0 9 H38 M0 19 H38 M12 0 V9 M26 9 V19 M16 19 V27" stroke="#bab3a6" stroke-width="0.8" opacity="0.65"/>
</pattern>
<pattern id="tile-soft" width="34" height="34" patternUnits="userSpaceOnUse">
  <rect width="34" height="34" fill="#eef1f0"/>
  <path d="M0 0 L34 34 M34 0 L0 34" stroke="#cfd6d6" stroke-width="1" opacity="0.75"/>
</pattern>
""".strip()


def _reference_css() -> str:
    css = """
text { font-family: Arial, sans-serif; fill: #1d2522; }
.ref-site { stroke-linejoin: round; }
.ref-site.boundary { fill: url(#lawn-soft); stroke: #6b7867; stroke-width: 4; }
.ref-site.planting { fill: url(#lawn-soft); stroke: #4f8d43; stroke-width: 1.8; opacity: 0.85; }
.ref-site.hardscape { fill: url(#pavers-soft); stroke: #b6ac9d; stroke-width: 1.5; }
.ref-site.deck { fill: url(#deck-boards-subtle); stroke: #714927; stroke-width: 2; }
.ref-site.building { fill: #d9dece; stroke: #697466; stroke-width: 2.2; }
.ref-floor { stroke: none; fill: url(#carpet-light-brown); }
.ref-floor.carpet { fill: url(#carpet-light-brown); }
.ref-floor.vinyl-plank { fill: url(#vinyl-planks-vertical); }
.ref-floor.tile { fill: url(#tile-soft); }
.ref-built-in.wardrobe { fill: #d9c39f; stroke: #9d8560; stroke-width: 0.8; }
.ref-built-in-wardrobe-divider { fill: #585b63; stroke: none; }
.wall-core, .wall-reference { fill: none; stroke-linecap: butt; stroke-linejoin: miter; }
.wall-core.exterior { stroke: #585b63; stroke-width: __EXTERIOR_WALL_STROKE__; }
.wall-core.thin-exterior { stroke: #585b63; stroke-width: __THIN_EXTERIOR_WALL_STROKE__; }
.wall-core.trimmed-exterior { stroke: #585b63; stroke-width: __TRIMMED_EXTERIOR_WALL_STROKE__; }
.wall-core.toilet-exterior { stroke: #585b63; stroke-width: __TOILET_EXTERIOR_WALL_STROKE__; }
.wall-core.interior { stroke: #585b63; stroke-width: __INTERIOR_WALL_STROKE__; }
.wall-core.thin-interior { stroke: #585b63; stroke-width: __THIN_INTERIOR_WALL_STROKE__; }
.wall-junction-cap { fill: #585b63; stroke: none; }
.wall-reference { display: none; }
.opening-cutout { fill: none; stroke: #fffdf8; stroke-linecap: butt; }
.opening-cutout.exterior { stroke-width: 9px; }
.opening-cutout.interior { stroke-width: 5px; }
.opening-cutout.timber { stroke: url(#vinyl-planks-vertical); }
.opening-cutout.deck { stroke: url(#deck-boards-subtle); }
.opening-cutout.threshold { stroke-width: 7px; }
.opening-passage-fill { fill: #eee7d9; stroke: none; }
.opening-passage-fill.vinyl-plank { fill: url(#vinyl-planks-vertical); }
.opening-passage-fill.carpet { fill: url(#carpet-light-brown); }
.opening-passage-fill.circulation { fill: #eee7d9; }
.ref-window-cutout { fill: none; stroke: #fffdf8; stroke-linecap: butt; }
.ref-window-cutout.exterior { stroke-width: 8px; }
.ref-window-cutout.exterior[data-ref-window="laundry_north_window"] { stroke-width: 2px; }
.ref-window-cutout.internal { stroke-width: 4px; }
.ref-window-cutout.internal[data-ref-window="bedroom2_entrance_internal_window"] { stroke-width: 2px; }
.ref-window-guide { fill: none; stroke: #777b80; stroke-width: 0.9; stroke-linecap: butt; }
.ref-sliding-door-panel { fill: #fffdf8; stroke: #111; stroke-width: 0.45; }
.ref-opening-jamb { stroke: #585b63; stroke-width: 1.8; stroke-linecap: butt; }
.ref-pocket-door-panel { fill: #fffdf8; stroke: #2f3134; stroke-width: 0.45; }
.ref-pocket-door-casing { fill: #2f3134; stroke: none; }
.ref-pocket-door-slot { fill: #fffdf8; stroke: none; }
.ref-door-leaf { fill: none; stroke: #111; stroke-width: 1.4; stroke-linecap: round; }
.ref-door-arc { fill: none; stroke: #111; stroke-width: 1.1; stroke-dasharray: 4 4; stroke-linecap: round; }
.ref-door-leaf.photo-reference { stroke: #111; stroke-width: 1.8; stroke-linecap: butt; }
.ref-door-arc.photo-reference { stroke: #111; stroke-width: 0.95; }
.ref-room-label, .ref-site-label { text-anchor: middle; dominant-baseline: middle; font-weight: 500; }
.ref-room-label { font-size: 9px; }
.ref-site-label { font-size: 8px; fill: #243029; }
.ref-scale-line, .ref-scale-tick { stroke: #2f3134; stroke-width: 1.1; stroke-linecap: butt; }
.ref-scale-label { font-size: 7px; text-anchor: middle; dominant-baseline: auto; fill: #2f3134; }
.ref-dimension-line, .ref-dimension-extension, .ref-dimension-tick { stroke: #263238; stroke-width: 0.85; stroke-linecap: butt; fill: none; }
.ref-dimension-extension { opacity: 0.58; }
.ref-dimension-label-bg { fill: #fffdf8; stroke: #d3cabd; stroke-width: 0.55; opacity: 0.96; }
.ref-dimension-label-bg.approximate { fill: #fff8e4; stroke: #b3893c; }
.ref-dimension-label { font-size: 7px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; fill: #263238; paint-order: stroke; stroke: #fffdf8; stroke-width: 3px; stroke-linejoin: round; }
.ref-dimension-label.approximate { fill: #7a5a1f; }
.ref-dimension-group.approximate .ref-dimension-line, .ref-dimension-group.approximate .ref-dimension-tick { stroke-dasharray: 3 2; stroke: #7a5a1f; }
.ref-compass-axis { stroke: #2f3134; stroke-width: 1.1; stroke-linecap: round; }
.ref-compass-secondary { stroke: #2f3134; stroke-width: 0.7; stroke-linecap: round; opacity: 0.58; }
.ref-compass-arrow { fill: #2f3134; stroke: none; }
.ref-compass-label { font-size: 7px; text-anchor: middle; dominant-baseline: middle; fill: #2f3134; }
.ref-compass-label.primary { font-weight: 700; font-size: 8px; }
""".strip()
    return (
        css.replace("__EXTERIOR_WALL_STROKE__", _css_px(EXTERIOR_WALL_STROKE_PX))
        .replace("__THIN_EXTERIOR_WALL_STROKE__", _css_px(THIN_EXTERIOR_WALL_STROKE_PX))
        .replace("__TRIMMED_EXTERIOR_WALL_STROKE__", _css_px(TRIMMED_EXTERIOR_WALL_STROKE_PX))
        .replace("__TOILET_EXTERIOR_WALL_STROKE__", _css_px(TOILET_EXTERIOR_WALL_STROKE_PX))
        .replace("__INTERIOR_WALL_STROKE__", _css_px(INTERIOR_WALL_STROKE_PX))
        .replace("__THIN_INTERIOR_WALL_STROKE__", _css_px(THIN_INTERIOR_WALL_STROKE_PX))
    )


def _css_px(value: float) -> str:
    return f"{value:g}px"


def _render_site_layer(site_elements: list[dict[str, Any]]) -> str:
    parts = ['<g id="site-layer">']
    for element in _site_draw_order(site_elements):
        parts.append(_render_geometry(element, f"ref-site {element.get('category', 'site')}", "data-ref-site"))
    parts.append("</g>")
    return "\n".join(parts)


def _render_floor_layer(spaces: list[dict[str, Any]]) -> str:
    parts = ['<g id="reference-floor-layer">']
    for space in spaces:
        parts.append(_render_geometry(space, f"ref-floor {_floor_material_class(space)}", "data-ref-room"))
    parts.append("</g>")
    return "\n".join(parts)


def _floor_material_class(space: dict[str, Any]) -> str:
    room_id = str(space.get("id", ""))
    if room_id in VINYL_PLANK_ROOM_IDS:
        return "vinyl-plank"
    if room_id in TILE_ROOM_IDS:
        return "tile"
    return "carpet"


def _render_built_in_layer(built_ins: list[dict[str, Any]]) -> str:
    parts = ['<g id="reference-built-in-layer">']
    for item in built_ins:
        item_type = str(item.get("type", "built_in")).replace("built_in_", "")
        parts.append(_render_geometry(item, f"ref-built-in {item_type}", "data-ref-built-in"))
        if item_type == "wardrobe":
            parts.append(_built_in_wardrobe_lines(item))
    parts.append("</g>")
    return "\n".join(part for part in parts if part)


def _built_in_wardrobe_lines(item: dict[str, Any]) -> str:
    item_id = escape(str(item.get("id", "unknown")))
    geometry = item.get("display_px", {})
    if geometry.get("type") != "rect":
        return ""
    x = float(geometry["x"])
    y = float(geometry["y"])
    width = float(geometry["width"])
    height = float(geometry["height"])
    divider_height = 4.0
    upper_y1 = y + 4.0
    upper_y2 = y + height / 2 - divider_height / 2 - 2.5
    lower_y1 = y + height / 2 + divider_height / 2 + 2.5
    lower_y2 = y + height - 4.0
    front_x = x + 2.0
    parts = []
    parts.extend(_sliding_door_symbol(f"{item_id}:upper", front_x, upper_y1, front_x, upper_y2))
    parts.append(
        f'<rect class="ref-built-in-wardrobe-divider" data-ref-built-in-divider="{item_id}" '
        f'x="{x:.1f}" y="{y + height / 2 - divider_height / 2:.1f}" '
        f'width="{width:.1f}" height="{divider_height:.1f}"/>'
    )
    parts.extend(_sliding_door_symbol(f"{item_id}:lower", front_x, lower_y1, front_x, lower_y2))
    return "\n".join(parts)


def _render_passage_layer(features: list[dict[str, Any]]) -> str:
    parts = ['<g id="reference-passage-layer">']
    for feature in features:
        if str(feature.get("type", "")) == "opening":
            parts.append(_render_passage_cutout(escape(str(feature.get("id", "unknown"))), feature))
    parts.append("</g>")
    return "\n".join(part for part in parts if part)


def _render_wall_layer() -> str:
    parts = ['<g id="reference-wall-layer" data-source="curated-matplotlib-wall-network">']
    exterior_path = _wall_path_by_class("exterior")
    thin_exterior_path = _wall_path_by_class("thin-exterior")
    trimmed_exterior_path = _wall_path_by_class("trimmed-exterior")
    toilet_exterior_path = _wall_path_by_class("toilet-exterior")
    interior_path = _wall_path_by_class("interior")
    thin_interior_path = _wall_path_by_class("thin-interior")
    parts.append(
        '<path class="wall-core exterior structural" data-ref-wall-class="exterior" '
        f'd="{escape(exterior_path)}"/>'
    )
    if thin_exterior_path:
        parts.append(
            '<path class="wall-core thin-exterior structural" data-ref-wall-class="thin-exterior" '
            f'd="{escape(thin_exterior_path)}"/>'
        )
    if trimmed_exterior_path:
        parts.append(
            '<path class="wall-core trimmed-exterior structural" data-ref-wall-class="trimmed-exterior" '
            f'd="{escape(trimmed_exterior_path)}"/>'
        )
    if toilet_exterior_path:
        parts.append(
            '<path class="wall-core toilet-exterior structural" data-ref-wall-class="toilet-exterior" '
            f'd="{escape(toilet_exterior_path)}"/>'
        )
    parts.append(
        '<path class="wall-core interior structural" data-ref-wall-class="interior" '
        f'd="{escape(interior_path)}"/>'
    )
    if thin_interior_path:
        parts.append(
            '<path class="wall-core thin-interior structural" data-ref-wall-class="thin-interior" '
            f'd="{escape(thin_interior_path)}"/>'
        )
    for junction_id, x, y, width, height in WALL_JUNCTION_CAPS:
        parts.append(
            f'<rect class="wall-junction-cap structural" data-ref-wall-junction="{escape(junction_id)}" '
            f'x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}"/>'
        )
    parts.append('<g id="wall-reference-layer" aria-hidden="true">')
    for wall_id, wall_class, path_data in CURATED_WALL_PATHS:
        thickness = WALL_THICKNESS_OVERRIDES_M.get(wall_id)
        projection = WALL_PROJECTION_OVERRIDES_M.get(wall_id)
        metadata_attrs = "".join(
            attr
            for attr in (
                f' data-wall-thickness-m="{thickness}"' if thickness else "",
                f' data-wall-projection-m="{projection}"' if projection else "",
            )
        )
        parts.append(
            f'<path class="wall-reference structural {wall_class}" data-ref-wall="{escape(wall_id)}" '
            f'data-ref-wall-class="{wall_class}"{metadata_attrs} d="{path_data}"/>'
        )
    parts.append("</g>")
    parts.append("</g>")
    return "\n".join(parts)


def _wall_path_by_class(wall_class: str) -> str:
    if wall_class in VISIBLE_WALL_PATHS:
        return " ".join(VISIBLE_WALL_PATHS[wall_class])
    return " ".join(path_data for _, candidate_class, path_data in CURATED_WALL_PATHS if candidate_class == wall_class)


def _render_opening_layer(features: list[dict[str, Any]]) -> str:
    parts = ['<g id="reference-opening-layer">']
    sliding_door_parts: list[str] = []
    for feature in features:
        feature_type = str(feature.get("type", ""))
        if feature_type not in OPENING_TYPES:
            continue
        feature_id = escape(str(feature.get("id", "unknown")))
        if feature_type == "opening":
            continue
        for x1, y1, x2, y2 in _opening_centerlines_for_feature(feature_id, feature):
            rendered = _render_reference_opening(feature_id, feature_type, x1, y1, x2, y2)
            if feature_id in SLIDING_DOOR_SYMBOL_IDS:
                sliding_door_parts.append(rendered)
            else:
                parts.append(rendered)
    parts.extend(sliding_door_parts)
    parts.append("</g>")
    return "\n".join(parts)


def _render_reference_opening(feature_id: str, feature_type: str, x1: float, y1: float, x2: float, y2: float) -> str:
    opening_context = _opening_context(feature_id)
    parts = [
        f'<g data-ref-opening="{feature_id}">',
    ]
    if "window" in feature_type:
        parts.extend(_window_symbol(feature_id, opening_context, x1, y1, x2, y2))
    elif feature_type == "sliding_door" and feature_id in POCKET_DOOR_IDS:
        parts.extend(_pocket_door_symbol(feature_id, x1, y1, x2, y2))
    elif feature_type in {"slider", "sliding_door"} and feature_id in SLIDING_DOOR_SYMBOL_IDS:
        parts.extend(_sliding_door_symbol(feature_id, x1, y1, x2, y2))
    elif feature_type in {"slider", "sliding_door"}:
        parts.extend(_window_symbol(feature_id, opening_context, x1, y1, x2, y2))
    elif feature_type == "door_group":
        if feature_id not in DOOR_GROUP_IDS_WITHOUT_CUTOUT:
            parts.append(_opening_cutout(feature_id, opening_context, x1, y1, x2, y2))
        if feature_id in DOUBLE_DOOR_GROUP_IDS:
            parts.extend(_double_door_symbol(feature_id, x1, y1, x2, y2))
        else:
            parts.append(_door_leaf(feature_id, x1, y1, x2, y2))
            parts.append(_door_arc(feature_id, x1, y1, x2, y2))
    elif feature_type == "door":
        if feature_id not in PHOTO_REFERENCE_DOOR_IDS:
            parts.append(_opening_cutout(feature_id, opening_context, x1, y1, x2, y2))
            parts.extend(_opening_jambs(x1, y1, x2, y2))
        parts.append(_door_leaf(feature_id, x1, y1, x2, y2))
        parts.append(_door_arc(feature_id, x1, y1, x2, y2))
    parts.append("</g>")
    return "\n".join(parts)


def _opening_context(feature_id: str) -> str:
    return "internal" if feature_id in INTERNAL_OPENING_IDS else "exterior"


def _window_symbol(feature_id: str, window_context: str, x1: float, y1: float, x2: float, y2: float) -> list[str]:
    attrs = f' data-ref-window="{feature_id}" data-window-context="{window_context}"'
    parts = [_line(f"ref-window-cutout {window_context}", x1, y1, x2, y2, attrs)]
    if window_context == "exterior" and feature_id != "laundry_north_window":
        parts.extend(_window_guides(feature_id, x1, y1, x2, y2))
    return parts


def _window_guides(feature_id: str, x1: float, y1: float, x2: float, y2: float) -> list[str]:
    return [
        _line("ref-window-guide", *offset, f' data-ref-window-guide="{feature_id}" data-window-context="exterior"')
        for offset in (
            _offset_line(x1, y1, x2, y2, -WINDOW_GUIDE_OFFSET_PX),
            _offset_line(x1, y1, x2, y2, WINDOW_GUIDE_OFFSET_PX),
        )
    ]


def _sliding_door_symbol(feature_id: str, x1: float, y1: float, x2: float, y2: float) -> list[str]:
    if abs(x2 - x1) >= abs(y2 - y1):
        left = min(x1, x2)
        right = max(x1, x2)
        span = right - left
        sliding_width = span * 0.67
        sliding_x = left
        fixed_join_x = left + sliding_width - 1.0
        fixed_width = (right - fixed_join_x) * 1.5
        fixed_x = right - fixed_width
        return [
            f'<g class="ref-sliding-door" data-ref-sliding-door="{feature_id}">',
            f'<rect class="ref-sliding-door-panel fixed" data-ref-sliding-door-panel="{feature_id}:fixed" '
            f'x="{fixed_x:.1f}" y="{y1:.1f}" width="{fixed_width:.1f}" height="1.8"/>',
            f'<rect class="ref-sliding-door-panel sliding" data-ref-sliding-door-panel="{feature_id}:sliding" '
            f'x="{sliding_x:.1f}" y="{y1 - 2.2:.1f}" width="{sliding_width:.1f}" height="1.8"/>',
            "</g>",
        ]

    top = min(y1, y2)
    bottom = max(y1, y2)
    span = bottom - top
    sliding_height = span * 0.67
    sliding_y = top
    fixed_join_y = top + sliding_height - 1.0
    fixed_height = (bottom - fixed_join_y) * 1.5
    fixed_y = bottom - fixed_height
    fixed_x = (x1 - 2.2) + 1.8
    return [
        f'<g class="ref-sliding-door" data-ref-sliding-door="{feature_id}">',
        f'<rect class="ref-sliding-door-panel fixed" data-ref-sliding-door-panel="{feature_id}:fixed" '
        f'x="{fixed_x:.1f}" y="{fixed_y:.1f}" width="1.8" height="{fixed_height:.1f}"/>',
        f'<rect class="ref-sliding-door-panel sliding" data-ref-sliding-door-panel="{feature_id}:sliding" '
        f'x="{x1 - 2.2:.1f}" y="{sliding_y:.1f}" width="1.8" height="{sliding_height:.1f}"/>',
        "</g>",
    ]


def _pocket_door_symbol(feature_id: str, x1: float, y1: float, x2: float, y2: float) -> list[str]:
    pocket = POCKET_DOOR_POCKET_CENTERLINES[feature_id]
    exposed_tail = 16.0
    pocket_overlap = 6.0
    if abs(y2 - y1) > abs(x2 - x1):
        _, pocket_y1, _, pocket_y2 = pocket
        casing_y = min(pocket_y1, pocket_y2)
        casing_height = abs(pocket_y2 - pocket_y1)
        panel_x = x1 - 1.0
        panel_y = casing_y - exposed_tail
        panel_height = exposed_tail + pocket_overlap
        panel = (
            f'<rect class="ref-pocket-door-panel" data-ref-pocket-door-panel="{feature_id}" '
            f'x="{panel_x:.1f}" y="{panel_y:.1f}" width="2.0" height="{panel_height:.1f}"/>'
        )
        casing = (
            f'<rect class="ref-pocket-door-casing" data-ref-pocket-door-casing="{feature_id}" '
            f'x="{x1 - 2.7:.1f}" y="{casing_y:.1f}" width="5.4" height="{casing_height:.1f}"/>'
        )
        slot = (
            f'<rect class="ref-pocket-door-slot" data-ref-pocket-door-slot="{feature_id}" '
            f'x="{x1 - 1.0:.1f}" y="{casing_y + 3.0:.1f}" width="2.0" height="{max(casing_height - 6.0, 0):.1f}"/>'
        )
    else:
        pocket_x1, _, pocket_x2, _ = pocket
        casing_x = min(pocket_x1, pocket_x2)
        casing_width = abs(pocket_x2 - pocket_x1)
        panel_x = casing_x - exposed_tail
        panel_y = y1 - 1.0
        panel_width = exposed_tail + pocket_overlap
        panel = (
            f'<rect class="ref-pocket-door-panel" data-ref-pocket-door-panel="{feature_id}" '
            f'x="{panel_x:.1f}" y="{panel_y:.1f}" width="{panel_width:.1f}" height="2.0"/>'
        )
        casing = (
            f'<rect class="ref-pocket-door-casing" data-ref-pocket-door-casing="{feature_id}" '
            f'x="{casing_x:.1f}" y="{y1 - 2.7:.1f}" width="{casing_width:.1f}" height="5.4"/>'
        )
        slot = (
            f'<rect class="ref-pocket-door-slot" data-ref-pocket-door-slot="{feature_id}" '
            f'x="{casing_x + 3.0:.1f}" y="{y1 - 1.0:.1f}" width="{max(casing_width - 6.0, 0):.1f}" height="2.0"/>'
        )
    return [
        f'<g class="ref-pocket-door" data-ref-pocket-door="{feature_id}">',
        panel,
        casing,
        slot,
        "</g>",
    ]


def _opening_cutout(feature_id: str, opening_context: str, x1: float, y1: float, x2: float, y2: float) -> str:
    css_context = "interior" if opening_context == "internal" else "exterior"
    if feature_id == "deck_door_group":
        return "\n".join(
            [
                _line(
                    f"opening-cutout {css_context} timber threshold",
                    829.5,
                    y1,
                    829.5,
                    y2,
                    f' data-ref-opening-cutout="{feature_id}" data-opening-context="{css_context}" data-opening-part="interior-floor"',
                ),
                _line(
                    f"opening-cutout {css_context} deck threshold",
                    836.0,
                    y1,
                    836.0,
                    y2,
                    f' data-ref-opening-cutout="{feature_id}" data-opening-context="{css_context}" data-opening-part="deck-floor"',
                ),
            ]
        )
    material_class = " timber" if feature_id in TIMBER_OPENING_CUTOUT_IDS else ""
    return _line(
        f"opening-cutout {css_context}{material_class}",
        x1,
        y1,
        x2,
        y2,
        f' data-ref-opening-cutout="{feature_id}" data-opening-context="{css_context}"',
    )


def _render_passage_cutout(feature_id: str, feature: dict[str, Any]) -> str:
    geometry = feature.get("display_px", {})
    fill_class = "vinyl-plank" if feature_id in VINYL_PLANK_PASSAGE_IDS else "carpet"
    if geometry.get("type") == "rect":
        x = float(geometry["x"])
        y = float(geometry["y"])
        width = float(geometry["width"])
        height = float(geometry["height"])
        return (
            f'<rect class="opening-passage-fill {fill_class}" data-ref-passage="{feature_id}" '
            f'x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}"/>'
        )
    if geometry.get("type") == "polygon":
        points = _point_text(geometry.get("points", []))
        return f'<polygon class="opening-passage-fill {fill_class}" data-ref-passage="{feature_id}" points="{points}"/>'
    if geometry.get("type") == "multi_polygon":
        return "\n".join(
            f'<polygon class="opening-passage-fill {fill_class}" data-ref-passage="{feature_id}" points="{_point_text(polygon)}"/>'
            for polygon in geometry.get("polygons", [])
        )
    return ""


def _opening_centerlines_for_feature(feature_id: str, feature: dict[str, Any]) -> list[tuple[float, float, float, float]]:
    if feature_id in OPENING_CENTERLINE_OVERRIDES:
        return OPENING_CENTERLINE_OVERRIDES[feature_id]
    return _opening_centerlines(feature)


def _line(css_class: str, x1: float, y1: float, x2: float, y2: float, attrs: str) -> str:
    return f'<line class="{css_class}"{attrs} x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'


def _offset_line(x1: float, y1: float, x2: float, y2: float, offset: float) -> tuple[float, float, float, float]:
    length = hypot(x2 - x1, y2 - y1)
    if length == 0:
        return x1, y1, x2, y2
    normal_x = -(y2 - y1) / length
    normal_y = (x2 - x1) / length
    return (
        x1 + normal_x * offset,
        y1 + normal_y * offset,
        x2 + normal_x * offset,
        y2 + normal_y * offset,
    )


def _opening_jambs(x1: float, y1: float, x2: float, y2: float) -> list[str]:
    if abs(y2 - y1) >= abs(x2 - x1):
        return [
            _line("ref-opening-jamb", x1 - 4.5, y1, x1 + 4.5, y1, ""),
            _line("ref-opening-jamb", x2 - 4.5, y2, x2 + 4.5, y2, ""),
        ]
    return [
        _line("ref-opening-jamb", x1, y1 - 4.5, x1, y1 + 4.5, ""),
        _line("ref-opening-jamb", x2, y2 - 4.5, x2, y2 + 4.5, ""),
    ]


def _double_door_symbol(feature_id: str, x1: float, y1: float, x2: float, y2: float) -> list[str]:
    if abs(x2 - x1) > 0.01 and abs(y2 - y1) > 0.01:
        return _angled_double_door_symbol(feature_id, x1, y1, x2, y2)
    if abs(y2 - y1) >= abs(x2 - x1):
        radius = abs(y2 - y1) / 2
        center_y = min(y1, y2) + radius
        side = _door_swing_side(feature_id)
        leaf_x = x1 + (side * radius)
        return [
            f'<path class="ref-door-leaf double-door" data-ref-door-leaf="{feature_id}:upper" '
            f'd="M {x1:.1f} {y1:.1f} L {leaf_x:.1f} {y1:.1f}"/>',
            f'<path class="ref-door-leaf double-door" data-ref-door-leaf="{feature_id}:lower" '
            f'd="M {x2:.1f} {y2:.1f} L {leaf_x:.1f} {y2:.1f}"/>',
            f'<path class="ref-door-arc double-door" data-ref-door-arc="{feature_id}:upper" '
            f'd="M {leaf_x:.1f} {y1:.1f} A {radius:.1f} {radius:.1f} 0 0 1 {x1:.1f} {center_y:.1f}"/>',
            f'<path class="ref-door-arc double-door" data-ref-door-arc="{feature_id}:lower" '
            f'd="M {leaf_x:.1f} {y2:.1f} A {radius:.1f} {radius:.1f} 0 0 0 {x2:.1f} {center_y:.1f}"/>',
        ]

    radius = abs(x2 - x1) / 2
    center_x = min(x1, x2) + radius
    leaf_y = y1 - radius
    return [
        f'<path class="ref-door-leaf double-door" data-ref-door-leaf="{feature_id}:left" '
        f'd="M {x1:.1f} {y1:.1f} L {x1:.1f} {leaf_y:.1f}"/>',
        f'<path class="ref-door-leaf double-door" data-ref-door-leaf="{feature_id}:right" '
        f'd="M {x2:.1f} {y2:.1f} L {x2:.1f} {leaf_y:.1f}"/>',
        f'<path class="ref-door-arc double-door" data-ref-door-arc="{feature_id}:left" '
        f'd="M {x1:.1f} {leaf_y:.1f} A {radius:.1f} {radius:.1f} 0 0 1 {center_x:.1f} {y1:.1f}"/>',
        f'<path class="ref-door-arc double-door" data-ref-door-arc="{feature_id}:right" '
        f'd="M {x2:.1f} {leaf_y:.1f} A {radius:.1f} {radius:.1f} 0 0 0 {center_x:.1f} {y2:.1f}"/>',
    ]


def _angled_double_door_symbol(feature_id: str, x1: float, y1: float, x2: float, y2: float) -> list[str]:
    length = hypot(x2 - x1, y2 - y1)
    if length == 0:
        return []
    radius = length / 2
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    tangent_x = (x2 - x1) / length
    tangent_y = (y2 - y1) / length
    normal_x = -tangent_y
    normal_y = tangent_x
    leaf_upper_x = x1 + normal_x * radius
    leaf_upper_y = y1 + normal_y * radius
    leaf_lower_x = x2 + normal_x * radius
    leaf_lower_y = y2 + normal_y * radius
    upper_sweep = 1 if normal_x * tangent_y - normal_y * tangent_x > 0 else 0
    lower_sweep = 1 - upper_sweep
    return [
        f'<path class="ref-door-leaf double-door" data-ref-door-leaf="{feature_id}:upper" '
        f'd="M {x1:.1f} {y1:.1f} L {leaf_upper_x:.1f} {leaf_upper_y:.1f}"/>',
        f'<path class="ref-door-leaf double-door" data-ref-door-leaf="{feature_id}:lower" '
        f'd="M {x2:.1f} {y2:.1f} L {leaf_lower_x:.1f} {leaf_lower_y:.1f}"/>',
        f'<path class="ref-door-arc double-door" data-ref-door-arc="{feature_id}:upper" '
        f'd="M {leaf_upper_x:.1f} {leaf_upper_y:.1f} A {radius:.1f} {radius:.1f} 0 0 {upper_sweep} {center_x:.1f} {center_y:.1f}"/>',
        f'<path class="ref-door-arc double-door" data-ref-door-arc="{feature_id}:lower" '
        f'd="M {leaf_lower_x:.1f} {leaf_lower_y:.1f} A {radius:.1f} {radius:.1f} 0 0 {lower_sweep} {center_x:.1f} {center_y:.1f}"/>',
    ]


def _door_leaf(feature_id: str, x1: float, y1: float, x2: float, y2: float) -> str:
    if feature_id in PHOTO_REFERENCE_VERTICAL_LEFT_UPPER_HINGE_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-leaf photo-reference" data-ref-door-leaf="{feature_id}" '
            f'd="M {x1:.1f} {y1:.1f} L {x1 - radius:.1f} {y1:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_VERTICAL_LEFT_LOWER_HINGE_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-leaf photo-reference" data-ref-door-leaf="{feature_id}" '
            f'd="M {x2:.1f} {y2:.1f} L {x2 - radius:.1f} {y2:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_VERTICAL_LEFT_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-leaf photo-reference" data-ref-door-leaf="{feature_id}" '
            f'd="M {x2:.1f} {y2:.1f} L {x2 - radius:.1f} {y2:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_VERTICAL_RIGHT_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-leaf photo-reference" data-ref-door-leaf="{feature_id}" '
            f'd="M {x2:.1f} {y2:.1f} L {x2 + radius:.1f} {y2:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_HORIZONTAL_DOWN_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-leaf photo-reference" data-ref-door-leaf="{feature_id}" '
            f'd="M {x1:.1f} {y1:.1f} L {x1:.1f} {y1 + radius:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_HORIZONTAL_UP_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-leaf photo-reference" data-ref-door-leaf="{feature_id}" '
            f'd="M {x1:.1f} {y1:.1f} L {x1:.1f} {y1 - radius:.1f}"/>'
        )
    if abs(y2 - y1) >= abs(x2 - x1):
        leaf = min(29, abs(y2 - y1))
        side = _door_swing_side(feature_id)
        return f'<path class="ref-door-leaf" data-ref-door-leaf="{feature_id}" d="M {x1:.1f} {y1:.1f} L {x1 + (side * 21):.1f} {y1 + leaf:.1f}"/>'
    leaf = min(29, abs(x2 - x1))
    return f'<path class="ref-door-leaf" data-ref-door-leaf="{feature_id}" d="M {x1:.1f} {y1:.1f} L {x1 + leaf:.1f} {y1 - 21:.1f}"/>'


def _door_arc(feature_id: str, x1: float, y1: float, x2: float, y2: float) -> str:
    if feature_id in PHOTO_REFERENCE_VERTICAL_LEFT_UPPER_HINGE_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-arc photo-reference" data-ref-door-arc="{feature_id}" '
            f'd="M {x2:.1f} {y2:.1f} A {radius:.1f} {radius:.1f} 0 0 1 '
            f'{x1 - radius:.1f} {y1:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_VERTICAL_LEFT_LOWER_HINGE_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-arc photo-reference" data-ref-door-arc="{feature_id}" '
            f'd="M {x1:.1f} {y1:.1f} A {radius:.1f} {radius:.1f} 0 0 0 '
            f'{x2 - radius:.1f} {y2:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_VERTICAL_LEFT_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-arc photo-reference" data-ref-door-arc="{feature_id}" '
            f'd="M {x1:.1f} {y1:.1f} A {radius:.1f} {radius:.1f} 0 0 0 '
            f'{x2 - radius:.1f} {y2:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_VERTICAL_RIGHT_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-arc photo-reference" data-ref-door-arc="{feature_id}" '
            f'd="M {x1:.1f} {y1:.1f} A {radius:.1f} {radius:.1f} 0 0 1 '
            f'{x2 + radius:.1f} {y2:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_HORIZONTAL_DOWN_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        sweep = 1 if x2 > x1 else 0
        return (
            f'<path class="ref-door-arc photo-reference" data-ref-door-arc="{feature_id}" '
            f'd="M {x2:.1f} {y2:.1f} A {radius:.1f} {radius:.1f} 0 0 {sweep} '
            f'{x1:.1f} {y1 + radius:.1f}"/>'
        )
    if feature_id in PHOTO_REFERENCE_HORIZONTAL_UP_DOOR_IDS:
        radius = _photo_reference_door_radius(x1, y1, x2, y2)
        return (
            f'<path class="ref-door-arc photo-reference" data-ref-door-arc="{feature_id}" '
            f'd="M {x2:.1f} {y2:.1f} A {radius:.1f} {radius:.1f} 0 0 0 '
            f'{x1:.1f} {y1 - radius:.1f}"/>'
        )
    if abs(y2 - y1) >= abs(x2 - x1):
        end_y = y1 + min(33, abs(y2 - y1))
        side = _door_swing_side(feature_id)
        return f'<path class="ref-door-arc" data-ref-door-arc="{feature_id}" d="M {x1:.1f} {y1:.1f} Q {x1 + (side * 28):.1f} {y1:.1f} {x1 + (side * 28):.1f} {end_y:.1f}"/>'
    end_x = x1 + min(33, abs(x2 - x1))
    return f'<path class="ref-door-arc" data-ref-door-arc="{feature_id}" d="M {x1:.1f} {y1:.1f} Q {x1:.1f} {y1 - 28:.1f} {end_x:.1f} {y1 - 28:.1f}"/>'


def _photo_reference_door_radius(x1: float, y1: float, x2: float, y2: float) -> float:
    measured_radius = max(abs(x2 - x1), abs(y2 - y1))
    return measured_radius or INTERNAL_DOOR_WIDTH_PX


def _door_swing_side(feature_id: str) -> int:
    return 1


def _render_label_layer(spaces: list[dict[str, Any]], site_elements: list[dict[str, Any]]) -> str:
    parts = ['<g id="reference-label-layer">']
    for element in _site_draw_order(site_elements):
        element_id = str(element.get("id", ""))
        if element_id not in {"upper_side_driveway", "front_diagonal_path", "garage_shed", "cottage"}:
            continue
        label = SITE_LABELS.get(element_id, _humanize(element_id))
        parts.append(_label(element, label, "ref-site-label"))
    for space in spaces:
        space_id = str(space.get("id", ""))
        label = ROOM_LABELS.get(space_id, _humanize(space_id))
        if space_id == "master_bedroom":
            label = "Master\nBedroom"
        parts.append(_label(space, label, "ref-room-label"))
    parts.append("</g>")
    return "\n".join(part for part in parts if part)


def _render_scale_layer() -> str:
    total_px = sum(px for px, _ in INTERNAL_SCALE_SPANS_PX_M)
    total_m = sum(metres for _, metres in INTERNAL_SCALE_SPANS_PX_M)
    px_per_m = total_px / total_m
    scale_m = 2.0
    scale_px = px_per_m * scale_m
    x1 = 1038.5
    x2 = x1 + scale_px
    x_mid = x1 + px_per_m
    y = 628.0
    return "\n".join(
        [
            f'<g id="reference-scale-layer" data-scale-source="internal-measured-spans" data-scale-metres="{scale_m:g}" data-scale-px="{scale_px:.1f}" data-scale-px-per-m="{px_per_m:.1f}">',
            f'<line class="ref-scale-line" x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}"/>',
            f'<line class="ref-scale-tick" x1="{x1:.1f}" y1="{y - 4:.1f}" x2="{x1:.1f}" y2="{y + 4:.1f}"/>',
            f'<line class="ref-scale-tick" x1="{x_mid:.1f}" y1="{y - 4:.1f}" x2="{x_mid:.1f}" y2="{y + 4:.1f}"/>',
            f'<line class="ref-scale-tick" x1="{x2:.1f}" y1="{y - 4:.1f}" x2="{x2:.1f}" y2="{y + 4:.1f}"/>',
            f'<text class="ref-scale-label" x="{x_mid:.1f}" y="{y - 14:.1f}">Internal room scale</text>',
            f'<text class="ref-scale-label" x="{x1:.1f}" y="{y + 12:.1f}">0</text>',
            f'<text class="ref-scale-label" x="{x_mid:.1f}" y="{y + 12:.1f}">1 m</text>',
            f'<text class="ref-scale-label" x="{x2:.1f}" y="{y + 12:.1f}">2 m</text>',
            "</g>",
        ]
    )


def _render_dimension_layer() -> str:
    parts = ['<g id="reference-dimension-layer" style="display:none" aria-hidden="true">']
    for annotation in DIMENSION_ANNOTATIONS:
        parts.append(_render_dimension_annotation(annotation))
    parts.append("</g>")
    return "\n".join(parts)


def _render_dimension_annotation(annotation: dict[str, Any]) -> str:
    dimension_id = escape(str(annotation["id"]))
    kind = escape(str(annotation["kind"]))
    confidence = escape(str(annotation["confidence"]))
    label = escape(str(annotation["label"]))
    source = escape(str(annotation["source"]))
    x1 = float(annotation["x1"])
    y1 = float(annotation["y1"])
    x2 = float(annotation["x2"])
    y2 = float(annotation["y2"])
    offset_x = float(annotation["offset_x"])
    offset_y = float(annotation["offset_y"])
    line_x1 = x1 + offset_x
    line_y1 = y1 + offset_y
    line_x2 = x2 + offset_x
    line_y2 = y2 + offset_y
    label_x = (line_x1 + line_x2) / 2
    label_y = (line_y1 + line_y2) / 2
    label_width = max(26.0, len(label) * 3.8 + 8.0)
    label_height = 11.0
    tick = 4.5
    if abs(line_x2 - line_x1) >= abs(line_y2 - line_y1):
        tick_one = (line_x1, line_y1 - tick, line_x1, line_y1 + tick)
        tick_two = (line_x2, line_y2 - tick, line_x2, line_y2 + tick)
    else:
        tick_one = (line_x1 - tick, line_y1, line_x1 + tick, line_y1)
        tick_two = (line_x2 - tick, line_y2, line_x2 + tick, line_y2)

    return "\n".join(
        [
            f'<g class="ref-dimension-group {confidence}" data-ref-dimension="{dimension_id}" '
            f'data-ref-dimension-kind="{kind}" data-ref-dimension-confidence="{confidence}" '
            f'data-ref-dimension-source="{source}">',
            f'<line class="ref-dimension-extension" x1="{x1:.1f}" y1="{y1:.1f}" x2="{line_x1:.1f}" y2="{line_y1:.1f}"/>',
            f'<line class="ref-dimension-extension" x1="{x2:.1f}" y1="{y2:.1f}" x2="{line_x2:.1f}" y2="{line_y2:.1f}"/>',
            f'<line class="ref-dimension-line" x1="{line_x1:.1f}" y1="{line_y1:.1f}" x2="{line_x2:.1f}" y2="{line_y2:.1f}"/>',
            f'<line class="ref-dimension-tick" x1="{tick_one[0]:.1f}" y1="{tick_one[1]:.1f}" x2="{tick_one[2]:.1f}" y2="{tick_one[3]:.1f}"/>',
            f'<line class="ref-dimension-tick" x1="{tick_two[0]:.1f}" y1="{tick_two[1]:.1f}" x2="{tick_two[2]:.1f}" y2="{tick_two[3]:.1f}"/>',
            f'<rect class="ref-dimension-label-bg {confidence}" x="{label_x - label_width / 2:.1f}" y="{label_y - label_height / 2:.1f}" width="{label_width:.1f}" height="{label_height:.1f}" rx="2.0" ry="2.0"/>',
            f'<text class="ref-dimension-label {confidence}" x="{label_x:.1f}" y="{label_y:.1f}">{label}</text>',
            "</g>",
        ]
    )


def _render_orientation_layer(orientation: dict[str, Any]) -> str:
    compass = orientation.get("compass", {})
    angle = float(compass.get("north_arrow_degrees_clockwise_from_plan_up", 0.0))
    plan_right_bearing = float(compass.get("plan_right_bearing_degrees", 90.0))
    confidence = str(compass.get("confidence", "unknown"))
    cx = 1065.0
    cy = 578.0
    axis_radius = 16.0
    label_radius = 25.0

    south = _compass_point(cx, cy, angle + 180.0, axis_radius)
    north = _compass_point(cx, cy, angle, axis_radius)
    west_inner = _compass_point(cx, cy, angle + 270.0, 9.0)
    east_inner = _compass_point(cx, cy, angle + 90.0, 9.0)
    north_label = _compass_point(cx, cy, angle, label_radius)
    east_label = _compass_point(cx, cy, angle + 90.0, label_radius)
    south_label = _compass_point(cx, cy, angle + 180.0, label_radius)
    west_label = _compass_point(cx, cy, angle + 270.0, label_radius)
    angle_rad = radians(angle)
    direction_x = sin(angle_rad)
    direction_y = -cos(angle_rad)
    perpendicular_x = cos(angle_rad)
    perpendicular_y = sin(angle_rad)
    arrow_base_x = north[0] - direction_x * 5.0
    arrow_base_y = north[1] - direction_y * 5.0
    arrow_left = (arrow_base_x + perpendicular_x * 2.3, arrow_base_y + perpendicular_y * 2.3)
    arrow_right = (arrow_base_x - perpendicular_x * 2.3, arrow_base_y - perpendicular_y * 2.3)

    title = "North arrow estimated from parcel-line angle in the cadastral map screenshot; plan right is approximately NE."
    return "\n".join(
        [
            f'<g id="reference-orientation-layer" data-north-angle-deg="{angle:.1f}" data-plan-right-bearing-deg="{plan_right_bearing:.1f}" data-orientation-confidence="{escape(confidence)}">',
            f"<title>{escape(title)}</title>",
            _line("ref-compass-secondary", west_inner[0], west_inner[1], east_inner[0], east_inner[1], ""),
            _line("ref-compass-axis", south[0], south[1], north[0], north[1], ""),
            '<polygon class="ref-compass-arrow" points="'
            f'{north[0]:.1f},{north[1]:.1f} {arrow_left[0]:.1f},{arrow_left[1]:.1f} {arrow_right[0]:.1f},{arrow_right[1]:.1f}"/>',
            f'<text class="ref-compass-label primary" x="{north_label[0]:.1f}" y="{north_label[1]:.1f}">N</text>',
            f'<text class="ref-compass-label" x="{east_label[0]:.1f}" y="{east_label[1]:.1f}">E</text>',
            f'<text class="ref-compass-label" x="{south_label[0]:.1f}" y="{south_label[1]:.1f}">S</text>',
            f'<text class="ref-compass-label" x="{west_label[0]:.1f}" y="{west_label[1]:.1f}">W</text>',
            "</g>",
        ]
    )


def _compass_point(cx: float, cy: float, degrees_clockwise_from_plan_up: float, radius: float) -> tuple[float, float]:
    angle = radians(degrees_clockwise_from_plan_up)
    return cx + sin(angle) * radius, cy - cos(angle) * radius


def _label(item: dict[str, Any], label: str, css_class: str) -> str:
    item_id = str(item.get("id", ""))
    bounds = _item_bounds(item)
    if not bounds:
        return ""
    if item_id in LABEL_OVERRIDES:
        x, y = LABEL_OVERRIDES[item_id]
    else:
        min_x, min_y, max_x, max_y = bounds
        x = (min_x + max_x) / 2
        y = (min_y + max_y) / 2
    lines = label.split("\n")
    if len(lines) == 1:
        return f'<text class="{css_class}" x="{x:.1f}" y="{y:.1f}">{escape(label)}</text>'
    tspans = [
        f'<tspan x="{x:.1f}" dy="{-4 if index == 0 else 9}">{escape(line)}</tspan>'
        for index, line in enumerate(lines)
    ]
    return f'<text class="{css_class}" x="{x:.1f}" y="{y:.1f}">{"".join(tspans)}</text>'


def _render_geometry(item: dict[str, Any], css_class: str, data_attr: str) -> str:
    item_id = str(item.get("id", "unknown"))
    geometry = item.get("display_px", {})
    title = escape(item_id)
    if geometry.get("type") == "rect":
        x = float(geometry["x"])
        y = float(geometry["y"])
        width = float(geometry["width"])
        height = float(geometry["height"])
        return f'<rect class="{escape(css_class)}" {data_attr}="{escape(item_id)}" x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}"><title>{title}</title></rect>'
    if geometry.get("type") == "polygon":
        return _polygon(geometry.get("points", []), css_class, data_attr, item_id, title)
    if geometry.get("type") == "multi_polygon":
        return "\n".join(
            _polygon(polygon, css_class, data_attr, item_id, title)
            for polygon in geometry.get("polygons", [])
        )
    return ""


def _polygon(points: list[list[float]], css_class: str, data_attr: str, item_id: str, title: str) -> str:
    return f'<polygon class="{escape(css_class)}" {data_attr}="{escape(item_id)}" points="{_point_text(points)}"><title>{title}</title></polygon>'


def _wall_path_from_geometry(geometry: dict[str, Any]) -> str:
    if geometry.get("type") == "rect":
        x = float(geometry["x"])
        y = float(geometry["y"])
        width = float(geometry["width"])
        height = float(geometry["height"])
        return f"M{x:.1f} {y:.1f} H{x + width:.1f} V{y + height:.1f} H{x:.1f} Z"
    if geometry.get("type") == "polygon":
        return _path_from_points(geometry.get("points", []))
    return ""


def _path_from_points(points: list[list[float]]) -> str:
    if not points:
        return ""
    first_x, first_y = points[0]
    commands = [f"M{float(first_x):.1f} {float(first_y):.1f}"]
    commands.extend(f"L{float(x):.1f} {float(y):.1f}" for x, y in points[1:])
    commands.append("Z")
    return " ".join(commands)


def _point_text(points: list[list[float]]) -> str:
    return " ".join(f"{float(x):.1f},{float(y):.1f}" for x, y in points)


def _site_draw_order(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {
        "boundary": 0,
        "planting": 1,
        "hardscape": 2,
        "deck": 3,
        "building": 4,
    }
    return sorted(items, key=lambda item: order.get(str(item.get("category")), 5))


def _opening_centerlines(feature: dict[str, Any]) -> list[tuple[float, float, float, float]]:
    geometry = feature.get("display_px", {})
    if geometry.get("type") == "multi_polygon":
        return [_centerline(points) for points in geometry.get("polygons", []) if points]
    if geometry.get("type") == "polygon":
        points = geometry.get("points", [])
        return [_centerline(points)] if points else []
    return []


def _centerline(points: list[list[float]]) -> tuple[float, float, float, float]:
    if len(points) == 4:
        long_axis = _thin_quad_centerline(points)
        if long_axis:
            return long_axis
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    height = max_y - min_y
    if height >= width:
        x = (min_x + max_x) / 2
        return x, min_y, x, max_y
    y = (min_y + max_y) / 2
    return min_x, y, max_x, y


def _thin_quad_centerline(points: list[list[float]]) -> tuple[float, float, float, float] | None:
    edges: list[tuple[float, tuple[float, float], tuple[float, float]]] = []
    for index, start in enumerate(points):
        end = points[(index + 1) % len(points)]
        x1, y1 = float(start[0]), float(start[1])
        x2, y2 = float(end[0]), float(end[1])
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
        edges.append((length, midpoint, (float(index), 0.0)))

    shortest = sorted(edges, key=lambda edge: edge[0])[:2]
    longest = sorted(edges, key=lambda edge: edge[0])[-1][0]
    if not shortest or longest < 1 or longest / max(shortest[-1][0], 0.1) < 1.4:
        return None
    (x1, y1), (x2, y2) = shortest[0][1], shortest[1][1]
    return x1, y1, x2, y2


def _item_bounds(item: dict[str, Any]) -> tuple[float, float, float, float] | None:
    geometry = item.get("display_px", {})
    if geometry.get("type") == "rect":
        x = float(geometry["x"])
        y = float(geometry["y"])
        return x, y, x + float(geometry["width"]), y + float(geometry["height"])
    if geometry.get("type") == "polygon":
        return _points_bounds(geometry.get("points", []))
    if geometry.get("type") == "multi_polygon":
        bounds = [_points_bounds(polygon) for polygon in geometry.get("polygons", [])]
        bounds = [item for item in bounds if item]
        if not bounds:
            return None
        return (
            min(item[0] for item in bounds),
            min(item[1] for item in bounds),
            max(item[2] for item in bounds),
            max(item[3] for item in bounds),
        )
    return None


def _points_bounds(points: list[list[float]]) -> tuple[float, float, float, float] | None:
    if not points:
        return None
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def _humanize(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split("_"))
