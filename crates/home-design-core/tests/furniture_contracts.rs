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
    assert!(item_ids.contains("l_sofa"));
    assert!(item_ids.contains("queen_bed"));
    assert!(item_ids.contains("l_desk"));
    assert!(item_ids.contains("custom_rectangle"));

    let l_sofa = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "l_sofa")
        .expect("l-shaped sofa catalog item");
    assert_eq!(l_sofa.symbol, "l-shape");
    assert!(l_sofa.default_l_shape.is_some());

    let l_desk = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "l_desk")
        .expect("l-shaped desk catalog item");
    assert_eq!(l_desk.symbol, "l-shape");
    assert!(l_desk.default_l_shape.is_some());
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
            .any(|object| object.id == "lounge_sofa" && object.l_shape.is_some())
    );
    assert!(
        layout
            .objects
            .iter()
            .any(|object| object.id == "office_desk")
    );
    assert!(
        layout
            .objects
            .iter()
            .any(|object| object.id == "office_desk" && object.l_shape.is_some())
    );
}

#[test]
fn furniture_layout_validation_rejects_duplicate_ids_and_invalid_dimensions() {
    let mut layout = seed_current_furniture_layout();
    let duplicate = layout.objects[0].clone();
    layout.objects.push(duplicate);
    layout.objects[0].width_m = 0.0;
    layout.objects[1].colour = "not-a-colour".to_string();
    layout.objects[2].l_shape = Some(home_design_core::FurnitureLShapeDimensions {
        main_depth_m: 10.0,
        return_width_m: 0.75,
    });

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
    assert!(
        result
            .errors
            .iter()
            .any(|error| error.contains("l_shape.main_depth_m must fit within depth_m"))
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
    assert!(json.contains("\"l_shape\""));
    assert!(json.contains("\"main_depth_m\""));
    assert!(json.contains("\"return_width_m\""));
}
