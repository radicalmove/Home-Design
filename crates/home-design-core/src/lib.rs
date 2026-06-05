use serde::{Deserialize, Serialize};

mod furniture;
mod model;
mod validation;

pub use furniture::{
    FurnitureCatalog, FurnitureCatalogGroup, FurnitureCatalogItem, FurnitureLShapeDimensions,
    FurnitureLayerKind, FurnitureLayout, FurnitureObject, FurnitureValidationResult, PlanPoint,
    PlanTransform, default_furniture_catalog, default_plan_transform, normalise_furniture_z_order,
    seed_current_furniture_layout, seed_furniture_layout_for_scenario, validate_furniture_layout,
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
    DesignReview,
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
pub struct DesignScenarioDescriptor {
    pub id: String,
    pub label: String,
    pub short_label: String,
    pub summary: String,
    pub source_design: Option<String>,
    pub rank: usize,
    pub complete: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProjectManifest {
    pub id: String,
    pub name: String,
    pub model_version: String,
    pub model_source: String,
    pub views: Vec<ViewDescriptor>,
    pub scenarios: Vec<DesignScenarioDescriptor>,
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
                label: "2D Plan".to_string(),
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
            ViewDescriptor {
                id: "design-review".to_string(),
                label: "Design Review".to_string(),
                mode: ViewMode::DesignReview,
                asset_path: String::new(),
                available: true,
            },
        ],
        scenarios: built_in_design_scenarios(),
        layers: Vec::new(),
        object_catalogs: Vec::new(),
        analysis_outputs: Vec::new(),
    }
}

fn built_in_design_scenarios() -> Vec<DesignScenarioDescriptor> {
    vec![
        DesignScenarioDescriptor {
            id: "current".to_string(),
            label: "Design 1 - Current House".to_string(),
            short_label: "Design 1".to_string(),
            summary: "The current measured house, furniture layout, daylight review, and 3D navigation model.".to_string(),
            source_design: None,
            rank: 1,
            complete: true,
        },
        DesignScenarioDescriptor {
            id: "back-side-living-sunroom-bedroom".to_string(),
            label: "Design 2 - Back-Side Living Rebuild + Sunroom Bedroom Replacement".to_string(),
            short_label: "Design 2".to_string(),
            summary: "Bedroom 2 and the service end become the stronger living/dining/day room, while the current lounge and sunroom footprints become bedrooms.".to_string(),
            source_design: Some("current".to_string()),
            rank: 2,
            complete: false,
        },
        DesignScenarioDescriptor {
            id: "wet-core-bright-day-room".to_string(),
            label: "Design 3 - Office-Side Service Rooms + Bright Service-End Day Room".to_string(),
            short_label: "Design 3".to_string(),
            summary: "The office and bathroom side becomes separated service rooms, freeing the brighter laundry/Bedroom 2 side for useful daytime occupation.".to_string(),
            source_design: Some("current".to_string()),
            rank: 3,
            complete: false,
        },
        DesignScenarioDescriptor {
            id: "kitchen-kept-social-spine".to_string(),
            label: "Design 4 - Kitchen-Kept Social Spine Rebuild".to_string(),
            short_label: "Design 4".to_string(),
            summary: "The recently renovated kitchen stays broadly intact while circulation and social spaces are reworked around it.".to_string(),
            source_design: Some("current".to_string()),
            rank: 4,
            complete: false,
        },
        DesignScenarioDescriptor {
            id: "two-living-room-family".to_string(),
            label: "Design 5 - Two-Living-Room Family Plan".to_string(),
            short_label: "Design 5".to_string(),
            summary: "The plan separates brighter shared daytime space from a quieter secondary media or retreat room for family flexibility.".to_string(),
            source_design: Some("current".to_string()),
            rank: 5,
            complete: false,
        },
        DesignScenarioDescriptor {
            id: "new-bedroom-pod-bedroom2-lounge".to_string(),
            label: "Design 6 - New Bedroom Pod + Bedroom 2 Lounge".to_string(),
            short_label: "Design 6".to_string(),
            summary: "A modest new bedroom pod allows Bedroom 2 to become a better-lit lounge/day room without heavily changing the kitchen.".to_string(),
            source_design: Some("current".to_string()),
            rank: 6,
            complete: false,
        },
    ]
}
