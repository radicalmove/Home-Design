import { describe, expect, it } from "vitest";
import {
  addCatalogItem,
  changeObjectLayer,
  deleteObject,
  duplicateObject,
  moveObject,
  normaliseFurnitureLayout,
  PARTITION_WALL_THICKNESS_M,
  recolourObject,
  reorderObject,
  resizeObject,
  rotateObject,
  sortedFurnitureObjects,
  WARDROBE_DOOR_THICKNESS_M,
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
      z_index: 0,
      rotation_deg: 0,
      colour: "#33312e",
      locked: false,
      notes: null,
      evidence: null,
    },
    {
      id: "legacy-l-shaped-sofa",
      catalog_id: "sofa",
      layer: "moveable",
      type: "sofa",
      label: "L-shaped sofa",
      abbreviation: null,
      x_m: 3,
      y_m: 4,
      width_m: 2.8,
      depth_m: 1.85,
      z_index: 1,
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

const lShapeCatalogItem: FurnitureCatalogItem = {
  id: "l_sofa",
  label: "L-shaped sofa",
  layer: "moveable",
  type: "l_sofa",
  abbreviation: null,
  default_width_m: 2.8,
  default_depth_m: 1.85,
  default_l_shape: {
    main_depth_m: 0.9,
    return_width_m: 1.05,
  },
  colour: "#33312e",
  symbol: "l-shape",
};

describe("furniture state reducers", () => {
  it("adds catalog items with unique ids", () => {
    const updated = addCatalogItem(layout, catalogItem, { x: 3, y: 4 });

    expect(updated.objects).toHaveLength(3);
    expect(updated.objects[2].id).toMatch(/^custom_rectangle-/);
    expect(updated.objects[2].x_m).toBe(3);
    expect(updated.objects[2].y_m).toBe(4);
  });

  it("adds L-shaped catalog items with adjustable arm dimensions", () => {
    const updated = addCatalogItem(layout, lShapeCatalogItem, { x: 6, y: 7 });

    expect(updated.objects.at(-1)).toMatchObject({
      catalog_id: "l_sofa",
      type: "l_sofa",
      width_m: 2.8,
      depth_m: 1.85,
      l_shape: {
        main_depth_m: 0.9,
        return_width_m: 1.05,
      },
    });
  });

  it("moves, resizes, rotates, and recolours objects immutably", () => {
    let updated = moveObject(layout, "sofa", { x: 2, y: 3 });
    updated = resizeObject(updated, "sofa", { width_m: 2.4, depth_m: 1.2 });
    updated = rotateObject(updated, "sofa", -15);
    updated = recolourObject(updated, "sofa", "#ffffff");

    expect(updated.objects[0]).toMatchObject({
      x_m: 2,
      y_m: 3,
      width_m: 2.4,
      depth_m: 1.2,
      rotation_deg: 345,
      colour: "#ffffff",
    });
    expect(layout.objects[0].x_m).toBe(1);
  });

  it("changes an object's fixed or moveable layer", () => {
    const updated = changeObjectLayer(layout, "sofa", "fixed");

    expect(updated.objects[0].layer).toBe("fixed");
    expect(layout.objects[0].layer).toBe("moveable");
  });

  it("rounds manual geometry edits to centimetre precision", () => {
    const moved = moveObject(layout, "sofa", {
      x: 6.276969728639951,
      y: 7.471349780045722,
    });
    const resized = resizeObject(moved, "sofa", {
      width_m: 1.704,
      depth_m: 0.666,
    });

    expect(resized.objects[0]).toMatchObject({
      x_m: 6.28,
      y_m: 7.47,
      width_m: 1.7,
      depth_m: 0.67,
    });
  });

  it("keeps partition wall depth locked when resizing", () => {
    const withPartitionWall: FurnitureLayout = {
      ...layout,
      objects: [
        ...layout.objects,
        {
          id: "partition",
          catalog_id: "partition_wall",
          layer: "fixed",
          type: "partition_wall",
          label: "Partition wall",
          abbreviation: null,
          x_m: 6,
          y_m: 7,
          width_m: 1.2,
          depth_m: PARTITION_WALL_THICKNESS_M,
          z_index: 2,
          rotation_deg: 0,
          colour: "#4e555e",
          locked: false,
          notes: null,
          evidence: null,
        },
      ],
    };

    const resized = resizeObject(withPartitionWall, "partition", {
      width_m: 2.4,
      depth_m: 0.8,
    });

    expect(resized.objects.at(-1)).toMatchObject({
      width_m: 2.4,
      depth_m: PARTITION_WALL_THICKNESS_M,
    });
  });

  it("repairs saved partition walls that were accidentally widened", () => {
    const loaded: FurnitureLayout = {
      ...layout,
      objects: [
        {
          ...layout.objects[0],
          id: "partition",
          catalog_id: "partition_wall",
          layer: "fixed",
          type: "partition_wall",
          label: "Partition wall",
          width_m: 1.234,
          depth_m: 0.8,
        },
      ],
    };

    const normalised = normaliseFurnitureLayout(loaded);

    expect(normalised.objects[0]).toMatchObject({
      width_m: 1.23,
      depth_m: PARTITION_WALL_THICKNESS_M,
    });
  });

  it("keeps wardrobe door depth locked when resizing", () => {
    const withWardrobeDoors: FurnitureLayout = {
      ...layout,
      objects: [
        ...layout.objects,
        {
          id: "wardrobe-doors",
          catalog_id: "wardrobe_doors",
          layer: "fixed",
          type: "wardrobe_doors",
          label: "Wardrobe doors",
          abbreviation: null,
          x_m: 6,
          y_m: 7,
          width_m: 1.6,
          depth_m: WARDROBE_DOOR_THICKNESS_M,
          z_index: 2,
          rotation_deg: 0,
          colour: "#f7f8f6",
          locked: false,
          notes: null,
          evidence: null,
        },
      ],
    };

    const resized = resizeObject(withWardrobeDoors, "wardrobe-doors", {
      width_m: 2.1,
      depth_m: 0.6,
    });

    expect(resized.objects.at(-1)).toMatchObject({
      width_m: 2.1,
      depth_m: WARDROBE_DOOR_THICKNESS_M,
    });
  });

  it("repairs saved wardrobe doors that were accidentally deepened", () => {
    const loaded: FurnitureLayout = {
      ...layout,
      objects: [
        {
          ...layout.objects[0],
          id: "wardrobe-doors",
          catalog_id: "wardrobe_doors",
          layer: "fixed",
          type: "wardrobe_doors",
          label: "Wardrobe doors",
          width_m: 1.638,
          depth_m: 0.4,
        },
      ],
    };

    const normalised = normaliseFurnitureLayout(loaded);

    expect(normalised.objects[0]).toMatchObject({
      width_m: 1.64,
      depth_m: WARDROBE_DOOR_THICKNESS_M,
    });
  });

  it("normalises loaded layouts without mutating the original", () => {
    const loaded = {
      ...layout,
      objects: [
        {
          ...layout.objects[0],
          x_m: 6.276969728639951,
          y_m: 7.471349780045722,
          width_m: 1.704,
          depth_m: 0.666,
          l_shape: {
            main_depth_m: 0.704,
            return_width_m: 3.1,
          },
        },
      ],
    };

    const normalised = normaliseFurnitureLayout(loaded);

    expect(normalised.objects[0]).toMatchObject({
      x_m: 6.28,
      y_m: 7.47,
      width_m: 1.7,
      depth_m: 0.67,
      l_shape: {
        main_depth_m: 0.67,
        return_width_m: 1.7,
      },
    });
    expect(loaded.objects[0].x_m).toBe(6.276969728639951);
  });

  it("upgrades legacy seeded L-shaped furniture when saved layouts are loaded", () => {
    const normalised = normaliseFurnitureLayout(layout);
    const upgraded = normalised.objects.find((object) => object.id === "legacy-l-shaped-sofa");

    expect(upgraded).toMatchObject({
      catalog_id: "l_sofa",
      type: "l_sofa",
      l_shape: {
        main_depth_m: 0.9,
        return_width_m: 1.05,
      },
    });
  });

  it("normalises legacy layouts with missing z-indexes from existing order", () => {
    const legacyLayout = {
      ...layout,
      objects: layout.objects.map(({ z_index: _zIndex, ...object }) => object),
    } as FurnitureLayout;

    const normalised = normaliseFurnitureLayout(legacyLayout);

    expect(normalised.objects.map((object) => object.z_index)).toEqual([0, 1]);
  });

  it("normalises mixed missing z-indexes using the existing array order", () => {
    const mixedLayout = {
      ...layout,
      objects: [
        { ...layout.objects[0], id: "A", z_index: 1 },
        (({ z_index: _zIndex, ...object }) => ({ ...object, id: "B" }))(layout.objects[1]),
        { ...layout.objects[0], id: "C", z_index: 2 },
      ],
    } as FurnitureLayout;

    const normalised = normaliseFurnitureLayout(mixedLayout);

    expect(sortedFurnitureObjects(normalised.objects).map((object) => object.id)).toEqual([
      "A",
      "B",
      "C",
    ]);
    expect(normalised.objects.map((object) => object.z_index)).toEqual([0, 1, 2]);
  });

  it("adds and duplicates objects at the front of the global furniture order", () => {
    const added = addCatalogItem(layout, catalogItem, { x: 3, y: 4 });
    expect(added.objects.at(-1)?.z_index).toBe(2);

    const duplicated = duplicateObject(layout, "sofa");
    expect(duplicated.objects.at(-1)).toMatchObject({
      z_index: 2,
      locked: false,
    });
  });

  it("sorts furniture objects by z-index with array order as the tie breaker", () => {
    const unordered = {
      ...layout,
      objects: [
        { ...layout.objects[0], id: "front", z_index: 10 },
        { ...layout.objects[1], id: "back", z_index: 2 },
        { ...layout.objects[0], id: "middle", z_index: 2 },
      ],
    };

    expect(sortedFurnitureObjects(unordered.objects).map((object) => object.id)).toEqual([
      "back",
      "middle",
      "front",
    ]);
  });

  it("reorders objects globally without changing geometry or layer", () => {
    const orderedLayout = {
      ...layout,
      objects: [
        { ...layout.objects[0], id: "desk", z_index: 0, x_m: 1, layer: "fixed" as const },
        { ...layout.objects[1], id: "chair", z_index: 1, x_m: 2, layer: "moveable" as const },
        { ...layout.objects[0], id: "lamp", z_index: 2, x_m: 3, layer: "moveable" as const },
      ],
    };

    const sentBackward = reorderObject(orderedLayout, "chair", "backward");
    expect(sortedFurnitureObjects(sentBackward.objects).map((object) => object.id)).toEqual([
      "chair",
      "desk",
      "lamp",
    ]);
    expect(sentBackward.objects.find((object) => object.id === "chair")).toMatchObject({
      x_m: 2,
      layer: "moveable",
    });

    const broughtToFront = reorderObject(sentBackward, "chair", "front");
    expect(sortedFurnitureObjects(broughtToFront.objects).at(-1)?.id).toBe("chair");

    const sentToBack = reorderObject(broughtToFront, "chair", "back");
    expect(sortedFurnitureObjects(sentToBack.objects)[0].id).toBe("chair");
  });

  it("leaves boundary and missing-object reorders harmless", () => {
    expect(reorderObject(layout, "sofa", "back")).toEqual(layout);
    expect(reorderObject(layout, "missing", "front")).toEqual(layout);
  });

  it("resizes L-shaped arm dimensions separately from the outer footprint", () => {
    const withLShape = addCatalogItem(layout, lShapeCatalogItem, { x: 6, y: 7 });
    const objectId = withLShape.objects.at(-1)?.id ?? "";
    const updated = resizeObject(withLShape, objectId, {
      width_m: 2.4,
      depth_m: 1.6,
      l_shape: {
        main_depth_m: 0.75,
        return_width_m: 0.85,
      },
    });

    expect(updated.objects.at(-1)).toMatchObject({
      width_m: 2.4,
      depth_m: 1.6,
      l_shape: {
        main_depth_m: 0.75,
        return_width_m: 0.85,
      },
    });
  });

  it("duplicates and deletes objects", () => {
    const duplicated = duplicateObject(layout, "sofa");
    expect(duplicated.objects).toHaveLength(3);
    expect(duplicated.objects.at(-1)?.id).toMatch(/^sofa-copy-/);

    const deleted = deleteObject(duplicated, "sofa");
    expect(deleted.objects.map((object) => object.id)).not.toContain("sofa");
  });
});
