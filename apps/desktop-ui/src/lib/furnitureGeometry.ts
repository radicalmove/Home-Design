import type { FurnitureLShapeDimensions, FurnitureObject, PlanPoint, PlanTransform } from "../types";

export type SvgBounds = {
  x: number;
  y: number;
  width: number;
  height: number;
  cx: number;
  cy: number;
};

export type PlanViewportSize = {
  width: number;
  height: number;
};

export type WallSegment = {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  thickness_px?: number;
};

export type WallDistanceGuideSide = "top" | "right" | "bottom" | "left";

export type WallDistanceGuide = {
  side: WallDistanceGuideSide;
  wallId: string;
  distance_m: number;
  label: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  labelX: number;
  labelY: number;
};

export type ResizeHandleName = "n" | "ne" | "e" | "se" | "s" | "sw" | "w" | "nw";

type ResizeHandleDirection = {
  x: -1 | 0 | 1;
  y: -1 | 0 | 1;
};

const RESIZE_HANDLE_DIRECTIONS: Record<ResizeHandleName, ResizeHandleDirection> = {
  n: { x: 0, y: -1 },
  ne: { x: 1, y: -1 },
  e: { x: 1, y: 0 },
  se: { x: 1, y: 1 },
  s: { x: 0, y: 1 },
  sw: { x: -1, y: 1 },
  w: { x: -1, y: 0 },
  nw: { x: -1, y: -1 },
};

export const MIN_PLAN_ZOOM = 0.5;
export const MAX_PLAN_ZOOM = 10;
export const PLAN_WHEEL_ZOOM_FACTOR = 1.1;
export const DEFAULT_PLAN_VIEWBOX_WIDTH = 1600;

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

function formatPathNumber(value: number): string {
  return value.toFixed(1);
}

export function lShapePath(
  bounds: Pick<SvgBounds, "x" | "y" | "width" | "height">,
  lShape: FurnitureLShapeDimensions,
  transform: PlanTransform,
): string {
  const mainDepth = Math.min(bounds.height, Math.max(0, lShape.main_depth_m * transform.px_per_m));
  const returnWidth = Math.min(bounds.width, Math.max(0, lShape.return_width_m * transform.px_per_m));
  const x0 = bounds.x;
  const y0 = bounds.y;
  const x1 = bounds.x + bounds.width;
  const y1 = bounds.y + bounds.height;
  const innerX = bounds.x + returnWidth;
  const innerY = bounds.y + mainDepth;

  return [
    "M",
    formatPathNumber(x0),
    formatPathNumber(y0),
    "H",
    formatPathNumber(x1),
    "V",
    formatPathNumber(innerY),
    "H",
    formatPathNumber(innerX),
    "V",
    formatPathNumber(y1),
    "H",
    formatPathNumber(x0),
    "Z",
  ].join(" ");
}

export function dimensionLabel(object: Pick<FurnitureObject, "width_m" | "depth_m">): string {
  return `${object.width_m.toFixed(2)} m x ${object.depth_m.toFixed(2)} m`;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function intervalsOverlap(aMin: number, aMax: number, bMin: number, bMax: number): boolean {
  return Math.min(aMax, bMax) >= Math.max(aMin, bMin);
}

function addNearestGuide(
  guides: Partial<Record<WallDistanceGuideSide, WallDistanceGuide>>,
  guide: WallDistanceGuide,
) {
  const current = guides[guide.side];
  if (!current || guide.distance_m < current.distance_m) {
    guides[guide.side] = guide;
  }
}

function distanceLabel(distanceM: number): string {
  return `${distanceM.toFixed(2)} m`;
}

export function nearestWallDistanceGuides(
  bounds: Pick<SvgBounds, "x" | "y" | "width" | "height">,
  wallSegments: WallSegment[],
  transform: Pick<PlanTransform, "px_per_m">,
): WallDistanceGuide[] {
  const objectLeft = bounds.x;
  const objectRight = bounds.x + bounds.width;
  const objectTop = bounds.y;
  const objectBottom = bounds.y + bounds.height;
  const objectCenterX = bounds.x + bounds.width / 2;
  const objectCenterY = bounds.y + bounds.height / 2;
  const nearest: Partial<Record<WallDistanceGuideSide, WallDistanceGuide>> = {};

  for (const wall of wallSegments) {
    const isHorizontal = wall.y1 === wall.y2;
    const isVertical = wall.x1 === wall.x2;
    const halfThickness = (wall.thickness_px ?? 0) / 2;

    if (isHorizontal) {
      const wallY = wall.y1;
      const wallLeft = Math.min(wall.x1, wall.x2);
      const wallRight = Math.max(wall.x1, wall.x2);
      if (!intervalsOverlap(objectLeft, objectRight, wallLeft, wallRight)) {
        continue;
      }

      const x = clamp(objectCenterX, Math.max(objectLeft, wallLeft), Math.min(objectRight, wallRight));
      if (wallY <= objectTop) {
        const wallFaceY = Math.min(objectTop, wallY + halfThickness);
        const distanceM = (objectTop - wallFaceY) / transform.px_per_m;
        addNearestGuide(nearest, {
          side: "top",
          wallId: wall.id,
          distance_m: distanceM,
          label: distanceLabel(distanceM),
          x1: x,
          y1: objectTop,
          x2: x,
          y2: wallFaceY,
          labelX: x,
          labelY: (objectTop + wallFaceY) / 2,
        });
      }
      if (wallY >= objectBottom) {
        const wallFaceY = Math.max(objectBottom, wallY - halfThickness);
        const distanceM = (wallFaceY - objectBottom) / transform.px_per_m;
        addNearestGuide(nearest, {
          side: "bottom",
          wallId: wall.id,
          distance_m: distanceM,
          label: distanceLabel(distanceM),
          x1: x,
          y1: objectBottom,
          x2: x,
          y2: wallFaceY,
          labelX: x,
          labelY: (objectBottom + wallFaceY) / 2,
        });
      }
    }

    if (isVertical) {
      const wallX = wall.x1;
      const wallTop = Math.min(wall.y1, wall.y2);
      const wallBottom = Math.max(wall.y1, wall.y2);
      if (!intervalsOverlap(objectTop, objectBottom, wallTop, wallBottom)) {
        continue;
      }

      const y = clamp(objectCenterY, Math.max(objectTop, wallTop), Math.min(objectBottom, wallBottom));
      if (wallX <= objectLeft) {
        const wallFaceX = Math.min(objectLeft, wallX + halfThickness);
        const distanceM = (objectLeft - wallFaceX) / transform.px_per_m;
        addNearestGuide(nearest, {
          side: "left",
          wallId: wall.id,
          distance_m: distanceM,
          label: distanceLabel(distanceM),
          x1: objectLeft,
          y1: y,
          x2: wallFaceX,
          y2: y,
          labelX: (objectLeft + wallFaceX) / 2,
          labelY: y,
        });
      }
      if (wallX >= objectRight) {
        const wallFaceX = Math.max(objectRight, wallX - halfThickness);
        const distanceM = (wallFaceX - objectRight) / transform.px_per_m;
        addNearestGuide(nearest, {
          side: "right",
          wallId: wall.id,
          distance_m: distanceM,
          label: distanceLabel(distanceM),
          x1: objectRight,
          y1: y,
          x2: wallFaceX,
          y2: y,
          labelX: (objectRight + wallFaceX) / 2,
          labelY: y,
        });
      }
    }
  }

  return ["top", "right", "bottom", "left"].flatMap((side) => {
    const guide = nearest[side as WallDistanceGuideSide];
    return guide ? [guide] : [];
  });
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

export function planViewBoxSize(
  canvasSize: PlanViewportSize,
  zoom: number,
  sourceWidth = DEFAULT_PLAN_VIEWBOX_WIDTH,
): PlanViewportSize {
  const safeCanvasWidth = Math.max(1, canvasSize.width);
  const safeCanvasHeight = Math.max(1, canvasSize.height);
  const width = sourceWidth / clampPlanZoom(zoom);

  return {
    width,
    height: width * (safeCanvasHeight / safeCanvasWidth),
  };
}

export function centeredViewOrigin(
  viewBoxSize: PlanViewportSize,
  sourceSize: PlanViewportSize,
): PlanPoint {
  return {
    x: (sourceSize.width - viewBoxSize.width) / 2,
    y: (sourceSize.height - viewBoxSize.height) / 2,
  };
}

export function svgPointInViewBox(
  viewOrigin: PlanPoint,
  pointerOffset: PlanPoint,
  canvasSize: PlanViewportSize,
  viewBoxSize: PlanViewportSize,
): PlanPoint {
  const safeCanvasWidth = Math.max(1, canvasSize.width);
  const safeCanvasHeight = Math.max(1, canvasSize.height);

  return {
    x: viewOrigin.x + (pointerOffset.x / safeCanvasWidth) * viewBoxSize.width,
    y: viewOrigin.y + (pointerOffset.y / safeCanvasHeight) * viewBoxSize.height,
  };
}

export function anchoredViewOriginAfterZoom(
  currentOrigin: PlanPoint,
  pointerOffset: PlanPoint,
  canvasSize: PlanViewportSize,
  currentViewBoxSize: PlanViewportSize,
  nextViewBoxSize: PlanViewportSize,
): PlanPoint {
  const safeCanvasWidth = Math.max(1, canvasSize.width);
  const safeCanvasHeight = Math.max(1, canvasSize.height);
  const anchor = svgPointInViewBox(currentOrigin, pointerOffset, canvasSize, currentViewBoxSize);

  return {
    x: anchor.x - (pointerOffset.x / safeCanvasWidth) * nextViewBoxSize.width,
    y: anchor.y - (pointerOffset.y / safeCanvasHeight) * nextViewBoxSize.height,
  };
}

export function viewOriginAfterPan(
  startOrigin: PlanPoint,
  startClient: PlanPoint,
  currentClient: PlanPoint,
  canvasSize: PlanViewportSize,
  viewBoxSize: PlanViewportSize,
): PlanPoint {
  const safeCanvasWidth = Math.max(1, canvasSize.width);
  const safeCanvasHeight = Math.max(1, canvasSize.height);

  return {
    x: startOrigin.x - ((currentClient.x - startClient.x) / safeCanvasWidth) * viewBoxSize.width,
    y: startOrigin.y - ((currentClient.y - startClient.y) / safeCanvasHeight) * viewBoxSize.height,
  };
}

export function screenPixelsToSvgUnits(
  canvasSize: PlanViewportSize,
  viewBoxSize: PlanViewportSize,
  pixels: number,
): number {
  const safeCanvasWidth = Math.max(1, canvasSize.width);
  return (pixels / safeCanvasWidth) * viewBoxSize.width;
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

function resizedAxis(
  sizeM: number,
  pointerDeltaM: number,
  direction: -1 | 0 | 1,
  minimumM: number,
): { sizeM: number; centreDeltaM: number } {
  if (direction === 0) {
    return { sizeM, centreDeltaM: 0 };
  }

  const nextSizeM = Math.max(minimumM, sizeM + direction * pointerDeltaM);
  const appliedEdgeDeltaM = (nextSizeM - sizeM) / direction;
  return {
    sizeM: nextSizeM,
    centreDeltaM: appliedEdgeDeltaM / 2,
  };
}

export function resizeObjectFromHandle<T extends FurnitureObject>(
  object: T,
  handle: ResizeHandleName,
  delta: { deltaWidthM: number; deltaDepthM: number },
  minimumM = 0.2,
): T {
  const direction = RESIZE_HANDLE_DIRECTIONS[handle];
  const width = resizedAxis(object.width_m, delta.deltaWidthM, direction.x, minimumM);
  const depth = resizedAxis(object.depth_m, delta.deltaDepthM, direction.y, minimumM);
  const radians = (object.rotation_deg * Math.PI) / 180;
  const cos = Math.cos(radians);
  const sin = Math.sin(radians);

  return {
    ...object,
    x_m: object.x_m + width.centreDeltaM * cos - depth.centreDeltaM * sin,
    y_m: object.y_m + width.centreDeltaM * sin + depth.centreDeltaM * cos,
    width_m: width.sizeM,
    depth_m: depth.sizeM,
  };
}
