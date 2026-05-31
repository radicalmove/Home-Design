export type FurnitureSymbol = {
  shape:
    | "rectangle"
    | "appliance"
    | "fixture"
    | "fireplace"
    | "sofa"
    | "l-shape"
    | "bed"
    | "bedside-table"
    | "desk"
    | "table"
    | "chair"
    | "storage"
    | "drawers"
    | "tv"
    | "heat-pump"
    | "partition-wall"
    | "sliding-door";
  abbreviation: string | null;
};

export function symbolForFurnitureObject(type: string, abbreviation: string | null): FurnitureSymbol {
  switch (type) {
    case "refrigerator":
    case "dishwasher":
    case "washer":
    case "dryer":
      return { shape: "appliance", abbreviation };
    case "toilet":
    case "shower":
    case "vanity":
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
    case "bookcase":
    case "cabinet":
      return { shape: "storage", abbreviation };
    default:
      return { shape: "rectangle", abbreviation };
  }
}
