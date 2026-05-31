import type { FurnitureObject, PlanPoint, PlanTransform } from "../types";

export type SvgBounds = {
  x: number;
  y: number;
  width: number;
  height: number;
  cx: number;
  cy: number;
};

export const MIN_PLAN_ZOOM = 0.5;
export const MAX_PLAN_ZOOM = 2.5;
export const PLAN_WHEEL_ZOOM_FACTOR = 1.1;

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

export function clampPlanZoom(zoom: number): number {
  return Math.min(MAX_PLAN_ZOOM, Math.max(MIN_PLAN_ZOOM, Math.round(zoom * 20) / 20));
}

export function planZoomLabel(zoom: number): string {
  return `${Math.round(clampPlanZoom(zoom) * 100)}%`;
}

export function nextWheelPlanZoom(currentZoom: number, deltaY: number): number {
  if (deltaY === 0) {
    return clampPlanZoom(currentZoom);
  }

  const zoomFactor = deltaY < 0 ? PLAN_WHEEL_ZOOM_FACTOR : 1 / PLAN_WHEEL_ZOOM_FACTOR;
  return clampPlanZoom(currentZoom * zoomFactor);
}

export function anchoredScrollAfterZoom(
  currentScroll: PlanPoint,
  pointerOffset: PlanPoint,
  currentZoom: number,
  nextZoom: number,
): PlanPoint {
  if (currentZoom <= 0) {
    return currentScroll;
  }

  const zoomRatio = nextZoom / currentZoom;
  return {
    x: (currentScroll.x + pointerOffset.x) * zoomRatio - pointerOffset.x,
    y: (currentScroll.y + pointerOffset.y) * zoomRatio - pointerOffset.y,
  };
}

export function angleDegFromCenter(point: PlanPoint, bounds: Pick<SvgBounds, "cx" | "cy">): number {
  const angle = Math.atan2(point.y - bounds.cy, point.x - bounds.cx) * (180 / Math.PI);
  return normaliseDegrees(angle);
}

export function normaliseDegrees(degrees: number): number {
  return Math.round(((degrees % 360) + 360) % 360);
}

export function rotateDeltaIntoObjectSpace(
  deltaSvg: PlanPoint,
  rotationDeg: number,
  transform: PlanTransform,
): { deltaWidthM: number; deltaDepthM: number } {
  const radians = (rotationDeg * Math.PI) / 180;
  const cos = Math.cos(radians);
  const sin = Math.sin(radians);

  return {
    deltaWidthM: (deltaSvg.x * cos + deltaSvg.y * sin) / transform.px_per_m,
    deltaDepthM: (-deltaSvg.x * sin + deltaSvg.y * cos) / transform.px_per_m,
  };
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
