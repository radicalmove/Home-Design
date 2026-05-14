from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from .model import HouseModel


CANVAS_WIDTH = 1600
CANVAS_HEIGHT = 900


ROOM_LABELS = {
    "kitchen_dining": "Kitchen / Dining",
    "lounge": "Lounge",
    "sunroom": "Sunroom",
    "hallway": "Hallway",
    "master_bedroom": "Master Bedroom",
    "office": "Office",
    "bathroom": "Bathroom",
    "bedroom_2": "Bedroom 2",
    "entrance": "Entrance",
    "laundry": "Laundry",
    "toilet": "Toilet",
}


SITE_LABELS = {
    "property_boundary": "Property Boundary",
    "upper_side_driveway": "Upper Side Driveway",
    "front_diagonal_path": "Front Path",
    "rear_timber_deck": "Rear Timber Deck",
    "cottage_end_deck": "Cottage End Deck",
    "garage_concrete_pad": "Garage Concrete",
    "garage_cottage_side_path": "Garage / Cottage Path",
    "garage_shed": "Garage / Shed",
    "cottage": "Cottage",
    "boundary_hedges_and_fences": "Hedges / Fences",
}


def render_presentation_plan_svg(model: HouseModel) -> str:
    current_structure = model.raw.get("current_structure", {})
    current_site = model.raw.get("current_site", {})
    spaces = current_structure.get("spaces", [])
    features = current_structure.get("features", [])
    site_elements = current_site.get("elements", [])

    parts = [
        f'<svg id="presentation-plan" xmlns="http://www.w3.org/2000/svg" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}">',
        "<defs>",
        _material_patterns(),
        "</defs>",
        "<style>",
        "text { font-family: Arial, sans-serif; fill: #1f2824; }",
        ".title { font-size: 28px; font-weight: 700; }",
        ".subtitle { font-size: 13px; fill: #5d675f; }",
        ".room-label { font-size: 13px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; }",
        ".site-label { font-size: 14px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; fill: #263126; }",
        ".space { stroke: #d2c8b8; stroke-width: 2.5; fill: url(#timber-light); }",
        ".space.wet { fill: url(#tile); }",
        ".space.circulation { fill: #efe6d5; }",
        ".space.bedroom { fill: url(#timber-light); }",
        ".site.boundary { stroke: #607068; stroke-width: 4; fill: url(#grass); }",
        ".site.hardscape { stroke: #a49b8b; stroke-width: 2; fill: url(#stone); }",
        ".site.deck { stroke: #7a5734; stroke-width: 2; fill: url(#timber); }",
        ".site.building { stroke: #65705c; stroke-width: 3; fill: #d9dfca; }",
        ".site.planting { stroke: #32663b; stroke-width: 2; fill: url(#grass); }",
        ".wall-segment { fill: none; stroke: #656d72; stroke-linecap: square; stroke-linejoin: round; }",
        ".exterior-wall { stroke-width: 9; }",
        ".interior-wall { stroke-width: 5; stroke: #8a8f93; }",
        ".opening { stroke-width: 5; fill: none; stroke-linecap: round; }",
        ".opening.window { stroke: #75c9df; }",
        ".opening.slider, .opening.door_group { stroke: #7b5bc2; }",
        ".opening.door, .opening.opening, .opening.sliding_door { stroke: #b97233; }",
        ".furniture { fill: #ffffff; stroke: #c3b7a5; stroke-width: 2; }",
        ".furniture.accent { fill: #7ab85d; stroke: #5d9747; }",
        ".furniture.appliance { fill: #f7f8f6; stroke: #aeb8bb; }",
        ".furniture.cabinet { fill: #315f8c; stroke: #234766; }",
        ".furniture.dark { fill: #33312e; stroke: #24221f; }",
        ".furniture.outdoor { fill: #596f49; stroke: #394b31; }",
        ".furniture.screen { fill: #24282c; stroke: #151719; }",
        ".furniture.storage { fill: #d6a05f; stroke: #9d7140; }",
        ".furniture.car { fill: #9a8c7d; stroke: #373331; }",
        ".furniture-detail { fill: none; stroke: #6e645b; stroke-width: 2; }",
        ".confidence-note { font-size: 12px; fill: #5d675f; }",
        "</style>",
        '<rect width="100%" height="100%" fill="#f4f1ea"/>',
        '<text class="title" x="42" y="50">Presentation 2D Plan</text>',
        '<text class="subtitle" x="42" y="72">Current measured/photo-context model rendered for visual feedback. Approximate elements remain labelled in metadata.</text>',
    ]

    parts.append('<g id="site-layer">')
    for element in _site_draw_order(site_elements):
        parts.append(_render_item(element, f"site {element.get('category', 'site')}", "data-plan-site"))
    parts.append("</g>")

    parts.append('<g id="rooms-layer">')
    for space in spaces:
        parts.append(_render_item(space, f"space {space.get('category', 'room')}", "data-plan-room"))
    parts.append("</g>")

    parts.append(_render_wall_layer(spaces))
    parts.append(_render_furniture_layer())

    parts.append('<g id="openings-layer">')
    for feature in features:
        feature_type = str(feature.get("type", "feature"))
        if feature_type in {"window", "window_group", "slider", "door_group", "door", "opening", "sliding_door"}:
            parts.append(_render_item(feature, f"opening {feature_type}", "data-plan-feature"))
    parts.append("</g>")

    parts.append('<g id="labels-layer">')
    for element in _site_draw_order(site_elements):
        label = SITE_LABELS.get(str(element.get("id")), _humanize(str(element.get("id", "site"))))
        if element.get("id") != "property_boundary":
            parts.append(_render_label(element, label, "site-label"))
    for space in spaces:
        label = ROOM_LABELS.get(str(space.get("id")), _humanize(str(space.get("id", "room"))))
        parts.append(_render_label(space, label, "room-label"))
    parts.append("</g>")

    approx_count = sum(
        1
        for item in [*spaces, *features, *site_elements]
        if "approx" in str(item.get("confidence", item.get("status", "")))
        or "reference_position" in str(item.get("confidence", ""))
    )
    parts.append(
        f'<text class="confidence-note" x="42" y="842">Approximate/reference-positioned items: {approx_count}. Use this plan for visual feedback, not construction documentation.</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def write_presentation_plan(path: str | Path, svg: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)


def _material_patterns() -> str:
    return """
<g id="materials"></g>
<pattern id="timber" width="18" height="18" patternUnits="userSpaceOnUse">
  <rect width="18" height="18" fill="#9b6235"/>
  <path d="M0 3 H18 M0 9 H18 M0 15 H18" stroke="#7e4d2a" stroke-width="1"/>
</pattern>
<pattern id="timber-light" width="22" height="22" patternUnits="userSpaceOnUse">
  <rect width="22" height="22" fill="#efd2a5"/>
  <path d="M0 5 H22 M0 12 H22 M0 19 H22" stroke="#e2bd85" stroke-width="1"/>
</pattern>
<pattern id="grass" width="20" height="20" patternUnits="userSpaceOnUse">
  <rect width="20" height="20" fill="#79b75b"/>
  <path d="M3 18 L8 2 M12 20 L16 4 M0 10 L20 6" stroke="#5c9b43" stroke-width="1.2"/>
</pattern>
<pattern id="stone" width="34" height="24" patternUnits="userSpaceOnUse">
  <rect width="34" height="24" fill="#d7d0c2"/>
  <path d="M0 8 H34 M0 17 H34 M10 0 V8 M23 8 V17 M14 17 V24" stroke="#b7ad9b" stroke-width="1"/>
</pattern>
<pattern id="tile" width="28" height="28" patternUnits="userSpaceOnUse">
  <rect width="28" height="28" fill="#eceff1"/>
  <path d="M0 0 L28 28 M28 0 L0 28" stroke="#d0d6d9" stroke-width="1"/>
</pattern>
""".strip()


def _site_draw_order(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {
        "boundary": 0,
        "planting": 1,
        "hardscape": 2,
        "deck": 3,
        "building": 4,
    }
    return sorted(items, key=lambda item: order.get(str(item.get("category")), 5))


def _render_item(item: dict[str, Any], css_class: str, data_attr: str) -> str:
    item_id = str(item.get("id", "unknown"))
    geometry = item.get("display_px", {})
    title = "; ".join(
        part
        for part in [
            item_id,
            str(item.get("confidence", item.get("status", "unknown"))),
            str(item.get("notes", "")),
        ]
        if part
    )
    if geometry.get("type") == "multi_polygon":
        return "\n".join(
            _polygon(polygon, css_class, data_attr, item_id, title)
            for polygon in geometry.get("polygons", [])
        )
    if geometry.get("type") == "polygon":
        return _polygon(geometry.get("points", []), css_class, data_attr, item_id, title)
    if geometry.get("type") == "rect":
        x = float(geometry["x"])
        y = float(geometry["y"])
        width = float(geometry["width"])
        height = float(geometry["height"])
        return (
            f'<rect class="{escape(css_class)}" {data_attr}="{escape(item_id)}" '
            f'x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}">'
            f"<title>{escape(title)}</title></rect>"
        )
    return f"<!-- presentation item {escape(item_id)} has no renderable geometry -->"


def _polygon(points: list[list[float]], css_class: str, data_attr: str, item_id: str, title: str) -> str:
    point_text = " ".join(f"{float(x):.1f},{float(y):.1f}" for x, y in points)
    return (
        f'<polygon class="{escape(css_class)}" {data_attr}="{escape(item_id)}" '
        f'points="{point_text}"><title>{escape(title)}</title></polygon>'
    )


def _render_label(item: dict[str, Any], label: str, css_class: str) -> str:
    bounds = _item_bounds(item)
    if not bounds:
        return ""
    min_x, min_y, max_x, max_y = bounds
    x = (min_x + max_x) / 2
    y = (min_y + max_y) / 2
    return f'<text class="{escape(css_class)}" x="{x:.1f}" y="{y:.1f}">{escape(label)}</text>'


def _render_wall_layer(spaces: list[dict[str, Any]]) -> str:
    parts = ['<g id="wall-layer">']
    for space in spaces:
        geometry = space.get("display_px", {})
        if geometry.get("type") == "rect":
            x = float(geometry["x"])
            y = float(geometry["y"])
            width = float(geometry["width"])
            height = float(geometry["height"])
            parts.append(
                f'<rect class="wall-segment exterior-wall" x="{x:.1f}" y="{y:.1f}" '
                f'width="{width:.1f}" height="{height:.1f}"><title>{escape(str(space.get("id")))} wall outline</title></rect>'
            )
        elif geometry.get("type") == "polygon":
            points = " ".join(f"{float(px):.1f},{float(py):.1f}" for px, py in geometry.get("points", []))
            parts.append(
                f'<polygon class="wall-segment exterior-wall" points="{points}">'
                f'<title>{escape(str(space.get("id")))} wall outline</title></polygon>'
            )
    parts.append("</g>")
    return "\n".join(parts)


def _render_furniture_layer() -> str:
    return """
<g id="furniture-layer">
  <g data-furniture="dining_table" data-evidence="Inside-Dining-Room-looking-N.jpg">
    <title>Dining table and four chairs visible in dining photos.</title>
    <rect class="furniture" x="761" y="384" width="42" height="68" rx="5"/>
    <circle class="furniture" cx="750" cy="399" r="7"/>
    <circle class="furniture" cx="814" cy="399" r="7"/>
    <circle class="furniture" cx="750" cy="438" r="7"/>
    <circle class="furniture" cx="814" cy="438" r="7"/>
  </g>
  <g data-furniture="kitchen_cabinetry" data-evidence="Inside-Kitchen-Looking-NW.jpg; Inside-Kitchen-Looking-SE.jpg">
    <title>Kitchen benches, blue cabinetry, pantry/fridge wall, and sink/cooktop run are visible in kitchen photos.</title>
    <rect class="furniture cabinet" x="746" y="330" width="12" height="150" rx="2"/>
    <rect class="furniture cabinet" x="805" y="326" width="13" height="154" rx="2"/>
    <rect class="furniture appliance" x="787" y="342" width="18" height="28" rx="3"/>
    <circle class="furniture-detail" cx="751" cy="362" r="5"/>
  </g>
  <g data-furniture="lounge_seating" data-placement="l_shape_with_rear_flow_gap" data-evidence="Inside-Lounge-Looking-NE.jpg; Inside-Lounge-Looking-SW.jpg; Inside-Lounge-Looking-SE.jpg">
    <title>L-shaped lounge sofa pulled off the lower wall to leave a circulation gap behind it, plus coffee table and TV/media wall visible in lounge photos.</title>
    <rect class="furniture dark" x="656" y="438" width="64" height="24" rx="6"/>
    <rect class="furniture dark" x="656" y="412" width="24" height="50" rx="6"/>
    <line class="furniture-detail" x1="652" y1="470" x2="724" y2="470"/>
    <rect class="furniture" x="686" y="404" width="28" height="20" rx="4"/>
    <rect class="furniture screen" x="718" y="376" width="10" height="58" rx="2"/>
  </g>
  <g data-furniture="master_bed" data-evidence="Inside-Master-Bedroom-Looking-S.jpg">
    <title>Master bed and headboard visible against the dark feature wall.</title>
    <rect class="furniture" x="541" y="528" width="56" height="68" rx="5"/>
    <rect class="furniture storage" x="541" y="528" width="56" height="12" rx="3"/>
    <line class="furniture-detail" x1="569" y1="540" x2="569" y2="596"/>
  </g>
  <g data-furniture="bedroom2_bed_and_storage" data-evidence="Inside-Bedroom-2-Looking-N.jpg; Inside-Bedroom-2-Looking-SW.jpg; Inside-Bedroom-2-Looking-W.jpg">
    <title>Bedroom 2 photos show bed/daybed along the pink feature wall with storage/bookcase and open wardrobe on the opposite side.</title>
    <rect class="furniture" x="772" y="532" width="62" height="42" rx="5"/>
    <rect class="furniture accent" x="772" y="532" width="62" height="11" rx="3"/>
    <rect class="furniture storage" x="850" y="532" width="28" height="14" rx="2"/>
    <rect class="furniture storage" x="868" y="548" width="12" height="48" rx="2"/>
    <line class="furniture-detail" x1="802" y1="543" x2="802" y2="574"/>
  </g>
  <g data-furniture="office_desk" data-evidence="Inside-Office-Looking-SE.jpg">
    <title>Office desk, chair, screens, and shelving visible in office photos.</title>
    <rect class="furniture" x="628" y="580" width="48" height="18" rx="3"/>
    <rect class="furniture screen" x="636" y="568" width="16" height="10" rx="2"/>
    <rect class="furniture screen" x="656" y="568" width="16" height="10" rx="2"/>
    <circle class="furniture dark" cx="652" cy="558" r="7"/>
  </g>
  <g data-furniture="laundry_appliances" data-evidence="Inside-Laundry-Looking-NE.jpg">
    <title>Laundry bench, sink, and two front-loading appliances visible in laundry photos.</title>
    <rect class="furniture" x="897" y="508" width="36" height="10" rx="2"/>
    <rect class="furniture appliance" x="898" y="524" width="16" height="24" rx="2"/>
    <rect class="furniture appliance" x="916" y="524" width="16" height="24" rx="2"/>
    <circle class="furniture-detail" cx="906" cy="537" r="5"/>
    <circle class="furniture-detail" cx="924" cy="537" r="5"/>
  </g>
  <g data-furniture="garage_car_pair" data-evidence="user_confirmed_two_cars">
    <title>Two cars shown because the user confirmed the garage can be represented with two cars.</title>
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
    <title>Small outdoor table/chairs and wicker seating visible on the deck photos.</title>
    <circle class="furniture outdoor" cx="868" cy="438" r="14"/>
    <rect class="furniture outdoor" x="844" y="452" width="14" height="22" rx="4"/>
    <rect class="furniture outdoor" x="882" y="452" width="14" height="22" rx="4"/>
    <rect class="furniture outdoor" x="894" y="456" width="34" height="22" rx="5"/>
    <line class="furniture-detail" x1="901" y1="467" x2="921" y2="467"/>
  </g>
</g>
""".strip()


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
