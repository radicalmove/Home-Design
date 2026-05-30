use crate::{HouseModel, ModeledItem};
use serde_json::Value;
use std::collections::BTreeSet;

const SEASONS: &[&str] = &["summer", "autumn", "winter", "spring"];
const TIME_BANDS: &[&str] = &["morning", "midday", "afternoon"];
const LIGHT_LEVELS: &[&str] = &["low", "medium", "high", "unknown"];
const REQUIRED_ANCHORS: &[&str] = &[
    "long_side_master_to_laundry",
    "combined_external_depth",
    "master_street_frontage",
    "dining_edge_to_entrance_laundry_edge",
    "laundry_toilet_projection_wall",
];

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ModelValidationResult {
    pub errors: Vec<String>,
    pub warnings: Vec<String>,
}

impl ModelValidationResult {
    pub fn ok(&self) -> bool {
        self.errors.is_empty()
    }
}

pub fn validate_house_model(model: &HouseModel) -> ModelValidationResult {
    let mut result = ModelValidationResult::default();

    validate_top_level_contract(model, &mut result);
    validate_current_structure(model, &mut result);
    validate_current_site(model, &mut result);
    validate_daylight(model, &mut result);

    result
}

fn validate_top_level_contract(model: &HouseModel, result: &mut ModelValidationResult) {
    if model.units != "metres" {
        result.errors.push("units must be metres".to_string());
    }

    if !float_eq(model.assumptions.exterior_wall_thickness_m, Some(0.30)) {
        result
            .warnings
            .push("exterior wall thickness differs from current 0.30m assumption".to_string());
    }
    if !float_eq(model.assumptions.internal_wall_thickness_m, Some(0.14)) {
        result
            .errors
            .push("internal wall thickness must be 0.14m".to_string());
    }

    for anchor_id in REQUIRED_ANCHORS {
        if model.anchor_value_m(anchor_id).is_none() {
            result.errors.push(format!("missing anchor: {anchor_id}"));
        }
    }

    for room in &model.rooms {
        if !room.dimensions_m.contains_key("height") {
            result
                .errors
                .push(format!("missing ceiling height for {}", room.id));
        }
        if is_missing_json_value(&room.layout) {
            result
                .errors
                .push(format!("missing layout for {}", room.id));
        }
    }
}

fn validate_current_structure(model: &HouseModel, result: &mut ModelValidationResult) {
    if model.current_structure.status != "active_source_of_truth" {
        result
            .errors
            .push("current_structure.status must be active_source_of_truth".to_string());
    }

    let photo_check_ids = photo_check_ids(model);
    validate_items(
        "current_structure.spaces",
        &model.current_structure.spaces,
        &photo_check_ids,
        result,
    );
    validate_items(
        "current_structure.built_ins",
        &model.current_structure.built_ins,
        &photo_check_ids,
        result,
    );
    validate_items(
        "current_structure.features",
        &model.current_structure.features,
        &photo_check_ids,
        result,
    );
}

fn validate_current_site(model: &HouseModel, result: &mut ModelValidationResult) {
    if model.current_site.status != "active_site_source_of_truth" {
        result
            .errors
            .push("current_site.status must be active_site_source_of_truth".to_string());
    }

    let photo_check_ids = photo_check_ids(model);
    validate_items(
        "current_site.elements",
        &model.current_site.elements,
        &photo_check_ids,
        result,
    );
    validate_items(
        "current_site.shadow_sources",
        &model.current_site.shadow_sources,
        &photo_check_ids,
        result,
    );

    let site_element_ids = model
        .current_site
        .elements
        .iter()
        .map(|item| item.id.as_str())
        .collect::<BTreeSet<_>>();
    let structure_ids = model.current_structure.item_ids().collect::<BTreeSet<_>>();
    let room_ids = model
        .rooms
        .iter()
        .map(|room| room.id.as_str())
        .collect::<BTreeSet<_>>();

    for shadow_source in &model.current_site.shadow_sources {
        for affected_id in shadow_source.string_list("affects").unwrap_or_default() {
            let is_valid = site_element_ids.contains(affected_id.as_str())
                || structure_ids.contains(affected_id.as_str())
                || room_ids.contains(affected_id.as_str());
            if !is_valid {
                result.errors.push(format!(
                    "current_site.shadow_sources.{} affects unknown feature: {affected_id}",
                    shadow_source.id
                ));
            }
        }
    }
}

fn validate_daylight(model: &HouseModel, result: &mut ModelValidationResult) {
    for room in &model.rooms {
        let Some(matrix) = model.daylight.rooms.get(&room.id) else {
            result
                .errors
                .push(format!("missing daylight matrix for {}", room.id));
            continue;
        };

        for season in SEASONS {
            let Some(season_value) = matrix.get(*season) else {
                result
                    .errors
                    .push(format!("missing {season} daylight for {}", room.id));
                continue;
            };

            for band in TIME_BANDS {
                let value = season_value.get(*band).and_then(Value::as_str);
                if !value.is_some_and(|level| LIGHT_LEVELS.contains(&level)) {
                    let rendered = value.unwrap_or("missing");
                    result.errors.push(format!(
                        "invalid daylight value for {}.{season}.{band}: {rendered}",
                        room.id
                    ));
                }
            }
        }
    }
}

fn validate_items(
    context: &str,
    items: &[ModeledItem],
    photo_check_ids: &BTreeSet<&str>,
    result: &mut ModelValidationResult,
) {
    for item in items {
        if item.display_px.is_none() {
            result
                .errors
                .push(format!("{context}.{} missing display_px", item.id));
        }
        for check_id in &item.evidence_check_ids {
            if !photo_check_ids.contains(check_id.as_str()) {
                result.errors.push(format!(
                    "{context}.{} references unknown evidence check: {check_id}",
                    item.id
                ));
            }
        }
    }
}

fn photo_check_ids(model: &HouseModel) -> BTreeSet<&str> {
    model.photo_check_ids().into_iter().collect()
}

fn float_eq(actual: Option<f64>, expected: Option<f64>) -> bool {
    match (actual, expected) {
        (Some(actual), Some(expected)) => (actual - expected).abs() < 0.000_001,
        (None, None) => true,
        _ => false,
    }
}

fn is_missing_json_value(value: &Value) -> bool {
    value.is_null() || value.as_object().is_some_and(serde_json::Map::is_empty)
}
