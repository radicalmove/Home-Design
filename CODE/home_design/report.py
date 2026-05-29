from __future__ import annotations

from .geometry import layout_bounds
from .model import HouseModel
from .validate import SEASONS, TIME_BANDS


def render_calibration_report(model: HouseModel) -> str:
    lines = [
        "# Home Design Calibration Report",
        "",
        "## Wall Assumptions",
        "",
    ]
    assumptions = model.raw.get("assumptions", {})
    lines.extend(
        [
            f"- Exterior wall thickness: {_m(assumptions.get('exterior_wall_thickness_m'))}",
            f"- Internal wall thickness: {_m(assumptions.get('internal_wall_thickness_m'))}",
            f"- Sunroom frame thickness: {_m(assumptions.get('sunroom_frame_thickness_m'))}",
            "",
            "## External Anchors",
            "",
        ]
    )
    for anchor in model.raw.get("anchors", []):
        confidence = anchor.get("confidence", "unknown")
        tolerance = ""
        if "tolerance_m" in anchor:
            tolerance = f" +/- {_m(anchor['tolerance_m'])}"
        lines.append(f"- {anchor['label']}: {_m(anchor['value_m'])}{tolerance} ({confidence})")

    sunroom = model.room("sunroom")
    segments = model.raw_room("sunroom").get("measured_segments_m", [])
    if segments:
        lines.extend(["", "## Sunroom Hand Measurements", ""])
        source = model.raw_room("sunroom").get("measurement_source", {})
        if source.get("path"):
            lines.append(f"- Source: {source['path']}")
        for segment in segments:
            lines.append(f"- {segment['label']}: {_m(segment['value_m'])} ({segment.get('confidence', 'unknown')})")
        lines.append(f"- Layout status: {sunroom.layout.get('confidence', 'unknown')}")

    pixel_layout = model.raw.get("reference_pixel_layout", {})
    pixel_openings = pixel_layout.get("openings", [])
    if pixel_openings:
        lines.extend(["", "## Calibrated Pixel Openings", ""])
        lines.append(f"- Source: {pixel_layout.get('source', 'unknown')}")
        lines.append(f"- Count: {len(pixel_openings)}")
        for opening in pixel_openings:
            location = opening.get("room")
            if location is None and "between" in opening:
                location = " / ".join(opening["between"])
            lines.append(
                f"- {opening['id']}: {opening.get('type', 'opening')} at {location or 'unknown'} "
                f"({opening.get('confidence', 'unknown')})"
            )

    photo_checks = model.raw.get("photo_evidence", {}).get("checks", [])
    if photo_checks:
        lines.extend(["", "## Photo Evidence Checks", ""])
        for check in photo_checks:
            features = ", ".join(check.get("feature_ids", []))
            lines.append(f"- {check['id']}: {check.get('status', 'unknown')} for {features}")
            summary = check.get("summary")
            if summary:
                lines.append(f"  Evidence: {summary}")
            for photo in check.get("photos", []):
                lines.append(f"  Photo: {photo['path']} - {photo.get('view', 'reference')}")

    current_structure = model.raw.get("current_structure", {})
    if current_structure:
        lines.extend(["", "## Current Structure", ""])
        lines.append(f"- Status: {current_structure.get('status', 'unknown')}")
        lines.append(f"- Method: {current_structure.get('method', 'unknown')}")
        legacy_layers = ", ".join(current_structure.get("legacy_layers", []))
        lines.append(f"- Legacy comparison layers: {legacy_layers or 'none'}")
        spaces = current_structure.get("spaces", [])
        built_ins = current_structure.get("built_ins", [])
        features = current_structure.get("features", [])
        lines.append(f"- Spaces promoted: {len(spaces)}")
        for space in spaces:
            checks = ", ".join(space.get("evidence_check_ids", []))
            lines.append(f"  Space: {space['id']} ({space.get('confidence', 'unknown')}; evidence: {checks or 'none'})")
        lines.append(f"- Built-ins recorded: {len(built_ins)}")
        for item in built_ins:
            checks = ", ".join(item.get("evidence_check_ids", []))
            lines.append(
                f"  Built-in: {item['id']} ({item.get('type', 'built_in')}; "
                f"{item.get('status', 'unknown')}; evidence: {checks or 'none'})"
            )
        lines.append(f"- Features promoted: {len(features)}")
        for feature in features:
            checks = ", ".join(feature.get("evidence_check_ids", []))
            lines.append(
                f"  Feature: {feature['id']} ({feature.get('type', 'feature')}; "
                f"{feature.get('status', 'unknown')}; evidence: {checks or 'none'})"
            )
            detail = _feature_detail(feature)
            if detail:
                lines.append(f"    Detail: {detail}")

    current_site = model.raw.get("current_site", {})
    if current_site:
        lines.extend(["", "## Current Site", ""])
        lines.append(f"- Status: {current_site.get('status', 'unknown')}")
        lines.append(f"- Method: {current_site.get('method', 'unknown')}")
        legacy_layers = ", ".join(current_site.get("legacy_layers", []))
        lines.append(f"- Legacy comparison layers: {legacy_layers or 'none'}")
        elements = current_site.get("elements", [])
        shadow_sources = current_site.get("shadow_sources", [])
        lines.append(f"- Site elements promoted: {len(elements)}")
        for element in elements:
            checks = ", ".join(element.get("evidence_check_ids", []))
            lines.append(
                f"  Site: {element['id']} ({element.get('category', 'site')}; "
                f"{element.get('confidence', element.get('status', 'unknown'))}; evidence: {checks or 'none'})"
            )
        lines.append(f"- Shadow sources promoted: {len(shadow_sources)}")
        for source in shadow_sources:
            checks = ", ".join(source.get("evidence_check_ids", []))
            lines.append(
                f"  Shadow source: {source['id']} ({source.get('type', 'shadow_source')}; "
                f"{source.get('status', 'unknown')}; evidence: {checks or 'none'})"
            )

    lines.extend(["", "## Layout Confidence", ""])
    for room in model.rooms:
        layout_confidence = room.layout.get("confidence", "unknown")
        lines.append(f"- {room.name}: dimensions {room.confidence}; layout {layout_confidence}")

    lines.extend(["", "## Daylight Coverage", ""])
    daylight = model.raw.get("daylight", {}).get("rooms", {})
    for room in model.rooms:
        room_daylight = daylight.get(room.id, {})
        known = _daylight_value_count(room_daylight)
        total = len(SEASONS) * len(TIME_BANDS)
        confidence = room_daylight.get("confidence", "unknown")
        lines.append(f"- {room.name}: {known}/{total} season/time values ({confidence})")

    lines.extend(["", "## Geometry Sanity", ""])
    min_x, min_y, max_x, max_y = layout_bounds(model.rooms)
    targets = _wall_adjusted_targets(model)
    lines.extend(
        [
            f"- Inferred layout bounds: {_m(max_x - min_x)} x {_m(max_y - min_y)}",
            f"- Wall-adjusted internal target: {_m(targets['long_side_internal_m'])} x {_m(targets['depth_internal_m'])}",
            "- This bound is a drawing/model bound, not yet a verified exterior footprint.",
            "- External anchors should be used to calibrate the next coordinate pass.",
        ]
    )

    lines.extend(["", "## Next Measurements", ""])
    lines.extend(
        [
            "- Sunroom exterior segment lengths, including angled/inset door face.",
            "- Eave overhang on at least one straight wall and one sunroom edge.",
            "- Window positions and widths for the main daylight rooms.",
            "- Garage-to-house distance and driveway/deck hardscape edges.",
            "- A confirmed compass/site north reference for more precise sun-path work.",
        ]
    )

    return "\n".join(lines) + "\n"


def _m(value: object) -> str:
    if isinstance(value, int | float):
        return f"{value:g}m"
    return "unknown"


def _feature_detail(feature: dict[str, object]) -> str:
    parts: list[str] = []
    if "width_m" in feature:
        parts.append(f"width {_m(feature['width_m'])}")
    offsets = feature.get("wall_offsets_m")
    if isinstance(offsets, dict):
        formatted_offsets = ", ".join(f"{key} {_m(value)}" for key, value in offsets.items())
        if formatted_offsets:
            parts.append(f"offsets {formatted_offsets}")
    position_reference = feature.get("position_reference")
    if isinstance(position_reference, str):
        parts.append(f"position {position_reference}")
    swing = feature.get("swing")
    if isinstance(swing, str):
        parts.append(f"swing {swing}")
    projection = feature.get("right_corner_nub_projection_m")
    if projection is not None:
        parts.append(f"right corner nub projection {_m(projection)}")
    return "; ".join(parts)


def _daylight_value_count(room_daylight: dict[str, object]) -> int:
    count = 0
    for season in SEASONS:
        values = room_daylight.get(season, {})
        if not isinstance(values, dict):
            continue
        for band in TIME_BANDS:
            if band in values:
                count += 1
    return count


def _wall_adjusted_targets(model: HouseModel) -> dict[str, float]:
    anchors = {anchor["id"]: anchor for anchor in model.raw.get("anchors", [])}
    exterior_wall = float(model.raw.get("assumptions", {}).get("exterior_wall_thickness_m", 0))
    return {
        "long_side_internal_m": round(float(anchors["long_side_master_to_laundry"]["value_m"]) - 2 * exterior_wall, 2),
        "depth_internal_m": round(float(anchors["combined_external_depth"]["value_m"]) - 2 * exterior_wall, 2),
    }
