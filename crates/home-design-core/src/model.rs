use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;
use std::fmt;
use std::fs;
use std::path::Path;

#[derive(Debug)]
pub enum ModelLoadError {
    Io(std::io::Error),
    Json(serde_json::Error),
}

impl fmt::Display for ModelLoadError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(error) => write!(formatter, "could not read model: {error}"),
            Self::Json(error) => write!(formatter, "could not parse model JSON: {error}"),
        }
    }
}

impl std::error::Error for ModelLoadError {}

impl From<std::io::Error> for ModelLoadError {
    fn from(error: std::io::Error) -> Self {
        Self::Io(error)
    }
}

impl From<serde_json::Error> for ModelLoadError {
    fn from(error: serde_json::Error) -> Self {
        Self::Json(error)
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct HouseModel {
    pub units: String,
    #[serde(default)]
    pub assumptions: Assumptions,
    #[serde(default)]
    pub anchors: Vec<Anchor>,
    #[serde(default)]
    pub rooms: Vec<Room>,
    #[serde(default)]
    pub photo_evidence: PhotoEvidence,
    #[serde(default)]
    pub current_structure: CurrentStructure,
    #[serde(default)]
    pub current_site: CurrentSite,
    #[serde(default)]
    pub daylight: Daylight,
}

impl HouseModel {
    pub fn from_json_str(json: &str) -> Result<Self, ModelLoadError> {
        Ok(serde_json::from_str(json)?)
    }

    pub fn room(&self, room_id: &str) -> Option<&Room> {
        self.rooms.iter().find(|room| room.id == room_id)
    }

    pub fn anchor_value_m(&self, anchor_id: &str) -> Option<f64> {
        self.anchors
            .iter()
            .find(|anchor| anchor.id == anchor_id)
            .map(|anchor| anchor.value_m)
    }

    pub fn photo_check_ids(&self) -> Vec<&str> {
        self.photo_evidence
            .checks
            .iter()
            .map(|check| check.id.as_str())
            .collect()
    }
}

pub fn load_house_model_from_path(path: impl AsRef<Path>) -> Result<HouseModel, ModelLoadError> {
    HouseModel::from_json_str(&fs::read_to_string(path)?)
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct HouseModelSummary {
    pub units: String,
    pub room_count: usize,
    pub current_space_count: usize,
    pub current_built_in_count: usize,
    pub current_feature_count: usize,
    pub site_element_count: usize,
    pub shadow_source_count: usize,
}

pub fn summarize_house_model(model: &HouseModel) -> HouseModelSummary {
    HouseModelSummary {
        units: model.units.clone(),
        room_count: model.rooms.len(),
        current_space_count: model.current_structure.spaces.len(),
        current_built_in_count: model.current_structure.built_ins.len(),
        current_feature_count: model.current_structure.features.len(),
        site_element_count: model.current_site.elements.len(),
        shadow_source_count: model.current_site.shadow_sources.len(),
    }
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Assumptions {
    #[serde(default)]
    pub exterior_wall_thickness_m: Option<f64>,
    #[serde(default)]
    pub internal_wall_thickness_m: Option<f64>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Anchor {
    pub id: String,
    pub value_m: f64,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Room {
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub category: String,
    #[serde(default)]
    pub dimensions_m: BTreeMap<String, Option<f64>>,
    #[serde(default)]
    pub confidence: String,
    #[serde(default)]
    pub notes: Vec<String>,
    #[serde(default)]
    pub layout: Value,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct PhotoEvidence {
    #[serde(default)]
    pub checks: Vec<PhotoEvidenceCheck>,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct PhotoEvidenceCheck {
    pub id: String,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct CurrentStructure {
    #[serde(default)]
    pub status: String,
    #[serde(default)]
    pub spaces: Vec<ModeledItem>,
    #[serde(default)]
    pub built_ins: Vec<ModeledItem>,
    #[serde(default)]
    pub features: Vec<ModeledItem>,
}

impl CurrentStructure {
    pub fn item(&self, collection: &str, item_id: &str) -> Option<&ModeledItem> {
        let items = match collection {
            "spaces" => &self.spaces,
            "built_ins" => &self.built_ins,
            "features" => &self.features,
            _ => return None,
        };
        items.iter().find(|item| item.id == item_id)
    }

    pub fn item_ids(&self) -> impl Iterator<Item = &str> {
        self.spaces
            .iter()
            .chain(self.built_ins.iter())
            .chain(self.features.iter())
            .map(|item| item.id.as_str())
    }
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct CurrentSite {
    #[serde(default)]
    pub status: String,
    #[serde(default)]
    pub elements: Vec<ModeledItem>,
    #[serde(default)]
    pub shadow_sources: Vec<ModeledItem>,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct ModeledItem {
    pub id: String,
    #[serde(default)]
    pub display_px: Option<Value>,
    #[serde(default)]
    pub evidence_check_ids: Vec<String>,
    #[serde(flatten)]
    pub extra: BTreeMap<String, Value>,
}

impl ModeledItem {
    pub fn display_geometry_kind(&self) -> Option<GeometryKind> {
        self.display_px
            .as_ref()
            .and_then(|geometry| geometry.get("type"))
            .and_then(Value::as_str)
            .and_then(GeometryKind::from_str)
    }

    pub fn string_list(&self, field: &str) -> Option<Vec<String>> {
        let values = self.extra.get(field)?.as_array()?;
        let strings = values
            .iter()
            .map(Value::as_str)
            .collect::<Option<Vec<_>>>()?;
        Some(strings.into_iter().map(str::to_string).collect())
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum GeometryKind {
    Rect,
    Polygon,
    MultiPolygon,
}

impl GeometryKind {
    fn from_str(value: &str) -> Option<Self> {
        match value {
            "rect" => Some(Self::Rect),
            "polygon" => Some(Self::Polygon),
            "multi_polygon" => Some(Self::MultiPolygon),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Daylight {
    #[serde(default)]
    pub rooms: BTreeMap<String, Value>,
}
