use home_design_core::{AppStatus, ProjectManifest, app_status, built_in_project_manifest};

pub fn get_app_status() -> AppStatus {
    app_status()
}

pub fn load_builtin_project() -> ProjectManifest {
    built_in_project_manifest()
}
