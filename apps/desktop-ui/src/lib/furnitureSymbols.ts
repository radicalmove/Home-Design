export type FurnitureSymbol = {
  shape:
    | "rectangle"
    | "appliance"
    | "fixture"
    | "sofa"
    | "l-shape"
    | "bed"
    | "desk"
    | "table"
    | "chair"
    | "storage";
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
    case "sofa":
      return { shape: "sofa", abbreviation };
    case "l_sofa":
    case "l_desk":
      return { shape: "l-shape", abbreviation };
    case "bed":
      return { shape: "bed", abbreviation };
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
