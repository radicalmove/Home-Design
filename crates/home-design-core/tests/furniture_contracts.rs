use home_design_core::{
    FurnitureLayerKind, default_furniture_catalog, seed_current_furniture_layout,
    validate_furniture_layout,
};
use std::collections::BTreeSet;

#[test]
fn default_catalog_groups_current_house_first_objects() {
    let catalog = default_furniture_catalog();

    let group_names: BTreeSet<_> = catalog
        .groups
        .iter()
        .map(|group| group.name.as_str())
        .collect();
    assert!(group_names.contains("Kitchen and built-ins"));
    assert!(group_names.contains("Bathroom and laundry"));
    assert!(group_names.contains("Lounge and dining"));
    assert!(group_names.contains("Bedroom and office"));
    assert!(group_names.contains("Custom objects"));

    let item_ids: BTreeSet<_> = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter().map(|item| item.id.as_str()))
        .collect();
    assert!(item_ids.contains("base_cabinet"));
    assert!(item_ids.contains("refrigerator"));
    assert!(item_ids.contains("sofa"));
    assert!(item_ids.contains("queen_bed"));
    assert!(item_ids.contains("custom_rectangle"));
}

#[test]
fn seed_layout_contains_fixed_and_moveable_current_house_objects() {
    let layout = seed_current_furniture_layout();

    assert_eq!(layout.project_id, "current-house");
    assert_eq!(layout.scenario_id, "current");
    assert_eq!(layout.plan_transform.units, "metres");
    assert!(
        layout
            .objects
            .iter()
            .any(|object| object.layer == FurnitureLayerKind::Fixed)
    );
    assert!(
        layout
            .objects
            .iter()
            .any(|object| object.layer == FurnitureLayerKind::Moveable)
    );
    assert!(
        layout
            .objects
            .iter()
            .any(|object| object.id == "master_bedroom_wardrobe")
    );
    assert!(
        layout
            .objects
            .iter()
            .any(|object| object.id == "lounge_sofa")
    );
    assert!(
        layout
            .objects
            .iter()
            .any(|object| object.id == "office_desk")
    );
}

#[test]
fn furniture_layout_validation_rejects_duplicate_ids_and_invalid_dimensions() {
    let mut layout = seed_current_furniture_layout();
    let duplicate = layout.objects[0].clone();
    layout.objects.push(duplicate);
    layout.objects[0].width_m = 0.0;
    layout.objects[1].colour = "not-a-colour".to_string();

    let result = validate_furniture_layout(&layout);

    assert!(!result.ok());
    assert!(
        result
            .errors
            .iter()
            .any(|error| error.contains("duplicate furniture object id"))
    );
    assert!(
        result
            .errors
            .iter()
            .any(|error| error.contains("width_m must be positive"))
    );
    assert!(
        result
            .errors
            .iter()
            .any(|error| error.contains("colour must be a hex colour"))
    );
}

#[test]
fn furniture_layout_round_trips_json_in_metres() {
    let layout = seed_current_furniture_layout();

    let json = serde_json::to_string_pretty(&layout).expect("serialize layout");
    let parsed: home_design_core::FurnitureLayout =
        serde_json::from_str(&json).expect("deserialize layout");

    assert_eq!(parsed, layout);
    assert!(json.contains("\"width_m\""));
    assert!(json.contains("\"depth_m\""));
}
