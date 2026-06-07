use home_design_core::seed_current_furniture_layout;
use home_design_desktop::{
    get_app_status, load_builtin_model_status, load_builtin_project,
    load_design_review_data_from_root, load_furniture_catalog, load_furniture_layout_from_root,
    save_furniture_layout_to_root,
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
    assert_eq!(manifest.views.len(), 5);
    assert!(manifest.views.iter().all(|view| view.available));
    assert!(
        manifest
            .views
            .iter()
            .any(|view| view.id == "furniture-editor")
    );
    assert!(
        manifest
            .views
            .iter()
            .any(|view| view.id == "estimated-cost")
    );
}

#[test]
fn load_design_review_data_returns_model_and_current_furniture_layout() {
    let root = isolated_storage_root("design-review");

    let review = load_design_review_data_from_root(&root, "current-house", "current")
        .expect("load design review data");

    assert_eq!(review.model_source, "DATA/house_model.json");
    assert_eq!(review.house_model["units"], "metres");
    assert_eq!(review.furniture_layout.source, "seed");
    assert_eq!(review.furniture_layout.layout.project_id, "current-house");
    assert_eq!(review.furniture_layout.layout.scenario_id, "current");
    assert!(
        review
            .furniture_layout
            .layout
            .objects
            .iter()
            .any(|object| object.id == "lounge_sofa")
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
fn load_furniture_layout_returns_seed_for_known_future_scenario() {
    let root = isolated_storage_root("future-seed");

    let loaded =
        load_furniture_layout_from_root(&root, "current-house", "back-side-living-sunroom-bedroom")
            .expect("load future seeded layout");

    assert_eq!(loaded.source, "seed");
    assert_eq!(loaded.layout.project_id, "current-house");
    assert_eq!(
        loaded.layout.scenario_id,
        "back-side-living-sunroom-bedroom"
    );
    assert!(
        loaded
            .layout
            .objects
            .iter()
            .any(|object| object.id == "lounge_sofa")
    );
}

#[test]
fn future_seed_derives_from_saved_current_layout_when_available() {
    let root = isolated_storage_root("future-seed-from-current");
    let mut current = seed_current_furniture_layout();
    let mut custom_sofa = current
        .objects
        .iter()
        .find(|object| object.id == "lounge_sofa")
        .expect("seed sofa")
        .clone();
    custom_sofa.id = "custom-current-sofa".to_string();
    custom_sofa.x_m = 6.2;
    custom_sofa.y_m = 2.4;
    current.objects.push(custom_sofa);

    save_furniture_layout_to_root(&root, &current).expect("save current layout");

    let future =
        load_furniture_layout_from_root(&root, "current-house", "back-side-living-sunroom-bedroom")
            .expect("load future layout from current saved seed");

    assert_eq!(future.source, "seed");
    assert_eq!(
        future.layout.scenario_id,
        "back-side-living-sunroom-bedroom"
    );
    assert!(
        future
            .layout
            .objects
            .iter()
            .any(|object| object.id == "custom-current-sofa")
    );

    let relocated = future
        .layout
        .objects
        .iter()
        .find(|object| object.id == "custom-current-sofa")
        .expect("relocated custom sofa");
    assert!((9.4..=16.1).contains(&relocated.x_m));
    assert!((6.45..=10.6).contains(&relocated.y_m));
}

#[test]
fn load_furniture_layout_rejects_unknown_scenario_id() {
    let root = isolated_storage_root("unknown-scenario-load");

    let error = load_furniture_layout_from_root(&root, "current-house", "typo-design")
        .expect_err("unknown scenarios should fail");

    assert!(error.contains("unknown scenario_id"));
}

#[test]
fn save_furniture_layout_rejects_unknown_scenario_id() {
    let root = isolated_storage_root("unknown-scenario-save");
    let mut layout = home_design_core::seed_current_furniture_layout();
    layout.scenario_id = "typo-design".to_string();

    let error = save_furniture_layout_to_root(&root, &layout)
        .expect_err("unknown scenarios should not be saved");

    assert!(error.contains("unknown scenario_id"));
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
