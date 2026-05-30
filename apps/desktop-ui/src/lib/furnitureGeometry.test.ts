import { describe, expect, it } from "vitest";
import {
  dimensionLabel,
  metresToSvg,
  objectBoundsSvg,
  resizeObjectFromCorner,
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
});
