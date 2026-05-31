import { describe, expect, it } from "vitest";
import {
  anchoredViewOriginAfterZoom,
  angleDegFromCenter,
  centeredViewOrigin,
  clampPlanZoom,
  dimensionLabel,
  metresToSvg,
  nextWheelPlanZoom,
  objectBoundsSvg,
  planViewBoxSize,
  planZoomLabel,
  resizeObjectFromHandle,
  resizeObjectFromCorner,
  rotateDeltaIntoObjectSpace,
  screenPixelsToSvgUnits,
  viewOriginAfterPan,
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

  it("resizes one horizontal edge while keeping the opposite edge fixed", () => {
    const resizedEast = resizeObjectFromHandle(object, "e", { deltaWidthM: 0.6, deltaDepthM: 2 });
    expect(resizedEast.width_m).toBeCloseTo(2.6);
    expect(resizedEast.depth_m).toBeCloseTo(0.9);
    expect(resizedEast.x_m - resizedEast.width_m / 2).toBeCloseTo(object.x_m - object.width_m / 2);
    expect(resizedEast.x_m).toBeCloseTo(5.3);

    const resizedWest = resizeObjectFromHandle(object, "w", { deltaWidthM: 0.6, deltaDepthM: 2 });
    expect(resizedWest.width_m).toBeCloseTo(1.4);
    expect(resizedWest.depth_m).toBeCloseTo(0.9);
    expect(resizedWest.x_m + resizedWest.width_m / 2).toBeCloseTo(object.x_m + object.width_m / 2);
    expect(resizedWest.x_m).toBeCloseTo(5.3);
  });

  it("resizes one vertical edge while keeping the opposite edge fixed", () => {
    const resizedNorth = resizeObjectFromHandle(object, "n", { deltaWidthM: 1, deltaDepthM: 0.2 });

    expect(resizedNorth.width_m).toBeCloseTo(2);
    expect(resizedNorth.depth_m).toBeCloseTo(0.7);
    expect(resizedNorth.y_m + resizedNorth.depth_m / 2).toBeCloseTo(object.y_m + object.depth_m / 2);
    expect(resizedNorth.y_m).toBeCloseTo(3.1);
  });

  it("resizes a rotated object along its local edge axis", () => {
    const rotated = { ...object, rotation_deg: 90 };
    const resized = resizeObjectFromHandle(rotated, "e", { deltaWidthM: 1, deltaDepthM: 0 });

    expect(resized.width_m).toBeCloseTo(3);
    expect(resized.depth_m).toBeCloseTo(0.9);
    expect(resized.x_m).toBeCloseTo(rotated.x_m);
    expect(resized.y_m).toBeCloseTo(rotated.y_m + 0.5);
  });

  it("clamps and labels furniture plan zoom", () => {
    expect(clampPlanZoom(0.2)).toBe(0.5);
    expect(clampPlanZoom(8)).toBe(5);
    expect(planZoomLabel(1.25)).toBe("125%");
  });

  it("computes wheel zoom up to 500 percent", () => {
    expect(nextWheelPlanZoom(1, -1)).toBe(1.1);
    expect(nextWheelPlanZoom(1, 1)).toBe(0.9);
    expect(nextWheelPlanZoom(4.9, -1)).toBe(5);
  });

  it("uses viewBox maths for a portrait furniture field of view", () => {
    const canvasSize = { width: 300, height: 600 };
    const fullView = planViewBoxSize(canvasSize, 1);
    const zoomedView = planViewBoxSize(canvasSize, 5);

    expect(fullView).toEqual({ width: 1600, height: 3200 });
    expect(zoomedView).toEqual({ width: 320, height: 640 });
    expect(zoomedView.height).toBe(zoomedView.width * 2);
    expect(centeredViewOrigin(fullView, { width: 1600, height: 900 })).toEqual({ x: 0, y: -1150 });
    expect(
      anchoredViewOriginAfterZoom(
        { x: 0, y: 0 },
        { x: 150, y: 300 },
        canvasSize,
        fullView,
        zoomedView,
      ),
    ).toEqual({ x: 640, y: 1280 });
    expect(
      viewOriginAfterPan(
        { x: 0, y: 0 },
        { x: 150, y: 300 },
        { x: 150, y: 450 },
        canvasSize,
        fullView,
      ).y,
    ).toBeCloseTo(-800);
  });

  it("converts screen pixels to SVG units so edit handles keep apparent size across zoom", () => {
    const canvasSize = { width: 300, height: 600 };
    const fullView = planViewBoxSize(canvasSize, 1);
    const zoomedView = planViewBoxSize(canvasSize, 5);

    expect(screenPixelsToSvgUnits(canvasSize, fullView, 12)).toBeCloseTo(64);
    expect(screenPixelsToSvgUnits(canvasSize, zoomedView, 12)).toBeCloseTo(12.8);
    expect((screenPixelsToSvgUnits(canvasSize, fullView, 12) / fullView.width) * canvasSize.width).toBeCloseTo(12);
    expect((screenPixelsToSvgUnits(canvasSize, zoomedView, 12) / zoomedView.width) * canvasSize.width).toBeCloseTo(12);
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
