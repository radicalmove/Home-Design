use home_design_core::{
    FurnitureCatalog, FurnitureLayout, default_furniture_catalog, seed_current_furniture_layout,
    validate_furniture_layout,
};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureLayoutLoadResult {
    pub source: String,
    pub layout: FurnitureLayout,
}

pub fn load_furniture_catalog() -> FurnitureCatalog {
    default_furniture_catalog()
}

pub fn furniture_layout_path(root: &Path, project_id: &str, scenario_id: &str) -> PathBuf {
    root.join("projects")
        .join(project_id)
        .join("scenarios")
        .join(scenario_id)
        .join("furniture-layout.json")
}

pub fn load_furniture_layout_from_root(
    root: &Path,
    project_id: &str,
    scenario_id: &str,
) -> Result<FurnitureLayoutLoadResult, String> {
    let path = furniture_layout_path(root, project_id, scenario_id);
    if !path.exists() {
        let mut layout = seed_current_furniture_layout();
        layout.project_id = project_id.to_string();
        layout.scenario_id = scenario_id.to_string();
        return Ok(FurnitureLayoutLoadResult {
            source: "seed".to_string(),
            layout,
        });
    }

    let raw = fs::read_to_string(&path)
        .map_err(|error| format!("could not read furniture layout: {error}"))?;
    let layout: FurnitureLayout = serde_json::from_str(&raw)
        .map_err(|error| format!("could not parse furniture layout: {error}"))?;
    let validation = validate_furniture_layout(&layout);
    if !validation.ok() {
        return Err(format!(
            "invalid furniture layout: {}",
            validation.errors.join("; ")
        ));
    }
    Ok(FurnitureLayoutLoadResult {
        source: "saved".to_string(),
        layout,
    })
}

pub fn save_furniture_layout_to_root(root: &Path, layout: &FurnitureLayout) -> Result<(), String> {
    let validation = validate_furniture_layout(layout);
    if !validation.ok() {
        return Err(format!(
            "invalid furniture layout: {}",
            validation.errors.join("; ")
        ));
    }
    let path = furniture_layout_path(root, &layout.project_id, &layout.scenario_id);
    let parent = path
        .parent()
        .ok_or_else(|| "invalid furniture layout path".to_string())?;
    fs::create_dir_all(parent)
        .map_err(|error| format!("could not create furniture layout directory: {error}"))?;
    let temporary_path = path.with_extension("json.tmp");
    let json = serde_json::to_string_pretty(layout)
        .map_err(|error| format!("could not serialize furniture layout: {error}"))?;
    fs::write(&temporary_path, json)
        .map_err(|error| format!("could not write furniture layout: {error}"))?;
    fs::rename(&temporary_path, &path)
        .map_err(|error| format!("could not replace furniture layout: {error}"))?;
    Ok(())
}
