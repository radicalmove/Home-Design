import type { PlanPoint, PlanTransform } from "../../types";

export type ScenePoint = {
  x: number;
  z: number;
};

export type SceneRectGeometry = {
  type: "rect";
  x: number;
  z: number;
  width: number;
  depth: number;
};

export type ScenePolygonGeometry = {
  type: "polygon";
  points: ScenePoint[];
};

export type SceneMultiPolygonGeometry = {
  type: "multi_polygon";
  polygons: ScenePoint[][];
};

export type SceneGeometry = SceneRectGeometry | ScenePolygonGeometry | SceneMultiPolygonGeometry;

export type SceneBounds = {
  minX: number;
  maxX: number;
  minZ: number;
  maxZ: number;
};

type JsonRecord = Record<string, unknown>;

function asRecord(value: unknown): JsonRecord {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? value as JsonRecord
    : {};
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function displayPointFromRaw(value: unknown): PlanPoint | null {
  if (!Array.isArray(value)) {
    return null;
  }
  const x = asNumber(value[0]);
  const y = asNumber(value[1]);
  return x === null || y === null ? null : { x, y };
}

export function displayPointToScene(point: PlanPoint, transform: PlanTransform): ScenePoint {
  return {
    x: (point.x - transform.origin_svg_px.x) / transform.px_per_m,
    z: (point.y - transform.origin_svg_px.y) / transform.px_per_m,
  };
}

export function displayLengthToMetres(lengthPx: number, transform: PlanTransform): number {
  return lengthPx / transform.px_per_m;
}

export function scenePointFromDisplayTuple(value: unknown, transform: PlanTransform): ScenePoint | null {
  const point = displayPointFromRaw(value);
  return point ? displayPointToScene(point, transform) : null;
}

export function sceneGeometryFromDisplayPx(value: unknown, transform: PlanTransform): SceneGeometry | null {
  const display = asRecord(value);
  const geometryType = display.type;

  if (geometryType === "rect") {
    const x = asNumber(display.x);
    const y = asNumber(display.y);
    const width = asNumber(display.width);
    const height = asNumber(display.height);
    if (x === null || y === null || width === null || height === null) {
      return null;
    }
    const origin = displayPointToScene({ x, y }, transform);
    return {
      type: "rect",
      x: origin.x,
      z: origin.z,
      width: displayLengthToMetres(width, transform),
      depth: displayLengthToMetres(height, transform),
    };
  }

  if (geometryType === "polygon") {
    const points = Array.isArray(display.points)
      ? display.points
        .map((point) => scenePointFromDisplayTuple(point, transform))
        .filter((point): point is ScenePoint => point !== null)
      : [];
    return points.length >= 3 ? { type: "polygon", points } : null;
  }

  if (geometryType === "multi_polygon") {
    const polygons = Array.isArray(display.polygons)
      ? display.polygons
        .filter(Array.isArray)
        .map((polygon) => polygon
          .map((point) => scenePointFromDisplayTuple(point, transform))
          .filter((point): point is ScenePoint => point !== null))
        .filter((polygon) => polygon.length >= 3)
      : [];
    return polygons.length > 0 ? { type: "multi_polygon", polygons } : null;
  }

  return null;
}

function boundsFromPoints(points: ScenePoint[]): SceneBounds | null {
  if (points.length === 0) {
    return null;
  }
  return {
    minX: Math.min(...points.map((point) => point.x)),
    maxX: Math.max(...points.map((point) => point.x)),
    minZ: Math.min(...points.map((point) => point.z)),
    maxZ: Math.max(...points.map((point) => point.z)),
  };
}

export function sceneGeometryBoundsList(geometry: SceneGeometry): SceneBounds[] {
  if (geometry.type === "rect") {
    return [
      {
        minX: geometry.x,
        maxX: geometry.x + geometry.width,
        minZ: geometry.z,
        maxZ: geometry.z + geometry.depth,
      },
    ];
  }

  if (geometry.type === "polygon") {
    const bounds = boundsFromPoints(geometry.points);
    return bounds ? [bounds] : [];
  }

  return geometry.polygons
    .map(boundsFromPoints)
    .filter((bounds): bounds is SceneBounds => bounds !== null);
}

export function sceneGeometryCentre(geometry: SceneGeometry): ScenePoint {
  const bounds = sceneGeometryBoundsList(geometry);
  if (bounds.length === 0) {
    return { x: 0, z: 0 };
  }
  return {
    x: (Math.min(...bounds.map((item) => item.minX)) + Math.max(...bounds.map((item) => item.maxX))) / 2,
    z: (Math.min(...bounds.map((item) => item.minZ)) + Math.max(...bounds.map((item) => item.maxZ))) / 2,
  };
}

export function sceneGeometryArea(geometry: SceneGeometry): number {
  if (geometry.type === "rect") {
    return Math.abs(geometry.width * geometry.depth);
  }
  const polygons = geometry.type === "polygon" ? [geometry.points] : geometry.polygons;
  return polygons.reduce((total, polygon) => {
    const area = polygon.reduce((sum, point, index) => {
      const next = polygon[(index + 1) % polygon.length];
      return sum + point.x * next.z - next.x * point.z;
    }, 0);
    return total + Math.abs(area) / 2;
  }, 0);
}
