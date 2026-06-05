use home_design_core::{
    FurnitureCatalog, FurnitureLayout, built_in_project_manifest, default_furniture_catalog,
    normalise_furniture_z_order, seed_current_furniture_layout, seed_furniture_layout_for_scenario,
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

fn load_saved_layout_from_path(
    path: &Path,
    project_id: &str,
    scenario_id: &str,
) -> Result<FurnitureLayout, String> {
    let raw = fs::read_to_string(path)
        .map_err(|error| format!("could not read furniture layout: {error}"))?;
    let mut layout: FurnitureLayout = serde_json::from_str(&raw)
        .map_err(|error| format!("could not parse furniture layout: {error}"))?;
    if layout.project_id != project_id || layout.scenario_id != scenario_id {
        return Err(format!(
            "furniture layout path mismatch: expected {project_id}/{scenario_id}, found {}/{}",
            layout.project_id, layout.scenario_id
        ));
    }
    normalise_furniture_z_order(&mut layout);
    let validation = validate_furniture_layout(&layout);
    if !validation.ok() {
        return Err(format!(
            "invalid furniture layout: {}",
            validation.errors.join("; ")
        ));
    }
    Ok(layout)
}

fn base_layout_for_missing_scenario(
    root: &Path,
    project_id: &str,
    scenario_id: &str,
) -> Result<FurnitureLayout, String> {
    if scenario_id != "current" {
        let current_path = furniture_layout_path(root, project_id, "current");
        if current_path.exists() {
            return load_saved_layout_from_path(&current_path, project_id, "current");
        }
    }

    Ok(seed_current_furniture_layout())
}

fn validate_known_layout_scope(project_id: &str, scenario_id: &str) -> Result<(), String> {
    let manifest = built_in_project_manifest();
    if project_id != manifest.id {
        return Err(format!("unknown project_id: {project_id}"));
    }
    if !manifest
        .scenarios
        .iter()
        .any(|scenario| scenario.id == scenario_id)
    {
        return Err(format!("unknown scenario_id: {scenario_id}"));
    }
    Ok(())
}

pub fn load_furniture_layout_from_root(
    root: &Path,
    project_id: &str,
    scenario_id: &str,
) -> Result<FurnitureLayoutLoadResult, String> {
    validate_known_layout_scope(project_id, scenario_id)?;

    let path = furniture_layout_path(root, project_id, scenario_id);
    if !path.exists() {
        let base_layout = base_layout_for_missing_scenario(root, project_id, scenario_id)?;
        let mut layout = seed_furniture_layout_for_scenario(scenario_id, &base_layout);
        layout.project_id = project_id.to_string();
        return Ok(FurnitureLayoutLoadResult {
            source: "seed".to_string(),
            layout,
        });
    }

    let layout = load_saved_layout_from_path(&path, project_id, scenario_id)?;
    Ok(FurnitureLayoutLoadResult {
        source: "saved".to_string(),
        layout,
    })
}

pub fn save_furniture_layout_to_root(root: &Path, layout: &FurnitureLayout) -> Result<(), String> {
    validate_known_layout_scope(&layout.project_id, &layout.scenario_id)?;

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
