use home_design_core::{AppStatus, FurnitureCatalog, FurnitureLayout, ProjectManifest};
use home_design_desktop::{BuiltInModelStatus, FurnitureLayoutLoadResult};
use tauri::Manager;

#[tauri::command]
fn get_app_status() -> AppStatus {
    home_design_desktop::get_app_status()
}

#[tauri::command]
fn load_builtin_project() -> ProjectManifest {
    home_design_desktop::load_builtin_project()
}

#[tauri::command]
fn load_builtin_model_status() -> Result<BuiltInModelStatus, String> {
    home_design_desktop::load_builtin_model_status()
}

fn app_data_root(app: &tauri::AppHandle) -> Result<std::path::PathBuf, String> {
    app.path()
        .app_data_dir()
        .map_err(|error| format!("could not resolve app data directory: {error}"))
}

#[tauri::command]
fn load_furniture_catalog() -> FurnitureCatalog {
    home_design_desktop::load_furniture_catalog()
}

#[tauri::command]
fn load_furniture_layout(
    app: tauri::AppHandle,
    project_id: String,
    scenario_id: String,
) -> Result<FurnitureLayoutLoadResult, String> {
    let root = app_data_root(&app)?;
    home_design_desktop::load_furniture_layout_from_root(&root, &project_id, &scenario_id)
}

#[tauri::command]
fn save_furniture_layout(app: tauri::AppHandle, layout: FurnitureLayout) -> Result<(), String> {
    let root = app_data_root(&app)?;
    home_design_desktop::save_furniture_layout_to_root(&root, &layout)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_app_status,
            load_builtin_project,
            load_builtin_model_status,
            load_furniture_catalog,
            load_furniture_layout,
            save_furniture_layout,
        ])
        .run(tauri::generate_context!())
        .expect("failed to run Home Design desktop app");
}
