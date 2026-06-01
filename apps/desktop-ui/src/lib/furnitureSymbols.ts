export type FurnitureSymbol = {
  shape:
    | "rectangle"
    | "appliance"
    | "fixture"
    | "refrigerator"
    | "washer"
    | "dryer"
    | "oven"
    | "island"
    | "fireplace"
    | "sofa"
    | "l-shape"
    | "bed"
    | "bedside-table"
    | "bath"
    | "basin"
    | "toilet"
    | "shower"
    | "desk"
    | "table"
    | "table-and-chairs"
    | "chair"
    | "armchair"
    | "storage"
    | "wardrobe"
    | "drawers"
    | "tv"
    | "heat-pump"
    | "partition-wall"
    | "sliding-door";
  abbreviation: string | null;
};

export function symbolForFurnitureObject(
  type: string,
  abbreviation: string | null,
  catalogId: string | null = null,
): FurnitureSymbol {
  switch (catalogId) {
    case "armchair":
      return { shape: "armchair", abbreviation };
    case "dining_table":
      return { shape: "table-and-chairs", abbreviation };
    case "island":
      return { shape: "island", abbreviation };
    case "oven_cooktop":
      return { shape: "oven", abbreviation };
    case "wardrobe":
      return { shape: "wardrobe", abbreviation };
  }

  switch (type) {
    case "refrigerator":
      return { shape: "refrigerator", abbreviation };
    case "washer":
      return { shape: "washer", abbreviation };
    case "dryer":
      return { shape: "dryer", abbreviation };
    case "dishwasher":
      return { shape: "appliance", abbreviation };
    case "appliance":
      return { shape: abbreviation === "OV" ? "oven" : "appliance", abbreviation };
    case "bath":
      return { shape: "bath", abbreviation };
    case "toilet":
      return { shape: "toilet", abbreviation };
    case "shower":
      return { shape: "shower", abbreviation };
    case "vanity":
      return { shape: "basin", abbreviation };
    case "fixture":
      return { shape: "fixture", abbreviation };
    case "fireplace":
      return { shape: "fireplace", abbreviation };
    case "sofa":
      return { shape: "sofa", abbreviation };
    case "l_sofa":
    case "l_desk":
      return { shape: "l-shape", abbreviation };
    case "bed":
      return { shape: "bed", abbreviation };
    case "bedside_table":
      return { shape: "bedside-table", abbreviation };
    case "dresser_drawers":
      return { shape: "drawers", abbreviation };
    case "tv":
      return { shape: "tv", abbreviation };
    case "heat_pump":
      return { shape: "heat-pump", abbreviation };
    case "partition_wall":
      return { shape: "partition-wall", abbreviation };
    case "wardrobe_doors":
      return { shape: "sliding-door", abbreviation };
    case "desk":
      return { shape: "desk", abbreviation };
    case "table":
      return { shape: "table", abbreviation };
    case "chair":
      return { shape: "chair", abbreviation };
    case "wardrobe":
      return { shape: "wardrobe", abbreviation };
    case "bookcase":
    case "cabinet":
      return { shape: "storage", abbreviation };
    default:
      return { shape: "rectangle", abbreviation };
  }
}
