from __future__ import annotations

from html import escape
from math import hypot
from typing import Any

from .model import HouseModel
from .presentation_plan import CANVAS_HEIGHT, CANVAS_WIDTH, ROOM_LABELS, SITE_LABELS


OPENING_TYPES = {"window", "window_group", "slider", "door_group", "door", "sliding_door", "opening"}

LABEL_OVERRIDES = {
    "lounge": (690.0, 392.0),
    "kitchen_dining": (782.0, 372.0),
    "master_bedroom": (563.0, 512.0),
    "office": (648.0, 554.0),
    "bedroom_2": (824.0, 592.0),
    "laundry": (916.0, 558.0),
}

CURATED_WALL_PATHS = [
    ("sunroom_glazing_frame", "interior", "M536 486 H646 V360 H597 V408 L552 452 H536 Z"),
    ("lounge_exterior", "exterior", "M638 358 H742"),
    ("lounge_sunroom_wall", "interior", "M638 358 V485"),
    ("master_sunroom_old_external_wall", "exterior", "M518 485 H608"),
    ("hallway_north_wall", "exterior", "M608 485 H638"),
    ("lounge_hallway_wall", "interior", "M638 489 H683 M705 489 H742"),
    ("kitchen_east_wall", "exterior", "M742 365 V314 H822 V496"),
    ("entrance_deck_wall", "exterior", "M822 496 H836 M877 496 H940"),
    ("kitchen_entrance_return_wall", "interior", "M822 496 H784"),
    ("private_rooms_south_wall", "exterior", "M518 610 H940"),
    ("bedroom2_east_wall", "interior", "M890 500 V610"),
    ("master_west_wall", "exterior", "M518 485 V610"),
    ("dining_west_external_wall", "exterior", "M742 314 V365"),
    ("lounge_kitchen_divider", "interior", "M742 395 V493"),
    ("hallway_south_wall", "interior", "M608 523 H657 M679 523 H688 M722 523 H758"),
    ("hallway_kitchen_door_wall", "interior", "M742 515 V523"),
    ("bedroom2_north_wall", "interior", "M758 523 H762 M784 523 H890"),
    ("master_office_wall", "interior", "M608 485 V494 M608 516 V610"),
    ("office_bathroom_wall", "interior", "M688 523 V610"),
    ("bathroom_bedroom2_wall", "interior", "M758 523 V610"),
    ("entrance_laundry_wall", "interior", "M890 500 V504 M890 524.1 V580"),
    ("laundry_toilet_wall", "interior", "M890 580 H896 M912 580 H940"),
    ("kitchen_entrance_door_wall", "interior", "M784 500 V501 M784 522 V523"),
    ("laundry_toilet_exterior", "exterior", "M940 496 V610"),
]

VISIBLE_WALL_PATHS = {
    "exterior": [
        "M638 358 H742",
        "M742 365 V314 H822 V496",
        "M822 496 H836 M877 496 H940 V610 H518 V485 H638",
    ],
}

INTERNAL_OPENING_IDS = {
    "sunroom_wraparound_glazing",
    "sunroom_lounge_slider",
    "master_sunroom_window",
    "hallway_to_lounge_door",
    "hallway_to_kitchen_dining_door",
    "hallway_to_bathroom_sliding_door",
    "hallway_to_master_bedroom_door",
    "hallway_to_office_door",
    "kitchen_dining_to_bedroom2_door",
    "entrance_to_kitchen_dining_door",
    "laundry_to_toilet_door",
}

INTERNAL_DOOR_WIDTH_PX = 22.0
POCKET_DOOR_IDS = {"hallway_to_bathroom_sliding_door"}
POCKET_DOOR_POCKET_CENTERLINES = {
    "hallway_to_bathroom_sliding_door": (722.0, 523.0, 758.0, 523.0),
}

PHOTO_REFERENCE_DOOR_IDS = {
    "hallway_to_lounge_door",
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

OPENING_CENTERLINE_OVERRIDES = {
    "deck_door_group": [(822.0, 338.0, 822.0, 396.0)],
    "deck_side_dining_window": [(822.0, 410.0, 822.0, 484.0)],
    "entrance_deck_slider": [(877.0, 496.0, 836.0, 496.0)],
    "toilet_frosted_window": [(940.0, 586.0, 940.0, 606.0)],
    "master_street_window": [(518.0, 528.0, 518.0, 588.0)],
    "master_sunroom_window": [(604.0, 485.0, 552.0, 485.0)],
    "hallway_to_lounge_door": [(683.0, 489.0, 705.0, 489.0)],
    "hallway_to_kitchen_dining_door": [(742.0, 493.0, 742.0, 515.0)],
    "hallway_to_bathroom_sliding_door": [(688.0, 523.0, 722.0, 523.0)],
    "hallway_to_master_bedroom_door": [(608.0, 494.0, 608.0, 516.0)],
    "hallway_to_office_door": [(679.0, 523.0, 657.0, 523.0)],
    "kitchen_dining_to_bedroom2_door": [(762.0, 523.0, 784.0, 523.0)],
    "entrance_to_kitchen_dining_door": [(784.0, 500.0, 784.0, 522.0)],
    "laundry_to_toilet_door": [(896.0, 580.0, 912.0, 580.0)],
    "office_se_window": [(675.0, 610.0, 625.0, 610.0)],
    "bathroom_se_window": [(746.0, 610.0, 704.0, 610.0)],
    "bedroom2_se_window": [(862.0, 610.0, 790.0, 610.0)],
}

WINDOW_GUIDE_OFFSET_PX = 2.0

def render_reference_plan_svg(model: HouseModel) -> str:
    current_structure = model.raw.get("current_structure", {})
    current_site = model.raw.get("current_site", {})
    spaces = current_structure.get("spaces", [])
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
        _render_passage_layer(features),
        _render_reference_furniture_layer(),
        _render_wall_layer(),
        _render_opening_layer(features),
        _render_scale_layer(),
        _render_label_layer(spaces, site_elements),
        "</svg>",
    ]
    return "\n".join(parts)


def _reference_defs() -> str:
    return """
<filter id="object-soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
  <feDropShadow dx="2" dy="2.5" stdDeviation="1.4" flood-color="#4b443a" flood-opacity="0.2"/>
</filter>
<pattern id="floorboards-subtle" width="24" height="24" patternUnits="userSpaceOnUse">
  <rect width="24" height="24" fill="#f4eee8"/>
  <path d="M0 8 H24 M0 18 H24" stroke="#dfcdb6" stroke-width="0.45" opacity="0.28"/>
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
    return """
text { font-family: Arial, sans-serif; fill: #1d2522; }
.ref-site { stroke-linejoin: round; }
.ref-site.boundary { fill: url(#lawn-soft); stroke: #6b7867; stroke-width: 4; }
.ref-site.planting { fill: url(#lawn-soft); stroke: #4f8d43; stroke-width: 1.8; opacity: 0.85; }
.ref-site.hardscape { fill: url(#pavers-soft); stroke: #b6ac9d; stroke-width: 1.5; }
.ref-site.deck { fill: url(#deck-boards-subtle); stroke: #714927; stroke-width: 2; }
.ref-site.building { fill: #d9dece; stroke: #697466; stroke-width: 2.2; }
.ref-floor { stroke: none; fill: url(#floorboards-subtle); }
.ref-floor.wet { fill: url(#tile-soft); }
.ref-floor.circulation { fill: #eee7d9; }
.wall-core, .wall-reference { fill: none; stroke-linecap: butt; stroke-linejoin: miter; }
.wall-core.exterior { stroke: #585b63; stroke-width: 12px; }
.wall-core.interior { stroke: #585b63; stroke-width: 5px; }
.wall-reference { display: none; }
.opening-cutout { fill: none; stroke: #fffdf8; stroke-linecap: butt; }
.opening-cutout.exterior { stroke-width: 13px; }
.opening-cutout.interior { stroke-width: 7px; }
.opening-passage-fill { fill: #eee7d9; stroke: none; }
.opening-passage-fill.timber { fill: url(#floorboards-subtle); }
.opening-passage-fill.circulation { fill: #eee7d9; }
.ref-window-cutout { fill: none; stroke: #fffdf8; stroke-linecap: butt; }
.ref-window-cutout.exterior { stroke-width: 8px; }
.ref-window-cutout.internal { stroke-width: 4px; }
.ref-window-guide { fill: none; stroke: #777b80; stroke-width: 0.9; stroke-linecap: butt; }
.ref-opening-jamb { stroke: #585b63; stroke-width: 1.8; stroke-linecap: butt; }
.ref-pocket-door-panel { fill: #fffdf8; stroke: #2f3134; stroke-width: 0.45; }
.ref-pocket-door-casing { fill: #2f3134; stroke: none; }
.ref-pocket-door-slot { fill: #fffdf8; stroke: none; }
.ref-door-leaf { fill: none; stroke: #575b60; stroke-width: 1.4; stroke-linecap: round; }
.ref-door-arc { fill: none; stroke: #575b60; stroke-width: 1.1; }
.ref-door-leaf.photo-reference { stroke: #2f3134; stroke-width: 1.8; stroke-linecap: butt; }
.ref-door-arc.photo-reference { stroke: #6f7478; stroke-width: 0.95; }
.furniture { fill: rgba(255, 255, 255, 0.92); stroke: #c3b7a5; stroke-width: 1.3; filter: url(#object-soft-shadow); }
.furniture.accent { fill: #75b45b; stroke: #5f984c; }
.furniture.appliance { fill: #f5f7f5; stroke: #b3bec0; }
.furniture.cabinet { fill: #e9edf0; stroke: #b9c1c4; }
.furniture.dark { fill: #e7e9e6; stroke: #bdc4be; }
.furniture.outdoor { fill: #e7e2d7; stroke: #b8aa96; }
.furniture.screen { fill: #35383a; stroke: #222426; }
.furniture.storage { fill: #d3a86d; stroke: #9f7b4a; }
.furniture.car { fill: #9a8d80; stroke: #4f4944; }
.furniture-detail { fill: none; stroke: rgba(85, 78, 70, 0.58); stroke-width: 1.3; }
.ref-room-label, .ref-site-label { text-anchor: middle; dominant-baseline: middle; font-weight: 500; }
.ref-room-label { font-size: 9px; }
.ref-site-label { font-size: 8px; fill: #243029; }
.ref-scale-line, .ref-scale-tick { stroke: #2f3134; stroke-width: 1.1; stroke-linecap: butt; }
.ref-scale-label { font-size: 7px; text-anchor: middle; dominant-baseline: auto; fill: #2f3134; }
""".strip()


def _render_site_layer(site_elements: list[dict[str, Any]]) -> str:
    parts = ['<g id="site-layer">']
    for element in _site_draw_order(site_elements):
        parts.append(_render_geometry(element, f"ref-site {element.get('category', 'site')}", "data-ref-site"))
    parts.append("</g>")
    return "\n".join(parts)


def _render_floor_layer(spaces: list[dict[str, Any]]) -> str:
    parts = ['<g id="reference-floor-layer">']
    for space in spaces:
        parts.append(_render_geometry(space, f"ref-floor {space.get('category', 'room')}", "data-ref-room"))
    parts.append("</g>")
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
    interior_path = _wall_path_by_class("interior")
    parts.append(
        '<path class="wall-core exterior structural" data-ref-wall-class="exterior" '
        f'd="{escape(exterior_path)}"/>'
    )
    parts.append(
        '<path class="wall-core interior structural" data-ref-wall-class="interior" '
        f'd="{escape(interior_path)}"/>'
    )
    parts.append('<g id="wall-reference-layer" aria-hidden="true">')
    for wall_id, wall_class, path_data in CURATED_WALL_PATHS:
        parts.append(
            f'<path class="wall-reference structural {wall_class}" data-ref-wall="{escape(wall_id)}" '
            f'data-ref-wall-class="{wall_class}" d="{path_data}"/>'
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
    for feature in features:
        feature_type = str(feature.get("type", ""))
        if feature_type not in OPENING_TYPES:
            continue
        feature_id = escape(str(feature.get("id", "unknown")))
        if feature_type == "opening":
            continue
        for x1, y1, x2, y2 in _opening_centerlines_for_feature(feature_id, feature):
            parts.append(_render_reference_opening(feature_id, feature_type, x1, y1, x2, y2))
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
    elif feature_type in {"slider", "sliding_door"}:
        parts.extend(_window_symbol(feature_id, opening_context, x1, y1, x2, y2))
    elif feature_type == "door_group":
        parts.append(_opening_cutout(feature_id, opening_context, x1, y1, x2, y2))
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
    if window_context == "exterior":
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
    return _line(
        f"opening-cutout {css_context}",
        x1,
        y1,
        x2,
        y2,
        f' data-ref-opening-cutout="{feature_id}" data-opening-context="{css_context}"',
    )


def _render_passage_cutout(feature_id: str, feature: dict[str, Any]) -> str:
    geometry = feature.get("display_px", {})
    fill_class = "timber" if feature_id == "hallway_to_entrance_laundry" else "circulation"
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


def _render_reference_furniture_layer() -> str:
    return """
<g id="furniture-layer" opacity="0.82">
  <g data-furniture="dining_table" data-evidence="Inside-Dining-Room-looking-N.jpg">
    <title>Dining table and chairs kept as a light visual cue.</title>
    <rect class="furniture" x="772" y="390" width="36" height="54" rx="5"/>
    <circle class="furniture" cx="762" cy="404" r="5"/>
    <circle class="furniture" cx="818" cy="404" r="5"/>
    <circle class="furniture" cx="762" cy="430" r="5"/>
    <circle class="furniture" cx="818" cy="430" r="5"/>
  </g>
  <g data-furniture="kitchen_island" data-evidence="Inside-Kitchen-Looking-NW.jpg; Inside-Kitchen-Looking-SE.jpg">
    <title>Compact kitchen island/bench cue, avoiding the oversized schematic cabinetry blocks.</title>
    <rect class="furniture cabinet" x="776" y="342" width="34" height="18" rx="4"/>
    <circle class="furniture-detail" cx="786" cy="351" r="4"/>
    <line class="furniture-detail" x1="796" y1="351" x2="805" y2="351"/>
  </g>
  <g data-furniture="lounge_seating" data-placement="l_shape_with_rear_flow_gap" data-evidence="Inside-Lounge-Looking-NE.jpg; Inside-Lounge-Looking-SW.jpg; Inside-Lounge-Looking-SE.jpg">
    <title>L-shaped sofa pulled off the lower wall to leave the circulation gap visible.</title>
    <rect class="furniture dark" x="656" y="438" width="64" height="24" rx="6"/>
    <rect class="furniture dark" x="656" y="412" width="24" height="50" rx="6"/>
    <line class="furniture-detail" x1="652" y1="470" x2="724" y2="470"/>
    <rect class="furniture" x="686" y="404" width="28" height="20" rx="4"/>
    <rect class="furniture screen" x="718" y="376" width="10" height="58" rx="2"/>
  </g>
  <g data-furniture="master_bed" data-evidence="Inside-Master-Bedroom-Looking-S.jpg">
    <title>Master bed and headboard.</title>
    <rect class="furniture" x="529" y="528" width="56" height="68" rx="5"/>
    <rect class="furniture storage" x="529" y="528" width="56" height="12" rx="3"/>
    <line class="furniture-detail" x1="557" y1="540" x2="557" y2="596"/>
  </g>
  <g data-furniture="bedroom2_bed_and_storage" data-evidence="Inside-Bedroom-2-Looking-N.jpg; Inside-Bedroom-2-Looking-SW.jpg; Inside-Bedroom-2-Looking-W.jpg">
    <title>Bedroom 2 bed and storage cues.</title>
    <rect class="furniture" x="772" y="532" width="62" height="42" rx="5"/>
    <rect class="furniture accent" x="772" y="532" width="62" height="11" rx="3"/>
    <rect class="furniture storage" x="850" y="532" width="28" height="14" rx="2"/>
    <rect class="furniture storage" x="868" y="548" width="12" height="48" rx="2"/>
    <line class="furniture-detail" x1="802" y1="543" x2="802" y2="574"/>
  </g>
  <g data-furniture="office_desk" data-evidence="Inside-Office-Looking-SE.jpg">
    <title>Office desk, chair, and screens.</title>
    <rect class="furniture" x="628" y="580" width="48" height="18" rx="3"/>
    <rect class="furniture screen" x="636" y="568" width="16" height="10" rx="2"/>
    <rect class="furniture screen" x="656" y="568" width="16" height="10" rx="2"/>
    <circle class="furniture dark" cx="652" cy="558" r="7"/>
  </g>
  <g data-furniture="laundry_appliances" data-evidence="Inside-Laundry-Looking-NE.jpg">
    <title>Laundry bench and appliances.</title>
    <rect class="furniture" x="897" y="508" width="36" height="10" rx="2"/>
    <rect class="furniture appliance" x="898" y="524" width="16" height="24" rx="2"/>
    <rect class="furniture appliance" x="916" y="524" width="16" height="24" rx="2"/>
    <circle class="furniture-detail" cx="906" cy="537" r="5"/>
    <circle class="furniture-detail" cx="924" cy="537" r="5"/>
  </g>
  <g data-furniture="garage_car_pair" data-evidence="user_confirmed_two_cars">
    <title>Two cars shown in the garage.</title>
    <rect class="furniture car" x="1030" y="260" width="72" height="36" rx="15"/>
    <rect class="furniture-detail" x="1050" y="266" width="30" height="24" rx="5"/>
    <circle class="furniture dark" cx="1046" cy="297" r="4"/>
    <circle class="furniture dark" cx="1086" cy="297" r="4"/>
    <rect class="furniture car" x="1108" y="260" width="72" height="36" rx="15"/>
    <rect class="furniture-detail" x="1128" y="266" width="30" height="24" rx="5"/>
    <circle class="furniture dark" cx="1124" cy="297" r="4"/>
    <circle class="furniture dark" cx="1164" cy="297" r="4"/>
  </g>
  <g data-furniture="deck_seating" data-evidence="From-Back-Door-looking-onto-deck.jpg">
    <title>Light outdoor table and seating cues on the rear deck.</title>
    <circle class="furniture outdoor" cx="868" cy="438" r="12"/>
    <rect class="furniture outdoor" x="844" y="452" width="14" height="19" rx="4"/>
    <rect class="furniture outdoor" x="882" y="452" width="14" height="19" rx="4"/>
    <rect class="furniture outdoor" x="894" y="456" width="34" height="20" rx="5"/>
    <line class="furniture-detail" x1="901" y1="466" x2="921" y2="466"/>
  </g>
</g>
""".strip()


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
    return -1 if feature_id == "deck_door_group" else 1


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
    px_per_m = INTERNAL_DOOR_WIDTH_PX / 0.81
    scale_m = 2.0
    scale_px = px_per_m * scale_m
    x1 = 958.0
    x2 = x1 + scale_px
    y = 628.0
    centre_x = (x1 + x2) / 2
    return "\n".join(
        [
            f'<g id="reference-scale-layer" data-scale-source="internal-door-0.81m" data-scale-metres="{scale_m:g}" data-scale-px="{scale_px:.1f}">',
            f'<line class="ref-scale-line" x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}"/>',
            f'<line class="ref-scale-tick" x1="{x1:.1f}" y1="{y - 4:.1f}" x2="{x1:.1f}" y2="{y + 4:.1f}"/>',
            f'<line class="ref-scale-tick" x1="{x2:.1f}" y1="{y - 4:.1f}" x2="{x2:.1f}" y2="{y + 4:.1f}"/>',
            f'<text class="ref-scale-label" x="{centre_x:.1f}" y="{y - 7:.1f}">2 m</text>',
            "</g>",
        ]
    )


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
