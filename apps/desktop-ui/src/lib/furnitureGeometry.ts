import type { FurnitureObject, PlanPoint, PlanTransform } from "../types";

export type SvgBounds = {
  x: number;
  y: number;
  width: number;
  height: number;
  cx: number;
  cy: number;
};

export function metresToSvg(point: PlanPoint, transform: PlanTransform): PlanPoint {
  return {
    x: transform.origin_svg_px.x + point.x * transform.px_per_m,
    y: transform.origin_svg_px.y + point.y * transform.px_per_m,
  };
}

export function svgToMetres(point: PlanPoint, transform: PlanTransform): PlanPoint {
  return {
    x: (point.x - transform.origin_svg_px.x) / transform.px_per_m,
    y: (point.y - transform.origin_svg_px.y) / transform.px_per_m,
  };
}

export function objectBoundsSvg(object: FurnitureObject, transform: PlanTransform): SvgBounds {
  const centre = metresToSvg({ x: object.x_m, y: object.y_m }, transform);
  const width = object.width_m * transform.px_per_m;
  const height = object.depth_m * transform.px_per_m;

  return {
    x: centre.x - width / 2,
    y: centre.y - height / 2,
    width,
    height,
    cx: centre.x,
    cy: centre.y,
  };
}

export function dimensionLabel(object: Pick<FurnitureObject, "width_m" | "depth_m">): string {
  return `${object.width_m.toFixed(2)} m x ${object.depth_m.toFixed(2)} m`;
}

export function resizeObjectFromCorner<T extends FurnitureObject>(
  object: T,
  delta: { deltaWidthM: number; deltaDepthM: number },
  minimumM = 0.2,
): T {
  return {
    ...object,
    width_m: Math.max(minimumM, object.width_m + delta.deltaWidthM),
    depth_m: Math.max(minimumM, object.depth_m + delta.deltaDepthM),
  };
}
