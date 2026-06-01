use serde::{Deserialize, Serialize};

mod furniture;
mod model;
mod validation;

pub use furniture::{
    FurnitureCatalog, FurnitureCatalogGroup, FurnitureCatalogItem, FurnitureLShapeDimensions,
    FurnitureLayerKind, FurnitureLayout, FurnitureObject, FurnitureValidationResult, PlanPoint,
    PlanTransform, default_furniture_catalog, default_plan_transform, normalise_furniture_z_order,
    seed_current_furniture_layout, validate_furniture_layout,
};
pub use model::{
    Anchor, Assumptions, CurrentSite, CurrentStructure, Daylight, GeometryKind, HouseModel,
    HouseModelSummary, MeasurementAudit, MeasurementAuditItem, MeasurementAuditSummary,
    ModelLoadError, ModeledItem, PhotoEvidence, PhotoEvidenceCheck, Room,
    load_house_model_from_path, summarize_house_model,
};
pub use validation::{ModelValidationResult, validate_house_model};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppStatus {
    pub app_name: String,
    pub runtime: String,
    pub built_in_project_count: usize,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ViewMode {
    BasePlan,
    ThreeDNavigation,
    FurnitureEditor,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ViewDescriptor {
    pub id: String,
    pub label: String,
    pub mode: ViewMode,
    pub asset_path: String,
    pub available: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProjectManifest {
    pub id: String,
    pub name: String,
    pub model_version: String,
    pub model_source: String,
    pub views: Vec<ViewDescriptor>,
    pub scenarios: Vec<String>,
    pub layers: Vec<String>,
    pub object_catalogs: Vec<String>,
    pub analysis_outputs: Vec<String>,
}

pub fn app_status() -> AppStatus {
    AppStatus {
        app_name: "Home Design".to_string(),
        runtime: "tauri-desktop".to_string(),
        built_in_project_count: 1,
    }
}

pub fn built_in_project_manifest() -> ProjectManifest {
    ProjectManifest {
        id: "current-house".to_string(),
        name: "Current House".to_string(),
        model_version: "current-generated-views".to_string(),
        model_source: "DATA/house_model.json".to_string(),
        views: vec![
            ViewDescriptor {
                id: "base-view".to_string(),
                label: "Base View".to_string(),
                mode: ViewMode::BasePlan,
                asset_path: "/views/reference_plan.html".to_string(),
                available: true,
            },
            ViewDescriptor {
                id: "three-d-navigation".to_string(),
                label: "3D Navigation".to_string(),
                mode: ViewMode::ThreeDNavigation,
                asset_path: "/views/house_3d.html".to_string(),
                available: true,
            },
            ViewDescriptor {
                id: "furniture-editor".to_string(),
                label: "Furniture Editor".to_string(),
                mode: ViewMode::FurnitureEditor,
                asset_path: "/views/reference_plan.svg".to_string(),
                available: true,
            },
        ],
        scenarios: Vec::new(),
        layers: Vec::new(),
        object_catalogs: Vec::new(),
        analysis_outputs: Vec::new(),
    }
}
