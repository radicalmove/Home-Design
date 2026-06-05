use home_design_core::{
    FurnitureLayerKind, FurnitureLayout, FurnitureObject, default_furniture_catalog,
    default_plan_transform, seed_current_furniture_layout, seed_furniture_layout_for_scenario,
    validate_furniture_layout,
};
use std::collections::BTreeSet;

#[derive(Debug)]
struct ObjectFootprint<'a> {
    id: &'a str,
    x_min: f64,
    x_max: f64,
    y_min: f64,
    y_max: f64,
}

fn object_footprint(object: &FurnitureObject) -> ObjectFootprint<'_> {
    let rotation = object.rotation_deg.rem_euclid(180.0);
    let quarter_turn = (rotation - 90.0).abs() < 0.001;
    let width_span = if quarter_turn {
        object.depth_m
    } else {
        object.width_m
    };
    let depth_span = if quarter_turn {
        object.width_m
    } else {
        object.depth_m
    };

    ObjectFootprint {
        id: object.id.as_str(),
        x_min: object.x_m - width_span / 2.0,
        x_max: object.x_m + width_span / 2.0,
        y_min: object.y_m - depth_span / 2.0,
        y_max: object.y_m + depth_span / 2.0,
    }
}

fn assert_no_large_plan_overlaps(objects: &[&FurnitureObject]) {
    let footprints: Vec<_> = objects
        .iter()
        .map(|object| object_footprint(object))
        .collect();

    for (index, first) in footprints.iter().enumerate() {
        for second in footprints.iter().skip(index + 1) {
            let overlap_x = first.x_max.min(second.x_max) - first.x_min.max(second.x_min);
            let overlap_y = first.y_max.min(second.y_max) - first.y_min.max(second.y_min);

            assert!(
                overlap_x <= 0.05 || overlap_y <= 0.05,
                "{} overlaps {} by {:.2}m x {:.2}m",
                first.id,
                second.id,
                overlap_x,
                overlap_y
            );
        }
    }
}

fn sample_object(
    id: &str,
    catalog_id: &str,
    object_type: &str,
    layer: FurnitureLayerKind,
    x_m: f64,
    y_m: f64,
    width_m: f64,
    depth_m: f64,
    rotation_deg: f64,
) -> FurnitureObject {
    FurnitureObject {
        id: id.to_string(),
        catalog_id: Some(catalog_id.to_string()),
        layer,
        z_index: 0,
        object_type: object_type.to_string(),
        label: id.to_string(),
        abbreviation: None,
        x_m,
        y_m,
        width_m,
        depth_m,
        rotation_deg,
        colour: "#cccccc".to_string(),
        locked: false,
        notes: None,
        evidence: None,
        l_shape: None,
    }
}

fn representative_saved_layout_for_design_2_seed() -> FurnitureLayout {
    FurnitureLayout {
        project_id: "current-house".to_string(),
        scenario_id: "current".to_string(),
        plan_transform: default_plan_transform(),
        objects: vec![
            sample_object(
                "l_sofa-1",
                "l_sofa",
                "l_sofa",
                FurnitureLayerKind::Moveable,
                7.72,
                4.19,
                2.30,
                2.25,
                180.0,
            ),
            sample_object(
                "armchair-1",
                "armchair",
                "chair",
                FurnitureLayerKind::Moveable,
                6.27,
                3.87,
                0.67,
                0.80,
                180.0,
            ),
            sample_object(
                "coffee_table-1",
                "coffee_table",
                "table",
                FurnitureLayerKind::Moveable,
                7.29,
                3.48,
                1.10,
                0.55,
                270.0,
            ),
            sample_object(
                "bedroom2_bed",
                "single_bed",
                "bed",
                FurnitureLayerKind::Moveable,
                13.22,
                8.86,
                1.62,
                2.17,
                0.0,
            ),
            sample_object(
                "dresser_drawers-2",
                "dresser_drawers",
                "dresser_drawers",
                FurnitureLayerKind::Moveable,
                13.34,
                10.24,
                1.40,
                0.39,
                0.0,
            ),
            sample_object(
                "tv-2",
                "tv",
                "tv",
                FurnitureLayerKind::Moveable,
                13.39,
                10.26,
                1.20,
                0.20,
                0.0,
            ),
            sample_object(
                "dresser_drawers-3",
                "dresser_drawers",
                "dresser_drawers",
                FurnitureLayerKind::Moveable,
                11.75,
                7.99,
                1.19,
                0.40,
                0.0,
            ),
            sample_object(
                "partition_wall-2",
                "partition_wall",
                "partition_wall",
                FurnitureLayerKind::Fixed,
                9.76,
                8.66,
                0.55,
                0.03,
                0.0,
            ),
            sample_object(
                "partition_wall-2-copy-1",
                "partition_wall",
                "partition_wall",
                FurnitureLayerKind::Fixed,
                9.76,
                9.48,
                0.55,
                0.03,
                0.0,
            ),
            sample_object(
                "wardrobe_doors-2",
                "wardrobe_doors",
                "wardrobe_doors",
                FurnitureLayerKind::Fixed,
                10.00,
                9.07,
                0.78,
                0.06,
                270.0,
            ),
            sample_object(
                "bookcase-2",
                "bookcase",
                "bookcase",
                FurnitureLayerKind::Moveable,
                9.64,
                9.99,
                0.80,
                0.30,
                270.0,
            ),
            sample_object(
                "linen_storage-1",
                "linen_storage",
                "cabinet",
                FurnitureLayerKind::Fixed,
                15.49,
                9.17,
                0.59,
                1.03,
                90.0,
            ),
            sample_object(
                "toilet-1",
                "toilet",
                "toilet",
                FurnitureLayerKind::Fixed,
                15.69,
                10.03,
                0.42,
                0.61,
                90.0,
            ),
            sample_object(
                "base_cabinet-1",
                "base_cabinet",
                "cabinet",
                FurnitureLayerKind::Fixed,
                15.68,
                7.69,
                2.35,
                0.61,
                270.0,
            ),
            sample_object(
                "washer-1",
                "washer",
                "washer",
                FurnitureLayerKind::Moveable,
                15.65,
                7.46,
                0.60,
                0.65,
                0.0,
            ),
            sample_object(
                "dryer-1",
                "dryer",
                "dryer",
                FurnitureLayerKind::Moveable,
                15.65,
                6.84,
                0.60,
                0.65,
                0.0,
            ),
            sample_object(
                "desk-1",
                "desk",
                "desk",
                FurnitureLayerKind::Moveable,
                5.64,
                10.15,
                1.40,
                0.60,
                0.0,
            ),
            sample_object(
                "office_chair-1",
                "office_chair",
                "chair",
                FurnitureLayerKind::Moveable,
                5.59,
                9.78,
                0.41,
                0.40,
                0.0,
            ),
            sample_object(
                "bookcase-1",
                "bookcase",
                "bookcase",
                FurnitureLayerKind::Moveable,
                5.23,
                7.99,
                0.86,
                0.40,
                0.0,
            ),
            sample_object(
                "bookcase-1-copy-1",
                "bookcase",
                "bookcase",
                FurnitureLayerKind::Moveable,
                6.10,
                7.99,
                0.86,
                0.40,
                0.0,
            ),
        ],
    }
}

fn assert_fits_inside_room(
    object: &FurnitureObject,
    room: &str,
    min_x: f64,
    max_x: f64,
    min_y: f64,
    max_y: f64,
) {
    let rotation = object.rotation_deg.rem_euclid(180.0);
    let quarter_turn = (rotation - 90.0).abs() < 0.001;
    let width_span = if quarter_turn {
        object.depth_m
    } else {
        object.width_m
    };
    let depth_span = if quarter_turn {
        object.width_m
    } else {
        object.depth_m
    };

    assert!(
        object.x_m - width_span / 2.0 >= min_x && object.x_m + width_span / 2.0 <= max_x,
        "{} does not fit horizontally inside {}: x={} width_span={} allowed={}..={}",
        object.id,
        room,
        object.x_m,
        width_span,
        min_x,
        max_x
    );
    assert!(
        object.y_m - depth_span / 2.0 >= min_y && object.y_m + depth_span / 2.0 <= max_y,
        "{} does not fit vertically inside {}: y={} depth_span={} allowed={}..={}",
        object.id,
        room,
        object.y_m,
        depth_span,
        min_y,
        max_y
    );
}

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
    assert!(item_ids.contains("kitchen_sink"));
    assert!(item_ids.contains("refrigerator"));
    assert!(item_ids.contains("sofa"));
    assert!(item_ids.contains("l_sofa"));
    assert!(item_ids.contains("fireplace"));
    assert!(item_ids.contains("tv"));
    assert!(item_ids.contains("piano"));
    assert!(item_ids.contains("stool"));
    assert!(item_ids.contains("queen_bed"));
    assert!(item_ids.contains("l_desk"));
    assert!(item_ids.contains("bedside_table"));
    assert!(item_ids.contains("dresser_drawers"));
    assert!(item_ids.contains("wardrobe_doors"));
    assert!(item_ids.contains("partition_wall"));
    assert!(item_ids.contains("heat_pump"));
    assert!(item_ids.contains("custom_rectangle"));

    let lounge_items: BTreeSet<_> = catalog
        .groups
        .iter()
        .find(|group| group.id == "lounge-dining")
        .expect("lounge and dining group")
        .items
        .iter()
        .map(|item| item.id.as_str())
        .collect();
    assert!(lounge_items.contains("fireplace"));
    assert!(lounge_items.contains("tv"));
    assert!(lounge_items.contains("piano"));
    assert!(lounge_items.contains("stool"));

    let bedroom_items: BTreeSet<_> = catalog
        .groups
        .iter()
        .find(|group| group.id == "bedroom-office")
        .expect("bedroom and office group")
        .items
        .iter()
        .map(|item| item.id.as_str())
        .collect();
    assert!(bedroom_items.contains("bedside_table"));
    assert!(bedroom_items.contains("dresser_drawers"));
    assert!(bedroom_items.contains("wardrobe_doors"));

    let partition_wall = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "partition_wall")
        .expect("partition wall catalog item");
    assert_eq!(partition_wall.layer, FurnitureLayerKind::Fixed);
    assert_eq!(partition_wall.default_depth_m, 0.03);

    let heat_pump = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "heat_pump")
        .expect("heat pump catalog item");
    assert_eq!(heat_pump.layer, FurnitureLayerKind::Fixed);
    assert_eq!(heat_pump.symbol, "heat-pump");

    let fireplace = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "fireplace")
        .expect("fireplace catalog item");
    assert_eq!(fireplace.layer, FurnitureLayerKind::Fixed);
    assert_eq!(fireplace.symbol, "fireplace");

    let kitchen_sink = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "kitchen_sink")
        .expect("kitchen sink catalog item");
    assert_eq!(kitchen_sink.layer, FurnitureLayerKind::Fixed);
    assert_eq!(kitchen_sink.object_type, "sink");
    assert_eq!(kitchen_sink.symbol, "sink");

    let tv = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "tv")
        .expect("tv catalog item");
    assert_eq!(tv.layer, FurnitureLayerKind::Moveable);
    assert_eq!(tv.symbol, "tv");

    let piano = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "piano")
        .expect("piano catalog item");
    assert_eq!(piano.layer, FurnitureLayerKind::Moveable);
    assert_eq!(piano.object_type, "piano");
    assert_eq!(piano.default_width_m, 1.45);
    assert_eq!(piano.default_depth_m, 0.55);
    assert_eq!(piano.symbol, "piano");

    let stool = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "stool")
        .expect("stool catalog item");
    assert_eq!(stool.layer, FurnitureLayerKind::Moveable);
    assert_eq!(stool.object_type, "stool");
    assert_eq!(stool.default_width_m, 0.42);
    assert_eq!(stool.default_depth_m, 0.42);
    assert_eq!(stool.symbol, "stool");

    let wardrobe_doors = catalog
        .groups
        .iter()
        .flat_map(|group| group.items.iter())
        .find(|item| item.id == "wardrobe_doors")
        .expect("wardrobe doors catalog item");
    assert_eq!(wardrobe_doors.layer, FurnitureLayerKind::Fixed);
    assert_eq!(wardrobe_doors.symbol, "sliding-door");

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
fn seed_layout_assigns_sequential_furniture_z_index() {
    let layout = seed_current_furniture_layout();

    let z_indexes: Vec<_> = layout.objects.iter().map(|object| object.z_index).collect();

    assert_eq!(z_indexes.first(), Some(&0));
    assert_eq!(z_indexes.last(), Some(&((layout.objects.len() as i32) - 1)));
    assert_eq!(
        z_indexes,
        (0..layout.objects.len() as i32).collect::<Vec<_>>()
    );
}

#[test]
fn design_2_seed_relocates_reused_furniture_into_proposed_rooms() {
    let current = seed_current_furniture_layout();
    let design_2 = seed_furniture_layout_for_scenario("back-side-living-sunroom-bedroom", &current);

    assert_eq!(design_2.project_id, "current-house");
    assert_eq!(design_2.scenario_id, "back-side-living-sunroom-bedroom");
    assert_eq!(design_2.objects.len(), current.objects.len());

    let lounge_sofa = design_2
        .objects
        .iter()
        .find(|object| object.id == "lounge_sofa")
        .expect("reused lounge sofa");
    assert_fits_inside_room(lounge_sofa, "Design 2 living/dining/day room", 9.4, 16.1, 6.45, 10.6);
    assert!(
        lounge_sofa
            .notes
            .as_deref()
            .unwrap_or_default()
            .contains("Design 2")
    );

    let bedroom_bed = design_2
        .objects
        .iter()
        .find(|object| object.id == "bedroom2_bed")
        .expect("reused Bedroom 2 bed");
    assert_fits_inside_room(bedroom_bed, "Design 2 replacement bedroom", 0.6, 5.35, 1.2, 6.25);

    let dining_table = design_2
        .objects
        .iter()
        .find(|object| object.id == "dining_table")
        .expect("reused dining table");
    assert_fits_inside_room(dining_table, "Design 2 living/dining/day room", 9.4, 16.1, 6.45, 10.6);

    let laundry_washer = design_2
        .objects
        .iter()
        .find(|object| object.id == "laundry_washer")
        .expect("reused laundry washer");
    assert_fits_inside_room(laundry_washer, "Design 2 office-side service rooms", 4.75, 9.4, 7.7, 10.6);

    let office_desk = design_2
        .objects
        .iter()
        .find(|object| object.id == "office_desk")
        .expect("reused office desk");
    assert_fits_inside_room(office_desk, "Design 2 kitchen chill/reading edge", 8.8, 11.7, -0.5, 6.8);

    let kitchen_current = current
        .objects
        .iter()
        .find(|object| object.id == "kitchen_base_cabinets")
        .expect("current kitchen cabinets");
    let kitchen_design_2 = design_2
        .objects
        .iter()
        .find(|object| object.id == "kitchen_base_cabinets")
        .expect("Design 2 kitchen cabinets");
    assert_eq!(kitchen_design_2.x_m, kitchen_current.x_m);
    assert_eq!(kitchen_design_2.y_m, kitchen_current.y_m);
}

#[test]
fn design_2_seed_spreads_realistic_saved_layout_without_stacking_objects() {
    let current = representative_saved_layout_for_design_2_seed();
    let design_2 = seed_furniture_layout_for_scenario("back-side-living-sunroom-bedroom", &current);

    let by_ids = |ids: &[&str]| -> Vec<&FurnitureObject> {
        ids.iter()
            .map(|id| {
                design_2
                    .objects
                    .iter()
                    .find(|object| object.id == *id)
                    .unwrap_or_else(|| panic!("missing object {id}"))
            })
            .collect()
    };

    let living_objects = by_ids(&["l_sofa-1", "armchair-1", "coffee_table-1"]);
    for object in &living_objects {
        assert_fits_inside_room(object, "Design 2 living/dining/day room", 9.4, 16.1, 6.45, 10.6);
    }
    assert_no_large_plan_overlaps(&living_objects);

    let bedroom_objects = by_ids(&[
        "bedroom2_bed",
        "dresser_drawers-2",
        "tv-2",
        "dresser_drawers-3",
        "partition_wall-2",
        "partition_wall-2-copy-1",
        "wardrobe_doors-2",
        "bookcase-2",
    ]);
    for object in &bedroom_objects {
        assert_fits_inside_room(object, "Design 2 replacement bedroom", 0.6, 5.35, 1.2, 6.25);
    }
    assert_no_large_plan_overlaps(&bedroom_objects);

    let wet_core_objects = by_ids(&[
        "linen_storage-1",
        "toilet-1",
        "base_cabinet-1",
        "washer-1",
        "dryer-1",
    ]);
    for object in &wet_core_objects {
        assert_fits_inside_room(object, "Design 2 office-side service rooms", 4.75, 9.4, 7.7, 10.6);
    }
    assert_no_large_plan_overlaps(&wet_core_objects);

    let chill_objects = by_ids(&["desk-1", "office_chair-1", "bookcase-1", "bookcase-1-copy-1"]);
    for object in &chill_objects {
        assert_fits_inside_room(object, "Design 2 kitchen chill/reading edge", 8.8, 11.7, -0.5, 6.8);
    }
    assert_no_large_plan_overlaps(&chill_objects);
}

#[test]
fn furniture_object_deserializes_when_legacy_json_omits_z_index() {
    let json = serde_json::json!({
        "id": "legacy-chair",
        "catalog_id": "chair",
        "layer": "moveable",
        "type": "chair",
        "label": "Legacy chair",
        "abbreviation": null,
        "x_m": 1.0,
        "y_m": 2.0,
        "width_m": 0.5,
        "depth_m": 0.5,
        "rotation_deg": 0.0,
        "colour": "#ffffff",
        "locked": false,
        "notes": null,
        "evidence": null
    });

    let parsed: FurnitureObject = serde_json::from_value(json).expect("legacy object parses");

    assert_eq!(parsed.z_index, 0);
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
fn furniture_layout_validation_allows_thin_partition_wall_depth() {
    let mut layout = seed_current_furniture_layout();
    layout.objects.push(FurnitureObject {
        id: "test_partition_wall".to_string(),
        catalog_id: Some("partition_wall".to_string()),
        layer: FurnitureLayerKind::Fixed,
        z_index: 0,
        object_type: "partition_wall".to_string(),
        label: "Partition wall".to_string(),
        abbreviation: None,
        x_m: 6.0,
        y_m: 7.0,
        width_m: 1.2,
        depth_m: 0.03,
        l_shape: None,
        rotation_deg: 0.0,
        colour: "#4e555e".to_string(),
        locked: false,
        notes: None,
        evidence: None,
    });

    let result = validate_furniture_layout(&layout);

    assert!(result.ok(), "{:?}", result.errors);

    let mut non_partition_layout = seed_current_furniture_layout();
    non_partition_layout.objects[0].depth_m = 0.03;
    let non_partition_result = validate_furniture_layout(&non_partition_layout);

    assert!(
        non_partition_result
            .errors
            .iter()
            .any(|error| error.contains("depth_m must be positive"))
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
    assert!(json.contains("\"z_index\""));
    assert!(json.contains("\"l_shape\""));
    assert!(json.contains("\"main_depth_m\""));
    assert!(json.contains("\"return_width_m\""));
}
