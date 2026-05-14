from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from .model import HouseModel, Room


CATEGORY_FILL = {
    "living": "#d9e9d0",
    "bedroom": "#dfe8f5",
    "wet": "#d7edf0",
    "circulation": "#efe9d8",
}

LIGHT_FILL = {
    "high": "#ffe28a",
    "medium": "#f6e6b8",
    "low": "#d8e0e7",
    "unknown": "#e5e2da",
}


def render_baseline_svg(
    model: HouseModel,
    *,
    season: str | None = None,
    time_band: str | None = None,
) -> str:
    scale = 55
    margin = 60
    min_x, min_y, max_x, max_y = _bounds(model.rooms)
    width = int((max_x - min_x) * scale + margin * 2 + 110)
    footer_h = 155
    height = int((max_y - min_y) * scale + margin * 2 + footer_h)

    def sx(x: float) -> float:
        return margin + (x - min_x) * scale

    def sy(y: float) -> float:
        return margin + (y - min_y) * scale

    daylight_active = season is not None and time_band is not None
    title = "Current Baseline Floor Plan"
    if daylight_active:
        title = f"Daylight: {season} {time_band}"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text { font-family: Arial, sans-serif; fill: #203026; }",
        ".title { font-size: 20px; font-weight: 700; }",
        ".label { font-size: 12px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; }",
        ".dim { font-size: 11px; fill: #425045; }",
        ".note { font-size: 11px; fill: #5a665d; }",
        ".room { stroke: #2f4236; stroke-width: 2; }",
        ".inferred { stroke-dasharray: 6 4; }",
        ".measured { stroke-dasharray: none; }",
        "</style>",
        '<rect x="0" y="0" width="100%" height="100%" fill="#fbfaf6"/>',
        f'<text class="title" x="{margin}" y="30">{escape(title)}</text>',
    ]

    for room in model.rooms:
        parts.append(_render_room(room, sx, sy, scale, model=model, season=season, time_band=time_band))

    anchors = {item["id"]: item for item in model.raw["anchors"]}
    notes_y = height - 128
    anchor_notes = [
        f'Long side anchor: {anchors["long_side_master_to_laundry"]["value_m"]}m',
        f'External depth anchor: {anchors["combined_external_depth"]["value_m"]}m',
        f'Master frontage: {anchors["master_street_frontage"]["value_m"]}m',
    ]
    for idx, note in enumerate(anchor_notes):
        parts.append(f'<text class="dim" x="{margin}" y="{notes_y + idx * 18}">{escape(note)}</text>')

    legend_x = margin + 315
    legend_y = notes_y
    parts.extend(
        [
            f'<text class="dim" x="{legend_x}" y="{legend_y}">Layout confidence</text>',
            f'<line x1="{legend_x}" y1="{legend_y + 17}" x2="{legend_x + 44}" y2="{legend_y + 17}" stroke="#2f4236" stroke-width="2" stroke-dasharray="6 4"/>',
            f'<text class="note" x="{legend_x + 55}" y="{legend_y + 21}">dashed = inferred</text>',
            f'<text class="note" x="{legend_x}" y="{legend_y + 43}">Room dimensions are measured; drawn positions are inferred.</text>',
        ]
    )
    if daylight_active:
        parts.extend(_render_daylight_legend(legend_x, legend_y + 65))

    parts.append("</svg>")
    return "\n".join(parts)


def render_overlay_svg(model: HouseModel) -> str:
    calibration = model.raw.get("overlay_calibration", {})
    canvas = calibration.get("canvas_px", {"width": 1600, "height": 900})
    width = int(canvas["width"])
    height = int(canvas["height"])
    reference_image = calibration.get("reference_image", "House-Outline-Internal-walls.png")
    opacity = float(calibration.get("opacity", 0.42))
    pixel_layout = model.raw.get("reference_pixel_layout", {})
    pixel_rooms = pixel_layout.get("rooms", [])
    pixel_openings = pixel_layout.get("openings", [])
    pixel_source = pixel_layout.get("source", "DATA/house_model.json")
    current_structure = model.raw.get("current_structure", {})
    current_spaces = current_structure.get("spaces", [])
    current_features = current_structure.get("features", [])
    current_site = model.raw.get("current_site", {})
    current_site_elements = current_site.get("elements", [])

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text { font-family: Arial, sans-serif; fill: #203026; }",
        ".title { font-size: 18px; font-weight: 700; }",
        ".label { font-size: 10px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; }",
        ".room-overlay { stroke: #005bbb; stroke-width: 3; fill: #5aa6ff; }",
        ".sunroom-overlay { stroke: #d43f00; fill: #ffb36c; }",
        ".opening-overlay { stroke: #d06a00; stroke-width: 3; fill: #ffe0b6; }",
        ".opening-overlay.window { stroke: #007f93; fill: #c9f1fb; }",
        ".opening-overlay.slider { stroke: #7a32b8; fill: #ead7ff; }",
        ".opening-overlay.door_gap { stroke: #b65400; fill: #fff0d8; }",
        ".current-space { stroke: #167a3f; stroke-width: 4; fill: #7bd88f; fill-opacity: 0.26; }",
        ".current-feature { stroke: #0b5f33; stroke-width: 5; fill: #42c56a; fill-opacity: 0.68; }",
        ".current-feature.window_group { stroke: #00816f; fill: #8ee6d2; }",
        ".current-site { stroke: #7a5f1d; stroke-width: 3; fill: #d8c46b; fill-opacity: 0.20; }",
        ".current-site.hardscape { stroke: #6f6b61; fill: #c8c2b5; fill-opacity: 0.42; }",
        ".current-site.deck { stroke: #7d5a2f; fill: #c79153; fill-opacity: 0.48; }",
        ".current-site.building { stroke: #4d5b40; fill: #b7cf9a; fill-opacity: 0.46; }",
        ".current-site.planting { stroke: #326b3a; fill: #4f9a58; fill-opacity: 0.30; }",
        "</style>",
        f'<image href="{escape(reference_image)}" x="0" y="0" width="{width}" height="{height}" preserveAspectRatio="none"/>',
        '<rect x="0" y="0" width="100%" height="100%" fill="white" opacity="0.08"/>',
        '<text class="title" x="32" y="42">Calibration Overlay</text>',
        f'<text x="32" y="62" font-size="11">Reference pixel layout: {escape(pixel_source)}</text>',
        f'<g id="model-overlay" opacity="{opacity:g}">',
    ]

    if pixel_rooms:
        room_names = {room.id: room.name for room in model.rooms}
        for room in pixel_rooms:
            parts.append(_render_pixel_overlay_room(room, room_names.get(room["id"], room["id"])))
    else:
        bounds_px = calibration.get("model_bounds_px", {"x": 520, "y": 313, "width": 420, "height": 297})
        min_x, min_y, max_x, max_y = _bounds(model.rooms)
        scale_x = float(bounds_px["width"]) / (max_x - min_x)
        scale_y = float(bounds_px["height"]) / (max_y - min_y)

        def sx(x: float) -> float:
            return float(bounds_px["x"]) + (x - min_x) * scale_x

        def sy(y: float) -> float:
            return float(bounds_px["y"]) + (y - min_y) * scale_y

        for room in model.rooms:
            parts.append(_render_overlay_room(room, sx, sy))

    if pixel_openings:
        parts.append('<g id="opening-overlay" opacity="0.9">')
        for opening in pixel_openings:
            parts.append(_render_pixel_opening(opening))
        parts.append("</g>")

    if current_spaces or current_features:
        parts.append('<g id="current-structure-overlay" opacity="0.96">')
        for space in current_spaces:
            parts.append(_render_current_structure_item(space, "current-space"))
        for feature in current_features:
            parts.append(_render_current_structure_item(feature, f"current-feature {feature.get('type', 'feature')}"))
        parts.append("</g>")

    if current_site_elements:
        parts.append('<g id="current-site-overlay" opacity="0.9">')
        for element in current_site_elements:
            parts.append(_render_site_item(element, f"current-site {element.get('category', 'site')}"))
        parts.append("</g>")

    parts.extend(
        [
            "</g>",
            '<text x="32" y="82" font-size="12">Blue/orange model layer is generated from DATA/house_model.json.</text>',
            '<text x="32" y="100" font-size="12">Current structure: photo/measured source of truth. Legacy pixels remain for comparison.</text>',
            '<text x="32" y="118" font-size="12">Current site: external source of truth for outside design and shadow/light context.</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts)


def write_svg(path: str | Path, svg: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)


def _bounds(rooms: list[Room]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for room in rooms:
        layout = room.layout
        if layout.get("type") == "polygon":
            for x, y in layout["points"]:
                xs.append(float(x))
                ys.append(float(y))
        else:
            x = float(layout.get("x", 0))
            y = float(layout.get("y", 0))
            xs.extend([x, x + float(layout.get("width", 0))])
            ys.extend([y, y + float(layout.get("depth", 0))])
    return min(xs), min(ys), max(xs), max(ys)


def _render_room(
    room: Room,
    sx: Any,
    sy: Any,
    scale: float,
    *,
    model: HouseModel,
    season: str | None,
    time_band: str | None,
) -> str:
    layout = room.layout
    fill = CATEGORY_FILL.get(room.category, "#e8e2d5")
    attrs = ""
    daylight_title = ""
    if season is not None and time_band is not None:
        daylight_room = model.raw.get("daylight", {}).get("rooms", {}).get(room.id, {})
        light_level = daylight_room.get(season, {}).get(time_band, "unknown")
        fill = LIGHT_FILL.get(light_level, LIGHT_FILL["unknown"])
        attrs = f' data-light-level="{escape(light_level)}"'
        note = daylight_room.get("notes", "")
        daylight_title = f" Daylight {season} {time_band}: {light_level}. {note}"
    confidence = layout.get("confidence", room.confidence)
    confidence_class = "measured" if confidence == "measured" else "inferred"
    title = escape(("; ".join(room.notes) or room.name) + daylight_title)

    if layout.get("type") == "polygon":
        points = " ".join(f"{sx(float(x)):.1f},{sy(float(y)):.1f}" for x, y in layout["points"])
        cx = sum(float(x) for x, _ in layout["points"]) / len(layout["points"])
        cy = sum(float(y) for _, y in layout["points"]) / len(layout["points"])
        shape = f'<polygon class="room {confidence_class}" points="{points}" fill="{fill}"{attrs}><title>{title}</title></polygon>'
    else:
        x = float(layout["x"])
        y = float(layout["y"])
        width = float(layout["width"])
        depth = float(layout["depth"])
        cx = x + width / 2
        cy = y + depth / 2
        shape = (
            f'<rect class="room {confidence_class}" x="{sx(x):.1f}" y="{sy(y):.1f}" '
            f'width="{width * scale:.1f}" height="{depth * scale:.1f}" fill="{fill}">'
            f"<title>{title}</title></rect>"
        )
        if attrs:
            shape = shape.replace(' fill="', f'{attrs} fill="', 1)

    label = escape(room.name)
    dims = _dimension_label(room)
    return "\n".join(
        [
            shape,
            f'<text class="label" x="{sx(cx):.1f}" y="{sy(cy):.1f}">{label}</text>',
            f'<text class="dim" text-anchor="middle" x="{sx(cx):.1f}" y="{sy(cy) + 16:.1f}">{escape(dims)}</text>',
        ]
    )


def _dimension_label(room: Room) -> str:
    dims = room.dimensions_m
    length = dims.get("length")
    width = dims.get("width")
    if length is None or width is None:
        return "irregular"
    return f"{length:g}m x {width:g}m"


def _render_daylight_legend(x: float, y: float) -> list[str]:
    items = [
        ("high", LIGHT_FILL["high"]),
        ("medium", LIGHT_FILL["medium"]),
        ("low", LIGHT_FILL["low"]),
    ]
    parts = [f'<text class="note" x="{x}" y="{y}">high / medium / low daylight</text>']
    for idx, (label, fill) in enumerate(items):
        item_x = x + idx * 82
        parts.append(f'<rect x="{item_x}" y="{y + 10}" width="18" height="12" fill="{fill}" stroke="#67736a"/>')
        parts.append(f'<text class="note" x="{item_x + 24}" y="{y + 21}">{label}</text>')
    return parts


def _render_overlay_room(room: Room, sx: Any, sy: Any) -> str:
    layout = room.layout
    css_class = "room-overlay sunroom-overlay" if room.id == "sunroom" else "room-overlay"
    if layout.get("type") == "polygon":
        points = " ".join(f"{sx(float(x)):.1f},{sy(float(y)):.1f}" for x, y in layout["points"])
        cx = sum(float(x) for x, _ in layout["points"]) / len(layout["points"])
        cy = sum(float(y) for _, y in layout["points"]) / len(layout["points"])
        shape = f'<polygon class="{css_class}" points="{points}"><title>{escape(room.name)}</title></polygon>'
    else:
        x = float(layout["x"])
        y = float(layout["y"])
        width = float(layout["width"])
        depth = float(layout["depth"])
        cx = x + width / 2
        cy = y + depth / 2
        shape = (
            f'<rect class="{css_class}" x="{sx(x):.1f}" y="{sy(y):.1f}" '
            f'width="{(sx(x + width) - sx(x)):.1f}" height="{(sy(y + depth) - sy(y)):.1f}">'
            f"<title>{escape(room.name)}</title></rect>"
        )
    return "\n".join(
        [
            shape,
            f'<text class="label" x="{sx(cx):.1f}" y="{sy(cy):.1f}">{escape(room.name)}</text>',
        ]
    )


def _render_pixel_overlay_room(room: dict[str, Any], name: str) -> str:
    css_class = "room-overlay sunroom-overlay" if room["id"] == "sunroom" else "room-overlay"
    if room.get("type") == "polygon":
        points = " ".join(f"{float(x):.1f},{float(y):.1f}" for x, y in room["points"])
        cx = sum(float(x) for x, _ in room["points"]) / len(room["points"])
        cy = sum(float(y) for _, y in room["points"]) / len(room["points"])
        shape = f'<polygon class="{css_class}" points="{points}"><title>{escape(name)}</title></polygon>'
    else:
        x = float(room["x"])
        y = float(room["y"])
        width = float(room["width"])
        height = float(room["height"])
        cx = x + width / 2
        cy = y + height / 2
        shape = (
            f'<rect class="{css_class}" x="{x:.1f}" y="{y:.1f}" '
            f'width="{width:.1f}" height="{height:.1f}"><title>{escape(name)}</title></rect>'
        )
    return "\n".join(
        [
            shape,
            f'<text class="label" x="{cx:.1f}" y="{cy:.1f}">{escape(name)}</text>',
        ]
    )


def _render_pixel_opening(opening: dict[str, Any]) -> str:
    opening_id = opening["id"]
    opening_type = opening.get("type", "opening")
    points = " ".join(f"{float(x):.1f},{float(y):.1f}" for x, y in opening["polygon"])
    title_parts = [opening_id, opening_type]
    if "room" in opening:
        title_parts.append(f"room: {opening['room']}")
    if "between" in opening:
        title_parts.append("between: " + " / ".join(opening["between"]))
    title = "; ".join(str(part) for part in title_parts)
    return (
        f'<polygon class="opening-overlay {escape(opening_type)}" '
        f'data-opening-id="{escape(opening_id)}" points="{points}">'
        f"<title>{escape(title)}</title></polygon>"
    )


def _render_current_structure_item(item: dict[str, Any], css_class: str) -> str:
    return _render_display_item(item, css_class, "data-current-id", "current_structure")


def _render_site_item(item: dict[str, Any], css_class: str) -> str:
    return _render_display_item(item, css_class, "data-site-id", "current_site")


def _render_display_item(item: dict[str, Any], css_class: str, data_attr: str, comment_prefix: str) -> str:
    item_id = str(item["id"])
    geometry = item.get("display_px", {})
    title = f"{item_id}; {item.get('status', item.get('confidence', 'unknown'))}"
    if geometry.get("type") == "multi_polygon":
        parts = []
        for polygon in geometry.get("polygons", []):
            points = " ".join(f"{float(x):.1f},{float(y):.1f}" for x, y in polygon)
            parts.append(
                f'<polygon class="{escape(css_class)}" {data_attr}="{escape(item_id)}" '
                f'points="{points}"><title>{escape(title)}</title></polygon>'
            )
        return "\n".join(parts)
    if geometry.get("type") == "polygon":
        points = " ".join(f"{float(x):.1f},{float(y):.1f}" for x, y in geometry["points"])
        return (
            f'<polygon class="{escape(css_class)}" {data_attr}="{escape(item_id)}" '
            f'points="{points}"><title>{escape(title)}</title></polygon>'
        )
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
    return f'<!-- {escape(comment_prefix)} item {escape(item_id)} has no renderable display_px geometry -->'
