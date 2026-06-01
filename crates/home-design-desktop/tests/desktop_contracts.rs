use home_design_desktop::{
    get_app_status, load_builtin_model_status, load_builtin_project, load_furniture_catalog,
    load_furniture_layout_from_root, save_furniture_layout_to_root,
};
use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

fn isolated_storage_root(test_name: &str) -> PathBuf {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("time")
        .as_nanos();
    std::env::temp_dir().join(format!("home-design-{test_name}-{nonce}"))
}

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
    assert_eq!(manifest.views.len(), 3);
    assert!(manifest.views.iter().all(|view| view.available));
    assert!(
        manifest
            .views
            .iter()
            .any(|view| view.id == "furniture-editor")
    );
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
    assert_eq!(status.summary.measurement_audit.total_count, 18);
    assert_eq!(status.summary.measurement_audit.measured_count, 15);
    assert_eq!(status.summary.measurement_audit.partly_measured_count, 1);
    assert_eq!(status.summary.measurement_audit.estimated_count, 2);
}

#[test]
fn load_furniture_layout_returns_seed_when_no_saved_file_exists() {
    let root = isolated_storage_root("seed");

    let loaded = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect("load seeded layout");

    assert_eq!(loaded.source, "seed");
    assert_eq!(loaded.layout.project_id, "current-house");
    assert!(
        loaded
            .layout
            .objects
            .iter()
            .any(|object| object.id == "lounge_sofa")
    );
}

#[test]
fn save_and_load_furniture_layout_persists_json() {
    let root = isolated_storage_root("save");
    let mut loaded = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect("load seeded layout");
    loaded.layout.objects[0].x_m += 0.5;

    save_furniture_layout_to_root(&root, &loaded.layout).expect("save layout");
    let reloaded = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect("load saved layout");

    assert_eq!(reloaded.source, "saved");
    assert_eq!(reloaded.layout.objects[0].x_m, loaded.layout.objects[0].x_m);
}

#[test]
fn load_saved_furniture_layout_migrates_legacy_missing_z_index() {
    let root = isolated_storage_root("legacy-z-index");
    let path = root.join("projects/current-house/scenarios/current/furniture-layout.json");
    fs::create_dir_all(path.parent().expect("parent")).expect("create parent");

    let layout = home_design_core::seed_current_furniture_layout();
    let mut json = serde_json::to_value(&layout).expect("layout json");
    let objects = json
        .get_mut("objects")
        .and_then(|value| value.as_array_mut())
        .expect("objects array");
    for object in objects {
        object.as_object_mut().expect("object").remove("z_index");
    }
    fs::write(&path, serde_json::to_string_pretty(&json).expect("json")).expect("write layout");

    let loaded = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect("load legacy layout");

    assert_eq!(loaded.source, "saved");
    assert_eq!(
        loaded
            .layout
            .objects
            .iter()
            .map(|object| object.z_index)
            .collect::<Vec<_>>(),
        (0..loaded.layout.objects.len() as i32).collect::<Vec<_>>()
    );
}

#[test]
fn invalid_saved_furniture_json_is_reported_without_overwriting() {
    let root = isolated_storage_root("invalid-json");
    let path = root.join("projects/current-house/scenarios/current/furniture-layout.json");
    fs::create_dir_all(path.parent().expect("parent")).expect("create parent");
    fs::write(&path, "{not json").expect("write invalid json");

    let error = load_furniture_layout_from_root(&root, "current-house", "current")
        .expect_err("invalid json should fail");

    assert!(error.contains("could not parse furniture layout"));
    assert_eq!(
        fs::read_to_string(path).expect("read invalid file"),
        "{not json"
    );
}

#[test]
fn load_furniture_catalog_returns_default_catalog() {
    let catalog = load_furniture_catalog();

    assert!(
        catalog
            .groups
            .iter()
            .any(|group| group.name == "Kitchen and built-ins")
    );
}
