use home_design_core::{
    GeometryKind, HouseModel, load_house_model_from_path, summarize_house_model,
    validate_house_model,
};
use std::path::PathBuf;

fn model_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../DATA/house_model.json")
}

#[test]
fn rust_model_loader_reads_current_house_model_contract() {
    let model = load_house_model_from_path(model_path()).expect("load house model");

    assert_eq!(model.units, "metres");
    assert_eq!(model.rooms.len(), 11);
    assert_eq!(model.current_structure.status, "active_source_of_truth");
    assert_eq!(model.current_structure.spaces.len(), 11);
    assert_eq!(model.current_structure.built_ins.len(), 1);
    assert_eq!(model.current_structure.features.len(), 30);
    assert_eq!(model.current_site.status, "active_site_source_of_truth");
    assert_eq!(model.current_site.elements.len(), 11);
    assert_eq!(model.current_site.shadow_sources.len(), 3);

    let kitchen = model.room("kitchen_dining").expect("kitchen/dining");
    assert_eq!(kitchen.name, "Kitchen / Dining");
    assert_eq!(
        kitchen.dimensions_m.get("length").copied().flatten(),
        Some(8.12)
    );
    assert_eq!(
        kitchen.dimensions_m.get("height").copied().flatten(),
        Some(2.4)
    );

    assert_eq!(
        model.anchor_value_m("long_side_master_to_laundry"),
        Some(16.1)
    );
    assert_eq!(model.anchor_value_m("combined_external_depth"), Some(11.58));
}

#[test]
fn rust_model_loader_preserves_display_geometry_and_evidence_links() {
    let model = load_house_model_from_path(model_path()).expect("load house model");

    let sunroom = model
        .current_structure
        .item("spaces", "sunroom")
        .expect("sunroom current-structure space");
    assert_eq!(sunroom.display_geometry_kind(), Some(GeometryKind::Polygon));
    assert_eq!(
        sunroom.evidence_check_ids,
        vec!["sunroom_wraparound_glazing"]
    );

    let slider = model
        .current_structure
        .item("features", "sunroom_lounge_slider")
        .expect("sunroom lounge slider feature");
    assert_eq!(slider.display_geometry_kind(), Some(GeometryKind::Polygon));
    assert_eq!(slider.evidence_check_ids, vec!["sunroom_lounge_slider"]);
    assert_eq!(
        slider.string_list("between"),
        Some(vec!["sunroom".to_string(), "lounge".to_string()])
    );
}

#[test]
fn rust_model_validation_matches_python_current_model_expectations() {
    let model = load_house_model_from_path(model_path()).expect("load house model");

    let result = validate_house_model(&model);

    assert!(result.ok(), "{:?}", result.errors);
    assert!(result.errors.is_empty());
    assert!(result.warnings.is_empty());
}

#[test]
fn rust_model_validation_reports_core_contract_failures() {
    let mut model = load_house_model_from_path(model_path()).expect("load house model");

    model.units = "feet".to_string();
    model.assumptions.internal_wall_thickness_m = Some(0.12);
    model.rooms[0].dimensions_m.remove("height");
    model.rooms[0].layout = serde_json::Value::Null;
    model.current_structure.features[0]
        .evidence_check_ids
        .push("missing_photo_check".to_string());
    model.daylight.rooms.remove("kitchen_dining");

    let result = validate_house_model(&model);

    assert!(!result.ok());
    assert!(result.errors.contains(&"units must be metres".to_string()));
    assert!(
        result
            .errors
            .contains(&"internal wall thickness must be 0.14m".to_string())
    );
    assert!(
        result
            .errors
            .contains(&"missing ceiling height for kitchen_dining".to_string())
    );
    assert!(
        result
            .errors
            .contains(&"missing layout for kitchen_dining".to_string())
    );
    assert!(
        result.errors.iter().any(|error| error
            == "current_structure.features.sunroom_lounge_slider references unknown evidence check: missing_photo_check")
    );
    assert!(
        result
            .errors
            .contains(&"missing daylight matrix for kitchen_dining".to_string())
    );
}

#[test]
fn rust_model_can_parse_from_json_string_for_future_commands() {
    let raw = std::fs::read_to_string(model_path()).expect("read model json");

    let model = HouseModel::from_json_str(&raw).expect("parse model json string");

    assert_eq!(model.units, "metres");
    assert_eq!(model.room("sunroom").expect("sunroom").category, "living");
}

#[test]
fn rust_model_summary_reports_counts_for_desktop_status() {
    let model = load_house_model_from_path(model_path()).expect("load house model");

    let summary = summarize_house_model(&model);

    assert_eq!(summary.units, "metres");
    assert_eq!(summary.room_count, 11);
    assert_eq!(summary.current_space_count, 11);
    assert_eq!(summary.current_built_in_count, 1);
    assert_eq!(summary.current_feature_count, 30);
    assert_eq!(summary.site_element_count, 11);
    assert_eq!(summary.shadow_source_count, 3);
}
