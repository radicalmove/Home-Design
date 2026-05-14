from __future__ import annotations

from dataclasses import dataclass

from .model import HouseModel


SEASONS = ("summer", "autumn", "winter", "spring")
TIME_BANDS = ("morning", "midday", "afternoon")
LIGHT_LEVELS = ("low", "medium", "high", "unknown")


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_model(model: HouseModel) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    raw = model.raw

    if raw.get("units") != "metres":
        errors.append("units must be metres")

    assumptions = raw.get("assumptions", {})
    if assumptions.get("exterior_wall_thickness_m") != 0.30:
        warnings.append("exterior wall thickness differs from current 0.30m assumption")
    if assumptions.get("internal_wall_thickness_m") != 0.14:
        errors.append("internal wall thickness must be 0.14m")

    anchors = {item.get("id"): item for item in raw.get("anchors", [])}
    for anchor_id in [
        "long_side_master_to_laundry",
        "combined_external_depth",
        "master_street_frontage",
        "dining_edge_to_entrance_laundry_edge",
        "laundry_toilet_projection_wall",
    ]:
        if anchor_id not in anchors:
            errors.append(f"missing anchor: {anchor_id}")

    for room in model.rooms:
        dimensions = room.dimensions_m
        if "height" not in dimensions:
            errors.append(f"missing ceiling height for {room.id}")
        if not room.layout:
            errors.append(f"missing layout for {room.id}")

    photo_check_ids = {check.get("id") for check in raw.get("photo_evidence", {}).get("checks", [])}
    current_structure = raw.get("current_structure", {})
    if current_structure:
        if current_structure.get("status") != "active_source_of_truth":
            errors.append("current_structure.status must be active_source_of_truth")
        for item_type in ("spaces", "features"):
            for item in current_structure.get(item_type, []):
                item_id = item.get("id", "unknown")
                if not item.get("display_px"):
                    errors.append(f"current_structure.{item_type}.{item_id} missing display_px")
                for check_id in item.get("evidence_check_ids", []):
                    if check_id not in photo_check_ids:
                        errors.append(f"current_structure.{item_type}.{item_id} references unknown evidence check: {check_id}")

    current_site = raw.get("current_site", {})
    if current_site:
        if current_site.get("status") != "active_site_source_of_truth":
            errors.append("current_site.status must be active_site_source_of_truth")
        site_element_ids = {item.get("id") for item in current_site.get("elements", [])}
        current_structure_ids = {
            item.get("id")
            for item_type in ("spaces", "features")
            for item in current_structure.get(item_type, [])
        }
        valid_site_affect_ids = site_element_ids | current_structure_ids | {room.id for room in model.rooms}
        for item_type in ("elements", "shadow_sources"):
            for item in current_site.get(item_type, []):
                item_id = item.get("id", "unknown")
                if not item.get("display_px"):
                    errors.append(f"current_site.{item_type}.{item_id} missing display_px")
                for check_id in item.get("evidence_check_ids", []):
                    if check_id not in photo_check_ids:
                        errors.append(f"current_site.{item_type}.{item_id} references unknown evidence check: {check_id}")
                if item_type == "shadow_sources":
                    for affected_id in item.get("affects", []):
                        if affected_id not in valid_site_affect_ids:
                            errors.append(f"current_site.shadow_sources.{item_id} affects unknown feature: {affected_id}")

    daylight = raw.get("daylight", {}).get("rooms", {})
    for room in model.rooms:
        matrix = daylight.get(room.id)
        if not matrix:
            errors.append(f"missing daylight matrix for {room.id}")
            continue
        for season in SEASONS:
            if season not in matrix:
                errors.append(f"missing {season} daylight for {room.id}")
                continue
            for band in TIME_BANDS:
                value = matrix[season].get(band)
                if value not in LIGHT_LEVELS:
                    errors.append(f"invalid daylight value for {room.id}.{season}.{band}: {value}")

    return ValidationResult(errors=errors, warnings=warnings)
