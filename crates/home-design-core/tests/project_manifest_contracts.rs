use home_design_core::{ViewMode, built_in_project_manifest};

#[test]
fn built_in_project_manifest_exposes_current_house_views() {
    let manifest = built_in_project_manifest();

    assert_eq!(manifest.id, "current-house");
    assert_eq!(manifest.name, "Current House");
    assert_eq!(manifest.model_source, "DATA/house_model.json");
    assert_eq!(manifest.views.len(), 4);

    let base_view = manifest
        .views
        .iter()
        .find(|view| view.id == "base-view")
        .expect("base view");
    assert_eq!(base_view.label, "2D Plan");
    assert_eq!(base_view.mode, ViewMode::BasePlan);
    assert_eq!(base_view.asset_path, "/views/reference_plan.html");
    assert!(base_view.available);

    let three_d_view = manifest
        .views
        .iter()
        .find(|view| view.id == "three-d-navigation")
        .expect("3D navigation view");
    assert_eq!(three_d_view.label, "3D Navigation");
    assert_eq!(three_d_view.mode, ViewMode::ThreeDNavigation);
    assert_eq!(three_d_view.asset_path, "/views/house_3d.html");
    assert!(three_d_view.available);

    let furniture_view = manifest
        .views
        .iter()
        .find(|view| view.id == "furniture-editor")
        .expect("furniture editor view");
    assert_eq!(furniture_view.label, "Furniture Editor");
    assert_eq!(furniture_view.mode, ViewMode::FurnitureEditor);
    assert_eq!(furniture_view.asset_path, "/views/reference_plan.svg");
    assert!(furniture_view.available);

    let design_review_view = manifest
        .views
        .iter()
        .find(|view| view.id == "design-review")
        .expect("design review view");
    assert_eq!(design_review_view.label, "Design Review");
    assert_eq!(design_review_view.mode, ViewMode::DesignReview);
    assert_eq!(design_review_view.asset_path, "");
    assert!(design_review_view.available);

    let scenario_ids: Vec<_> = manifest
        .scenarios
        .iter()
        .map(|scenario| scenario.id.as_str())
        .collect();
    assert_eq!(
        scenario_ids,
        vec![
            "current",
            "back-side-living-sunroom-bedroom",
            "wet-core-bright-day-room",
            "kitchen-kept-social-spine",
            "two-living-room-family",
            "new-bedroom-pod-bedroom2-lounge",
        ],
    );

    let current_design = manifest
        .scenarios
        .iter()
        .find(|scenario| scenario.id == "current")
        .expect("current design scenario");
    assert_eq!(current_design.label, "Design 1 - Current House");
    assert_eq!(current_design.short_label, "Design 1");
    assert_eq!(current_design.source_design, None);
    assert_eq!(current_design.rank, 1);
    assert!(current_design.complete);

    for scenario in manifest
        .scenarios
        .iter()
        .filter(|scenario| scenario.id != "current")
    {
        assert_eq!(scenario.source_design.as_deref(), Some("current"));
        assert!(!scenario.complete);
    }

    assert!(manifest.layers.is_empty());
    assert!(manifest.object_catalogs.is_empty());
    assert!(manifest.analysis_outputs.is_empty());
}

#[test]
fn app_status_reports_single_builtin_project() {
    let status = home_design_core::app_status();

    assert_eq!(status.app_name, "Home Design");
    assert_eq!(status.built_in_project_count, 1);
    assert_eq!(status.runtime, "tauri-desktop");
}
