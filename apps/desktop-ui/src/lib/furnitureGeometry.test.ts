import { describe, expect, it } from "vitest";
import {
  anchoredScrollAfterZoom,
  angleDegFromCenter,
  clampPlanZoom,
  dimensionLabel,
  metresToSvg,
  nextWheelPlanZoom,
  objectBoundsSvg,
  planZoomLabel,
  resizeObjectFromCorner,
  rotateDeltaIntoObjectSpace,
  svgToMetres,
} from "./furnitureGeometry";
import type { FurnitureObject, PlanTransform } from "../types";

const transform: PlanTransform = {
  units: "metres",
  svg_width_px: 1600,
  svg_height_px: 900,
  origin_svg_px: { x: 518, y: 314 },
  px_per_m: 27.160493827160494,
};

const object: FurnitureObject = {
  id: "sofa",
  catalog_id: "sofa",
  layer: "moveable",
  type: "sofa",
  label: "Sofa",
  abbreviation: null,
  x_m: 5,
  y_m: 3,
  width_m: 2,
  depth_m: 0.9,
  rotation_deg: 0,
  colour: "#33312e",
  locked: false,
  notes: null,
  evidence: null,
};

describe("furniture geometry", () => {
  it("round trips between metres and SVG coordinates", () => {
    const svg = metresToSvg({ x: 2.5, y: 1.25 }, transform);
    const metres = svgToMetres(svg, transform);

    expect(metres.x).toBeCloseTo(2.5, 5);
    expect(metres.y).toBeCloseTo(1.25, 5);
  });

  it("computes SVG object bounds from metre dimensions", () => {
    const bounds = objectBoundsSvg(object, transform);

    expect(bounds.width).toBeCloseTo(54.32, 1);
    expect(bounds.height).toBeCloseTo(24.44, 1);
  });

  it("formats live dimensions in metres", () => {
    expect(dimensionLabel(object)).toBe("2.00 m x 0.90 m");
  });

  it("resizes from a corner with minimum positive dimensions", () => {
    const resized = resizeObjectFromCorner(object, { deltaWidthM: -4, deltaDepthM: 1 }, 0.2);

    expect(resized.width_m).toBe(0.2);
    expect(resized.depth_m).toBeCloseTo(1.9);
  });

  it("clamps and labels furniture plan zoom", () => {
    expect(clampPlanZoom(0.2)).toBe(0.5);
    expect(clampPlanZoom(3)).toBe(2.5);
    expect(planZoomLabel(1.25)).toBe("125%");
  });

  it("computes wheel zoom and keeps the cursor anchor stable", () => {
    expect(nextWheelPlanZoom(1, -1)).toBe(1.1);
    expect(nextWheelPlanZoom(1, 1)).toBe(0.9);

    expect(
      anchoredScrollAfterZoom(
        { x: 100, y: 50 },
        { x: 200, y: 100 },
        1,
        1.5,
      ),
    ).toEqual({ x: 250, y: 125 });
  });

  it("measures rotation from object centre in SVG space", () => {
    const bounds = objectBoundsSvg(object, transform);

    expect(angleDegFromCenter({ x: bounds.cx, y: bounds.cy - 20 }, bounds)).toBe(270);
    expect(angleDegFromCenter({ x: bounds.cx + 20, y: bounds.cy }, bounds)).toBe(0);
  });

  it("converts drag deltas into rotated object space for resize handles", () => {
    const local = rotateDeltaIntoObjectSpace({ x: 0, y: 27.16 }, 90, transform);

    expect(local.deltaWidthM).toBeCloseTo(1, 2);
    expect(local.deltaDepthM).toBeCloseTo(0, 2);
  });
});
