import { describe, expect, it } from "vitest";
import { buildEstimatedCostAnalysis } from "./estimatedCosts";
import type { DesignReviewData, FurnitureObject } from "../types";

function object(type: string, id: string, layer: "fixed" | "moveable" = "fixed"): FurnitureObject {
  return {
    id,
    catalog_id: null,
    layer,
    type,
    label: id,
    abbreviation: null,
    x_m: 0,
    y_m: 0,
    width_m: 1,
    depth_m: 1,
    z_index: 0,
    rotation_deg: 0,
    colour: "#ffffff",
    locked: false,
    notes: null,
    evidence: null,
  };
}

const design2Data: DesignReviewData = {
  model_source: "DATA/house_model.json",
  house_model: {},
  furniture_layout: {
    source: "saved",
    layout: {
      project_id: "current-house",
      scenario_id: "back-side-living-sunroom-bedroom",
      plan_transform: {
        units: "metres",
        svg_width_px: 1600,
        svg_height_px: 900,
        origin_svg_px: { x: 518, y: 314 },
        px_per_m: 27.16,
      },
      objects: [
        object("toilet", "toilet-1"),
        object("toilet", "toilet-2"),
        object("partition_wall", "partition-1"),
        object("partition_wall", "partition-2"),
        object("partition_wall", "partition-3"),
        object("partition_wall", "partition-4"),
        object("bath", "bath-1"),
        object("vanity", "vanity-1"),
        object("washer", "washer-1"),
        object("dryer", "dryer-1"),
        object("counter", "counter-1"),
        object("sofa", "sofa-1", "moveable"),
      ],
    },
  },
};

describe("estimated cost analysis", () => {
  it("builds a Design 2 cost breakdown from the saved furniture and service-room layout", () => {
    const analysis = buildEstimatedCostAnalysis(design2Data);

    expect(analysis.scenarioId).toBe("back-side-living-sunroom-bedroom");
    expect(analysis.rangeLabel).toBe("NZD 250k-640k+");
    expect(analysis.summary).toContain("planning estimate");
    expect(analysis.furnitureSignals).toContain("2 toilet fixtures");
    expect(analysis.furnitureSignals).toContain("4 partition wall objects");
    expect(analysis.furnitureSignals).toContain("bath, vanity, washer, dryer, and counter/cabinet objects");
    expect(analysis.lines.map((line) => line.item)).toContain("Roof and envelope rethink");
    expect(analysis.roofNotes.join(" ")).toContain("former sunroom");
    expect(analysis.exclusions.join(" ")).toContain("builder's quote");
    expect(analysis.totalLow).toBe(250_000);
    expect(analysis.totalHigh).toBe(640_000);
  });
});
