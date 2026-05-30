use home_design_desktop::{get_app_status, load_builtin_project};

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
