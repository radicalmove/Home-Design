use home_design_core::{
    AppStatus, HouseModel, HouseModelSummary, ProjectManifest, app_status,
    built_in_project_manifest, summarize_house_model, validate_house_model,
};
use crate::furniture_storage::{FurnitureLayoutLoadResult, load_furniture_layout_from_root};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::path::Path;

const BUILT_IN_MODEL_SOURCE_PATH: &str = "DATA/house_model.json";
const BUILT_IN_MODEL_JSON: &str = include_str!("../../../DATA/house_model.json");

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BuiltInModelStatus {
    pub source_path: String,
    pub summary: HouseModelSummary,
    pub valid: bool,
    pub validation_error_count: usize,
    pub validation_warning_count: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DesignReviewData {
    pub model_source: String,
    pub house_model: Value,
    pub furniture_layout: FurnitureLayoutLoadResult,
}

pub fn get_app_status() -> AppStatus {
    app_status()
}

pub fn load_builtin_project() -> ProjectManifest {
    built_in_project_manifest()
}

pub fn load_builtin_model_status() -> Result<BuiltInModelStatus, String> {
    let model =
        HouseModel::from_json_str(BUILT_IN_MODEL_JSON).map_err(|error| error.to_string())?;
    let validation = validate_house_model(&model);

    Ok(BuiltInModelStatus {
        source_path: BUILT_IN_MODEL_SOURCE_PATH.to_string(),
        summary: summarize_house_model(&model),
        valid: validation.ok(),
        validation_error_count: validation.errors.len(),
        validation_warning_count: validation.warnings.len(),
    })
}

pub fn load_design_review_data_from_root(
    root: &Path,
    project_id: &str,
    scenario_id: &str,
) -> Result<DesignReviewData, String> {
    let house_model = HouseModel::from_json_str(BUILT_IN_MODEL_JSON)
        .map_err(|error| error.to_string())?;
    let validation = validate_house_model(&house_model);
    if !validation.ok() {
        return Err(format!(
            "invalid built-in model: {}",
            validation.errors.join("; ")
        ));
    }

    let house_model_value: Value = serde_json::from_str(BUILT_IN_MODEL_JSON)
        .map_err(|error| format!("could not parse built-in model JSON: {error}"))?;
    let furniture_layout = load_furniture_layout_from_root(root, project_id, scenario_id)?;

    Ok(DesignReviewData {
        model_source: BUILT_IN_MODEL_SOURCE_PATH.to_string(),
        house_model: house_model_value,
        furniture_layout,
    })
}
