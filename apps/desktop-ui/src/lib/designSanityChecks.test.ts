import { describe, expect, it } from "vitest";
import type { FurnitureLayout, FurnitureObject, FurnitureLayerKind } from "../types";
import { buildDesignSanityChecks } from "./designSanityChecks";

function object(
  id: string,
  catalogId: string,
  type: string,
  x: number,
  y: number,
  width: number,
  depth: number,
  rotation = 0,
  layer: FurnitureLayerKind = "moveable",
): FurnitureObject {
  return {
    id,
    catalog_id: catalogId,
    layer,
    type,
    label: id,
    abbreviation: null,
    x_m: x,
    y_m: y,
    width_m: width,
    depth_m: depth,
    rotation_deg: rotation,
    colour: "#cccccc",
    locked: false,
    notes: null,
    evidence: null,
    z_index: 0,
  };
}

function layout(objects: FurnitureObject[], scenarioId = "back-side-living-sunroom-bedroom"): FurnitureLayout {
  return {
    project_id: "current-house",
    scenario_id: scenarioId,
    plan_transform: {
      units: "metres",
      svg_width_px: 1600,
      svg_height_px: 900,
      origin_svg_px: { x: 518, y: 314 },
      px_per_m: 27.16,
    },
    objects,
  };
}

describe("design sanity checks", () => {
  it("does not report checks for the current design", () => {
    const checks = buildDesignSanityChecks({
      scenarioId: "current",
      layout: layout([object("chair", "chair", "chair", 1, 1, 0.5, 0.5)], "current"),
      layoutSource: "saved",
    });

    expect(checks).toEqual([]);
  });

  it("flags future saved layouts as potentially stale after seed logic changes", () => {
    const checks = buildDesignSanityChecks({
      scenarioId: "back-side-living-sunroom-bedroom",
      layout: layout([object("chair", "chair", "chair", 11.5, 8.2, 0.5, 0.5)]),
      layoutSource: "saved",
    });

    expect(checks).toEqual(expect.arrayContaining([
      expect.objectContaining({
        id: "saved-layout-may-be-stale",
        severity: "info",
      }),
    ]));
  });

  it("flags furniture outside every proposed room and furniture that overlaps another item", () => {
    const checks = buildDesignSanityChecks({
      scenarioId: "back-side-living-sunroom-bedroom",
      layout: layout([
        object("sofa", "sofa", "sofa", 11.4, 8.2, 1.8, 0.8),
        object("chair", "chair", "chair", 11.5, 8.25, 0.8, 0.8),
        object("bookcase", "bookcase", "bookcase", 18, 2, 1.0, 0.3),
      ]),
      layoutSource: "seed",
    });

    expect(checks).toEqual(expect.arrayContaining([
      expect.objectContaining({
        id: "furniture-overlap",
        severity: "warning",
      }),
      expect.objectContaining({
        id: "furniture-outside-proposed-rooms",
        severity: "warning",
      }),
    ]));
    expect(checks.find((check) => check.id === "furniture-overlap")?.details.join(" ")).toContain("sofa");
    expect(checks.find((check) => check.id === "furniture-outside-proposed-rooms")?.details.join(" ")).toContain("bookcase");
  });

  it("allows intentional TV-on-dresser overlaps", () => {
    const checks = buildDesignSanityChecks({
      scenarioId: "back-side-living-sunroom-bedroom",
      layout: layout([
        object("dresser", "dresser_drawers", "dresser_drawers", 4.78, 2.1, 1.4, 0.4),
        object("tv", "tv", "tv", 4.78, 2.1, 1.2, 0.2),
      ]),
      layoutSource: "seed",
    });

    expect(checks.map((check) => check.id)).not.toContain("furniture-overlap");
  });

  it("flags future designs that still need a final vector model", () => {
    const checks = buildDesignSanityChecks({
      scenarioId: "wet-core-bright-day-room",
      layout: layout([object("chair", "chair", "chair", 11.5, 8.2, 0.5, 0.5)], "wet-core-bright-day-room"),
      layoutSource: "seed",
    });

    expect(checks).toEqual(expect.arrayContaining([
      expect.objectContaining({
        id: "final-vector-model-missing",
        severity: "info",
      }),
    ]));
  });
});
