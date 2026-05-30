use home_design_core::{AppStatus, ProjectManifest};
use home_design_desktop::BuiltInModelStatus;

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

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_app_status,
            load_builtin_project,
            load_builtin_model_status,
        ])
        .run(tauri::generate_context!())
        .expect("failed to run Home Design desktop app");
}
