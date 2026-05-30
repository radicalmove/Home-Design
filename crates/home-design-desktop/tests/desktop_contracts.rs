use home_design_desktop::{get_app_status, load_builtin_model_status, load_builtin_project};

#[test]
fn desktop_status_delegates_to_core_contract() {
    let status = get_app_status();

    assert_eq!(status.app_name, "Home Design");
    assert_eq!(status.runtime, "tauri-desktop");
    assert_eq!(status.built_in_project_count, 1);
}

#[test]
fn load_builtin_project_returns_packaged_view_manifest() {
    let manifest = load_builtin_project();

    assert_eq!(manifest.id, "current-house");
    assert_eq!(manifest.views.len(), 2);
    assert!(manifest.views.iter().all(|view| view.available));
}

#[test]
fn load_builtin_model_status_validates_packaged_house_model() {
    let status = load_builtin_model_status().expect("load built-in model status");

    assert_eq!(status.source_path, "DATA/house_model.json");
    assert!(status.valid);
    assert_eq!(status.validation_error_count, 0);
    assert_eq!(status.validation_warning_count, 0);
    assert_eq!(status.summary.units, "metres");
    assert_eq!(status.summary.room_count, 11);
    assert_eq!(status.summary.current_feature_count, 30);
}
