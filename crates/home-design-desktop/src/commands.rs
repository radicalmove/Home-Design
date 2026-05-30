use home_design_core::{
    AppStatus, HouseModel, HouseModelSummary, ProjectManifest, app_status,
    built_in_project_manifest, summarize_house_model, validate_house_model,
};
use serde::{Deserialize, Serialize};

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
