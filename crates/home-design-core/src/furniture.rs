use serde::{Deserialize, Serialize};
use std::collections::HashSet;

const MIN_FURNITURE_DIMENSION_M: f64 = 0.05;
const PARTITION_WALL_TYPE: &str = "partition_wall";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FurnitureLayerKind {
    Fixed,
    Moveable,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureLShapeDimensions {
    pub main_depth_m: f64,
    pub return_width_m: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PlanPoint {
    pub x: f64,
    pub y: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PlanTransform {
    pub units: String,
    pub svg_width_px: f64,
    pub svg_height_px: f64,
    pub origin_svg_px: PlanPoint,
    pub px_per_m: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureObject {
    pub id: String,
    pub catalog_id: Option<String>,
    pub layer: FurnitureLayerKind,
    #[serde(default)]
    pub z_index: i32,
    #[serde(rename = "type")]
    pub object_type: String,
    pub label: String,
    pub abbreviation: Option<String>,
    pub x_m: f64,
    pub y_m: f64,
    pub width_m: f64,
    pub depth_m: f64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub l_shape: Option<FurnitureLShapeDimensions>,
    pub rotation_deg: f64,
    pub colour: String,
    pub locked: bool,
    pub notes: Option<String>,
    pub evidence: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureLayout {
    pub project_id: String,
    pub scenario_id: String,
    pub plan_transform: PlanTransform,
    pub objects: Vec<FurnitureObject>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureCatalog {
    pub groups: Vec<FurnitureCatalogGroup>,
}

fn is_partition_wall_object(object: &FurnitureObject) -> bool {
    object.object_type == PARTITION_WALL_TYPE
        || object.catalog_id.as_deref() == Some(PARTITION_WALL_TYPE)
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureCatalogGroup {
    pub id: String,
    pub name: String,
    pub items: Vec<FurnitureCatalogItem>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FurnitureCatalogItem {
    pub id: String,
    pub label: String,
    pub layer: FurnitureLayerKind,
    #[serde(rename = "type")]
    pub object_type: String,
    pub abbreviation: Option<String>,
    pub default_width_m: f64,
    pub default_depth_m: f64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub default_l_shape: Option<FurnitureLShapeDimensions>,
    pub colour: String,
    pub symbol: String,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct FurnitureValidationResult {
    pub errors: Vec<String>,
}

impl FurnitureValidationResult {
    pub fn ok(&self) -> bool {
        self.errors.is_empty()
    }
}

pub fn default_plan_transform() -> PlanTransform {
    PlanTransform {
        units: "metres".to_string(),
        svg_width_px: 1600.0,
        svg_height_px: 900.0,
        origin_svg_px: PlanPoint { x: 518.0, y: 314.0 },
        px_per_m: 27.16,
    }
}

pub fn default_furniture_catalog() -> FurnitureCatalog {
    FurnitureCatalog {
        groups: vec![
            FurnitureCatalogGroup {
                id: "kitchen-built-ins".to_string(),
                name: "Kitchen and built-ins".to_string(),
                items: vec![
                    catalog_item(
                        "base_cabinet",
                        "Base cabinet",
                        FurnitureLayerKind::Fixed,
                        "cabinet",
                        Some("CAB"),
                        1.2,
                        0.6,
                        "#315f8c",
                        "storage",
                    ),
                    catalog_item(
                        "tall_cabinet",
                        "Tall cabinet",
                        FurnitureLayerKind::Fixed,
                        "cabinet",
                        Some("CAB"),
                        0.8,
                        0.6,
                        "#315f8c",
                        "storage",
                    ),
                    catalog_item(
                        "overhead_cabinet",
                        "Overhead cabinet",
                        FurnitureLayerKind::Fixed,
                        "cabinet",
                        Some("OH"),
                        1.2,
                        0.35,
                        "#4c789d",
                        "storage",
                    ),
                    catalog_item(
                        "pantry",
                        "Pantry",
                        FurnitureLayerKind::Fixed,
                        "pantry",
                        Some("P"),
                        0.9,
                        0.6,
                        "#315f8c",
                        "storage",
                    ),
                    catalog_item(
                        "counter",
                        "Bench / counter",
                        FurnitureLayerKind::Fixed,
                        "counter",
                        Some("CNTR"),
                        1.8,
                        0.65,
                        "#315f8c",
                        "storage",
                    ),
                    catalog_item(
                        "island",
                        "Island",
                        FurnitureLayerKind::Fixed,
                        "island",
                        None,
                        1.8,
                        0.9,
                        "#7d8f80",
                        "table",
                    ),
                    catalog_item(
                        "refrigerator",
                        "Refrigerator",
                        FurnitureLayerKind::Fixed,
                        "refrigerator",
                        Some("REF"),
                        0.9,
                        0.75,
                        "#f7f8f6",
                        "appliance",
                    ),
                    catalog_item(
                        "dishwasher",
                        "Dishwasher",
                        FurnitureLayerKind::Fixed,
                        "dishwasher",
                        Some("D/W"),
                        0.6,
                        0.6,
                        "#f7f8f6",
                        "appliance",
                    ),
                    catalog_item(
                        "oven_cooktop",
                        "Oven / cooktop",
                        FurnitureLayerKind::Fixed,
                        "appliance",
                        Some("OV"),
                        0.7,
                        0.6,
                        "#f7f8f6",
                        "appliance",
                    ),
                ],
            },
            FurnitureCatalogGroup {
                id: "bathroom-laundry".to_string(),
                name: "Bathroom and laundry".to_string(),
                items: vec![
                    catalog_item(
                        "toilet",
                        "Toilet",
                        FurnitureLayerKind::Fixed,
                        "toilet",
                        Some("TLT"),
                        0.7,
                        0.9,
                        "#f7f8f6",
                        "fixture",
                    ),
                    catalog_item(
                        "shower",
                        "Shower",
                        FurnitureLayerKind::Fixed,
                        "shower",
                        Some("SHWR"),
                        0.9,
                        0.9,
                        "#eef1f0",
                        "fixture",
                    ),
                    catalog_item(
                        "bath",
                        "Bath",
                        FurnitureLayerKind::Fixed,
                        "bath",
                        None,
                        1.7,
                        0.75,
                        "#eef1f0",
                        "fixture",
                    ),
                    catalog_item(
                        "vanity",
                        "Vanity / lavatory",
                        FurnitureLayerKind::Fixed,
                        "vanity",
                        Some("LAV"),
                        0.9,
                        0.5,
                        "#eef1f0",
                        "fixture",
                    ),
                    catalog_item(
                        "washer",
                        "Washer",
                        FurnitureLayerKind::Fixed,
                        "washer",
                        Some("W"),
                        0.6,
                        0.65,
                        "#f7f8f6",
                        "appliance",
                    ),
                    catalog_item(
                        "dryer",
                        "Dryer",
                        FurnitureLayerKind::Fixed,
                        "dryer",
                        Some("D"),
                        0.6,
                        0.65,
                        "#f7f8f6",
                        "appliance",
                    ),
                    catalog_item(
                        "linen_storage",
                        "Linen storage",
                        FurnitureLayerKind::Fixed,
                        "cabinet",
                        Some("LIN"),
                        0.8,
                        0.45,
                        "#d6a05f",
                        "storage",
                    ),
                ],
            },
            FurnitureCatalogGroup {
                id: "lounge-dining".to_string(),
                name: "Lounge and dining".to_string(),
                items: vec![
                    catalog_item(
                        "sofa",
                        "Sofa",
                        FurnitureLayerKind::Moveable,
                        "sofa",
                        None,
                        2.2,
                        0.95,
                        "#33312e",
                        "sofa",
                    ),
                    catalog_l_shape_item(
                        "l_sofa",
                        "L-shaped sofa",
                        FurnitureLayerKind::Moveable,
                        "l_sofa",
                        None,
                        2.8,
                        1.85,
                        0.9,
                        1.05,
                        "#33312e",
                    ),
                    catalog_item(
                        "fireplace",
                        "Fireplace",
                        FurnitureLayerKind::Fixed,
                        "fireplace",
                        Some("FP"),
                        1.1,
                        0.35,
                        "#5a4a3d",
                        "fireplace",
                    ),
                    catalog_item(
                        "armchair",
                        "Armchair",
                        FurnitureLayerKind::Moveable,
                        "chair",
                        None,
                        0.85,
                        0.85,
                        "#596f49",
                        "chair",
                    ),
                    catalog_item(
                        "coffee_table",
                        "Coffee table",
                        FurnitureLayerKind::Moveable,
                        "table",
                        None,
                        1.1,
                        0.6,
                        "#ffffff",
                        "table",
                    ),
                    catalog_item(
                        "tv_unit",
                        "TV / media unit",
                        FurnitureLayerKind::Moveable,
                        "cabinet",
                        None,
                        1.8,
                        0.4,
                        "#24282c",
                        "storage",
                    ),
                    catalog_item(
                        "tv",
                        "TV",
                        FurnitureLayerKind::Moveable,
                        "tv",
                        None,
                        1.2,
                        0.08,
                        "#24282c",
                        "tv",
                    ),
                    catalog_item(
                        "dining_table",
                        "Dining table",
                        FurnitureLayerKind::Moveable,
                        "table",
                        None,
                        1.8,
                        0.9,
                        "#ffffff",
                        "table",
                    ),
                    catalog_item(
                        "dining_chair",
                        "Dining chair",
                        FurnitureLayerKind::Moveable,
                        "chair",
                        None,
                        0.45,
                        0.45,
                        "#ffffff",
                        "chair",
                    ),
                    catalog_item(
                        "sideboard",
                        "Sideboard",
                        FurnitureLayerKind::Moveable,
                        "cabinet",
                        None,
                        1.5,
                        0.45,
                        "#d6a05f",
                        "storage",
                    ),
                ],
            },
            FurnitureCatalogGroup {
                id: "bedroom-office".to_string(),
                name: "Bedroom and office".to_string(),
                items: vec![
                    catalog_item(
                        "single_bed",
                        "Single bed",
                        FurnitureLayerKind::Moveable,
                        "bed",
                        None,
                        1.9,
                        0.9,
                        "#ffffff",
                        "bed",
                    ),
                    catalog_item(
                        "queen_bed",
                        "Queen bed",
                        FurnitureLayerKind::Moveable,
                        "bed",
                        None,
                        2.03,
                        1.53,
                        "#ffffff",
                        "bed",
                    ),
                    catalog_item(
                        "bedside_table",
                        "Bedside table",
                        FurnitureLayerKind::Moveable,
                        "bedside_table",
                        None,
                        0.45,
                        0.45,
                        "#ffffff",
                        "bedside-table",
                    ),
                    catalog_item(
                        "dresser_drawers",
                        "Dresser drawer",
                        FurnitureLayerKind::Moveable,
                        "dresser_drawers",
                        None,
                        1.2,
                        0.5,
                        "#d6a05f",
                        "drawers",
                    ),
                    catalog_item(
                        "wardrobe",
                        "Wardrobe",
                        FurnitureLayerKind::Fixed,
                        "wardrobe",
                        Some("CL"),
                        1.6,
                        0.62,
                        "#d9c39f",
                        "storage",
                    ),
                    catalog_item(
                        "wardrobe_doors",
                        "Wardrobe doors",
                        FurnitureLayerKind::Fixed,
                        "wardrobe_doors",
                        None,
                        1.6,
                        0.06,
                        "#f7f8f6",
                        "sliding-door",
                    ),
                    catalog_item(
                        "desk",
                        "Desk",
                        FurnitureLayerKind::Moveable,
                        "desk",
                        None,
                        1.4,
                        0.7,
                        "#ffffff",
                        "desk",
                    ),
                    catalog_l_shape_item(
                        "l_desk",
                        "L-shaped desk",
                        FurnitureLayerKind::Moveable,
                        "l_desk",
                        None,
                        1.8,
                        1.6,
                        0.65,
                        0.65,
                        "#ffffff",
                    ),
                    catalog_item(
                        "office_chair",
                        "Office chair",
                        FurnitureLayerKind::Moveable,
                        "chair",
                        None,
                        0.55,
                        0.55,
                        "#33312e",
                        "chair",
                    ),
                    catalog_item(
                        "bookcase",
                        "Bookcase",
                        FurnitureLayerKind::Moveable,
                        "bookcase",
                        None,
                        0.9,
                        0.35,
                        "#d6a05f",
                        "storage",
                    ),
                ],
            },
            FurnitureCatalogGroup {
                id: "custom".to_string(),
                name: "Custom objects".to_string(),
                items: vec![
                    catalog_item(
                        "heat_pump",
                        "Heat pump",
                        FurnitureLayerKind::Fixed,
                        "heat_pump",
                        Some("HP"),
                        0.85,
                        0.22,
                        "#f7f8f6",
                        "heat-pump",
                    ),
                    catalog_item(
                        "partition_wall",
                        "Partition wall",
                        FurnitureLayerKind::Fixed,
                        "partition_wall",
                        None,
                        1.2,
                        0.03,
                        "#4e555e",
                        "partition-wall",
                    ),
                    catalog_item(
                        "custom_rectangle",
                        "Custom rectangle",
                        FurnitureLayerKind::Moveable,
                        "custom",
                        None,
                        1.2,
                        0.6,
                        "#f7f8f6",
                        "rectangle",
                    ),
                ],
            },
        ],
    }
}

pub fn seed_current_furniture_layout() -> FurnitureLayout {
    let mut layout = FurnitureLayout {
        project_id: "current-house".to_string(),
        scenario_id: "current".to_string(),
        plan_transform: default_plan_transform(),
        objects: vec![
            furniture_object(
                "master_bedroom_wardrobe",
                Some("wardrobe"),
                FurnitureLayerKind::Fixed,
                "wardrobe",
                "Master wardrobe",
                Some("CL"),
                4.38,
                7.65,
                0.62,
                2.90,
                0.0,
                "#d9c39f",
                Some("Measured built-in wardrobe bay between master bedroom and office."),
                Some("built_in:master_bedroom_wardrobe"),
            ),
            furniture_object(
                "kitchen_base_cabinets",
                Some("base_cabinet"),
                FurnitureLayerKind::Fixed,
                "cabinet",
                "Kitchen cabinets",
                Some("CAB"),
                10.7,
                3.2,
                2.8,
                0.6,
                90.0,
                "#315f8c",
                Some("Approximate fixed cabinet run seeded from kitchen/dining context."),
                Some("room:kitchen_dining"),
            ),
            furniture_object(
                "kitchen_refrigerator",
                Some("refrigerator"),
                FurnitureLayerKind::Fixed,
                "refrigerator",
                "Refrigerator",
                Some("REF"),
                10.9,
                6.1,
                0.9,
                0.75,
                0.0,
                "#f7f8f6",
                Some("Approximate appliance position for planning."),
                Some("room:kitchen_dining"),
            ),
            furniture_object(
                "laundry_washer",
                Some("washer"),
                FurnitureLayerKind::Fixed,
                "washer",
                "Washer",
                Some("W"),
                15.1,
                7.4,
                0.6,
                0.65,
                0.0,
                "#f7f8f6",
                Some("Approximate laundry appliance position."),
                Some("room:laundry"),
            ),
            furniture_object(
                "bathroom_vanity",
                Some("vanity"),
                FurnitureLayerKind::Fixed,
                "vanity",
                "Vanity",
                Some("LAV"),
                8.2,
                8.2,
                0.9,
                0.5,
                0.0,
                "#eef1f0",
                Some("Approximate bathroom fixture position."),
                Some("room:bathroom"),
            ),
            furniture_object(
                "bathroom_toilet",
                Some("toilet"),
                FurnitureLayerKind::Fixed,
                "toilet",
                "Toilet",
                Some("TLT"),
                8.0,
                9.4,
                0.7,
                0.9,
                0.0,
                "#f7f8f6",
                Some("Approximate bathroom/toilet fixture position."),
                Some("room:bathroom"),
            ),
            furniture_object(
                "bathroom_shower",
                Some("shower"),
                FurnitureLayerKind::Fixed,
                "shower",
                "Shower",
                Some("SHWR"),
                9.0,
                8.3,
                0.9,
                0.9,
                0.0,
                "#eef1f0",
                Some("Approximate shower position for planning."),
                Some("room:bathroom"),
            ),
            furniture_l_shape_object(
                "lounge_sofa",
                Some("l_sofa"),
                FurnitureLayerKind::Moveable,
                "l_sofa",
                "L-shaped sofa",
                None,
                5.1,
                3.6,
                2.8,
                1.85,
                0.9,
                1.05,
                0.0,
                "#33312e",
                Some("Photo-based lounge sofa seed with rear flow gap."),
                Some("scenario_editor:lounge_sofa"),
            ),
            furniture_object(
                "dining_table",
                Some("dining_table"),
                FurnitureLayerKind::Moveable,
                "table",
                "Dining table",
                None,
                8.95,
                3.1,
                1.55,
                2.5,
                0.0,
                "#ffffff",
                Some("Photo-based dining table seed."),
                Some("scenario_editor:dining_table"),
            ),
            furniture_object(
                "bedroom2_bed",
                Some("single_bed"),
                FurnitureLayerKind::Moveable,
                "bed",
                "Bedroom 2 bed",
                None,
                9.35,
                8.05,
                2.28,
                1.55,
                0.0,
                "#ffffff",
                Some("Approximate bed/daybed position from bedroom photos."),
                Some("scenario_editor:bedroom2_bed"),
            ),
            furniture_l_shape_object(
                "office_desk",
                Some("l_desk"),
                FurnitureLayerKind::Moveable,
                "l_desk",
                "L-shaped desk",
                None,
                4.05,
                9.8,
                1.75,
                1.6,
                0.65,
                0.65,
                0.0,
                "#ffffff",
                Some("Desk placed near the office window wall."),
                Some("scenario_editor:office_desk"),
            ),
            furniture_object(
                "bookcase",
                Some("bookcase"),
                FurnitureLayerKind::Moveable,
                "bookcase",
                "Bookcase",
                None,
                5.65,
                8.2,
                0.9,
                0.35,
                0.0,
                "#d6a05f",
                Some("Approximate storage object for planning."),
                Some("room:office"),
            ),
        ],
    };
    normalise_furniture_z_order(&mut layout);
    layout
}

pub fn normalise_furniture_z_order(layout: &mut FurnitureLayout) {
    if layout.objects.is_empty() {
        return;
    }

    let all_default_order = layout.objects.iter().all(|object| object.z_index == 0);
    if all_default_order {
        for (index, object) in layout.objects.iter_mut().enumerate() {
            object.z_index = index as i32;
        }
        return;
    }

    let mut ordered: Vec<(usize, i32)> = layout
        .objects
        .iter()
        .enumerate()
        .map(|(index, object)| (index, object.z_index))
        .collect();
    ordered.sort_by_key(|(index, z_index)| (*z_index, *index));

    for (new_index, (object_index, _)) in ordered.into_iter().enumerate() {
        layout.objects[object_index].z_index = new_index as i32;
    }
}

pub fn validate_furniture_layout(layout: &FurnitureLayout) -> FurnitureValidationResult {
    let mut errors = Vec::new();
    if layout.project_id.trim().is_empty() {
        errors.push("project_id is required".to_string());
    }
    if layout.scenario_id.trim().is_empty() {
        errors.push("scenario_id is required".to_string());
    }
    if layout.plan_transform.units != "metres" {
        errors.push("plan_transform.units must be metres".to_string());
    }
    validate_finite(
        "plan_transform.svg_width_px",
        layout.plan_transform.svg_width_px,
        &mut errors,
    );
    validate_finite(
        "plan_transform.svg_height_px",
        layout.plan_transform.svg_height_px,
        &mut errors,
    );
    validate_finite(
        "plan_transform.px_per_m",
        layout.plan_transform.px_per_m,
        &mut errors,
    );
    if layout.plan_transform.px_per_m <= 0.0 {
        errors.push("plan_transform.px_per_m must be positive".to_string());
    }

    let mut ids = HashSet::new();
    for object in &layout.objects {
        if object.id.trim().is_empty() {
            errors.push("furniture object id is required".to_string());
        } else if !ids.insert(object.id.as_str()) {
            errors.push(format!("duplicate furniture object id: {}", object.id));
        }
        if object.label.trim().is_empty() {
            errors.push(format!("{} label is required", object.id));
        }
        validate_finite(&format!("{}.x_m", object.id), object.x_m, &mut errors);
        validate_finite(&format!("{}.y_m", object.id), object.y_m, &mut errors);
        validate_finite(
            &format!("{}.width_m", object.id),
            object.width_m,
            &mut errors,
        );
        validate_finite(
            &format!("{}.depth_m", object.id),
            object.depth_m,
            &mut errors,
        );
        validate_finite(
            &format!("{}.rotation_deg", object.id),
            object.rotation_deg,
            &mut errors,
        );
        if object.width_m <= MIN_FURNITURE_DIMENSION_M {
            errors.push(format!("{} width_m must be positive", object.id));
        }
        if object.depth_m <= 0.0
            || (!is_partition_wall_object(object) && object.depth_m <= MIN_FURNITURE_DIMENSION_M)
        {
            errors.push(format!("{} depth_m must be positive", object.id));
        }
        if let Some(l_shape) = &object.l_shape {
            validate_finite(
                &format!("{}.l_shape.main_depth_m", object.id),
                l_shape.main_depth_m,
                &mut errors,
            );
            validate_finite(
                &format!("{}.l_shape.return_width_m", object.id),
                l_shape.return_width_m,
                &mut errors,
            );
            if l_shape.main_depth_m <= 0.05 {
                errors.push(format!(
                    "{} l_shape.main_depth_m must be positive",
                    object.id
                ));
            }
            if l_shape.return_width_m <= 0.05 {
                errors.push(format!(
                    "{} l_shape.return_width_m must be positive",
                    object.id
                ));
            }
            if l_shape.main_depth_m > object.depth_m {
                errors.push(format!(
                    "{} l_shape.main_depth_m must fit within depth_m",
                    object.id
                ));
            }
            if l_shape.return_width_m > object.width_m {
                errors.push(format!(
                    "{} l_shape.return_width_m must fit within width_m",
                    object.id
                ));
            }
        }
        if !is_hex_colour(&object.colour) {
            errors.push(format!("{} colour must be a hex colour", object.id));
        }
    }

    FurnitureValidationResult { errors }
}

fn catalog_item(
    id: &str,
    label: &str,
    layer: FurnitureLayerKind,
    object_type: &str,
    abbreviation: Option<&str>,
    default_width_m: f64,
    default_depth_m: f64,
    colour: &str,
    symbol: &str,
) -> FurnitureCatalogItem {
    FurnitureCatalogItem {
        id: id.to_string(),
        label: label.to_string(),
        layer,
        object_type: object_type.to_string(),
        abbreviation: abbreviation.map(str::to_string),
        default_width_m,
        default_depth_m,
        default_l_shape: None,
        colour: colour.to_string(),
        symbol: symbol.to_string(),
    }
}

#[allow(clippy::too_many_arguments)]
fn catalog_l_shape_item(
    id: &str,
    label: &str,
    layer: FurnitureLayerKind,
    object_type: &str,
    abbreviation: Option<&str>,
    default_width_m: f64,
    default_depth_m: f64,
    main_depth_m: f64,
    return_width_m: f64,
    colour: &str,
) -> FurnitureCatalogItem {
    FurnitureCatalogItem {
        id: id.to_string(),
        label: label.to_string(),
        layer,
        object_type: object_type.to_string(),
        abbreviation: abbreviation.map(str::to_string),
        default_width_m,
        default_depth_m,
        default_l_shape: Some(FurnitureLShapeDimensions {
            main_depth_m,
            return_width_m,
        }),
        colour: colour.to_string(),
        symbol: "l-shape".to_string(),
    }
}

#[allow(clippy::too_many_arguments)]
fn furniture_object(
    id: &str,
    catalog_id: Option<&str>,
    layer: FurnitureLayerKind,
    object_type: &str,
    label: &str,
    abbreviation: Option<&str>,
    x_m: f64,
    y_m: f64,
    width_m: f64,
    depth_m: f64,
    rotation_deg: f64,
    colour: &str,
    notes: Option<&str>,
    evidence: Option<&str>,
) -> FurnitureObject {
    FurnitureObject {
        id: id.to_string(),
        catalog_id: catalog_id.map(str::to_string),
        layer,
        z_index: 0,
        object_type: object_type.to_string(),
        label: label.to_string(),
        abbreviation: abbreviation.map(str::to_string),
        x_m,
        y_m,
        width_m,
        depth_m,
        l_shape: None,
        rotation_deg,
        colour: colour.to_string(),
        locked: false,
        notes: notes.map(str::to_string),
        evidence: evidence.map(str::to_string),
    }
}

#[allow(clippy::too_many_arguments)]
fn furniture_l_shape_object(
    id: &str,
    catalog_id: Option<&str>,
    layer: FurnitureLayerKind,
    object_type: &str,
    label: &str,
    abbreviation: Option<&str>,
    x_m: f64,
    y_m: f64,
    width_m: f64,
    depth_m: f64,
    main_depth_m: f64,
    return_width_m: f64,
    rotation_deg: f64,
    colour: &str,
    notes: Option<&str>,
    evidence: Option<&str>,
) -> FurnitureObject {
    let mut object = furniture_object(
        id,
        catalog_id,
        layer,
        object_type,
        label,
        abbreviation,
        x_m,
        y_m,
        width_m,
        depth_m,
        rotation_deg,
        colour,
        notes,
        evidence,
    );
    object.l_shape = Some(FurnitureLShapeDimensions {
        main_depth_m,
        return_width_m,
    });
    object
}

fn validate_finite(field: &str, value: f64, errors: &mut Vec<String>) {
    if !value.is_finite() {
        errors.push(format!("{field} must be finite"));
    }
}

fn is_hex_colour(value: &str) -> bool {
    value.len() == 7
        && value.starts_with('#')
        && value[1..]
            .chars()
            .all(|character| character.is_ascii_hexdigit())
}
