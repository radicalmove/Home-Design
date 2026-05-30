import { describe, expect, it } from "vitest";
import {
  addCatalogItem,
  deleteObject,
  duplicateObject,
  moveObject,
  recolourObject,
  resizeObject,
  rotateObject,
} from "./furnitureState";
import type { FurnitureCatalogItem, FurnitureLayout } from "../types";

const layout: FurnitureLayout = {
  project_id: "current-house",
  scenario_id: "current",
  plan_transform: {
    units: "metres",
    svg_width_px: 1600,
    svg_height_px: 900,
    origin_svg_px: { x: 518, y: 314 },
    px_per_m: 27.16,
  },
  objects: [
    {
      id: "sofa",
      catalog_id: "sofa",
      layer: "moveable",
      type: "sofa",
      label: "Sofa",
      abbreviation: null,
      x_m: 1,
      y_m: 2,
      width_m: 2,
      depth_m: 1,
      rotation_deg: 0,
      colour: "#33312e",
      locked: false,
      notes: null,
      evidence: null,
    },
  ],
};

const catalogItem: FurnitureCatalogItem = {
  id: "custom_rectangle",
  label: "Custom rectangle",
  layer: "moveable",
  type: "custom",
  abbreviation: null,
  default_width_m: 1.2,
  default_depth_m: 0.6,
  colour: "#f7f8f6",
  symbol: "rectangle",
};

describe("furniture state reducers", () => {
  it("adds catalog items with unique ids", () => {
    const updated = addCatalogItem(layout, catalogItem, { x: 3, y: 4 });

    expect(updated.objects).toHaveLength(2);
    expect(updated.objects[1].id).toMatch(/^custom_rectangle-/);
    expect(updated.objects[1].x_m).toBe(3);
  });

  it("moves, resizes, rotates, and recolours objects immutably", () => {
    let updated = moveObject(layout, "sofa", { x: 2, y: 3 });
    updated = resizeObject(updated, "sofa", { width_m: 2.4, depth_m: 1.2 });
    updated = rotateObject(updated, "sofa", 90);
    updated = recolourObject(updated, "sofa", "#ffffff");

    expect(updated.objects[0]).toMatchObject({
      x_m: 2,
      y_m: 3,
      width_m: 2.4,
      depth_m: 1.2,
      rotation_deg: 90,
      colour: "#ffffff",
    });
    expect(layout.objects[0].x_m).toBe(1);
  });

  it("duplicates and deletes objects", () => {
    const duplicated = duplicateObject(layout, "sofa");
    expect(duplicated.objects).toHaveLength(2);
    expect(duplicated.objects[1].id).toMatch(/^sofa-copy-/);

    const deleted = deleteObject(duplicated, "sofa");
    expect(deleted.objects.map((object) => object.id)).not.toContain("sofa");
  });
});
