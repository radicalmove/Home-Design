import type { FurnitureLayout, FurnitureObject, PlanTransform } from "../types";
import { CURRENT_SCENARIO_ID } from "./designScenarios";
import {
  currentPlanVectorModel,
  planVectorModelForScenario,
  type PlanVectorModel,
  type PlanVectorShape,
} from "./planVectorModel";

export type DesignSanitySeverity = "warning" | "info";

export type DesignSanityCheck = {
  id: string;
  severity: DesignSanitySeverity;
  title: string;
  details: string[];
};

export type DesignSanityCheckInput = {
  scenarioId: string;
  layout: FurnitureLayout;
  layoutSource?: "seed" | "saved" | null;
};

type Bounds = {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
};

const FINAL_VECTOR_SCENARIO_IDS = new Set(["back-side-living-sunroom-bedroom"]);
const OVERLAP_TOLERANCE_M = 0.08;
const OUTSIDE_TOLERANCE_PX = 4;

const TV_TYPES = new Set(["tv", "television"]);
const TV_SUPPORT_TYPES = new Set([
  "dresser_drawers",
  "dresser",
  "tv_unit",
  "media_unit",
  "cabinet",
  "base_cabinet",
  "fireplace",
]);

function objectLabel(object: FurnitureObject): string {
  return object.label || object.catalog_id || object.type || object.id;
}

function normalisedType(object: FurnitureObject): string {
  return (object.catalog_id || object.type || "").toLowerCase();
}

function boundsFromPoints(points: Array<[number, number]>): Bounds {
  return points.reduce<Bounds>(
    (bounds, [x, y]) => ({
      minX: Math.min(bounds.minX, x),
      minY: Math.min(bounds.minY, y),
      maxX: Math.max(bounds.maxX, x),
      maxY: Math.max(bounds.maxY, y),
    }),
    {
      minX: Number.POSITIVE_INFINITY,
      minY: Number.POSITIVE_INFINITY,
      maxX: Number.NEGATIVE_INFINITY,
      maxY: Number.NEGATIVE_INFINITY,
    },
  );
}

function shapeBounds(shape: PlanVectorShape): Bounds {
  if (shape.kind === "rect") {
    return {
      minX: shape.x,
      minY: shape.y,
      maxX: shape.x + shape.width,
      maxY: shape.y + shape.height,
    };
  }

  if (shape.kind === "multi_polygon") {
    return unionBounds(shape.polygons.map((points) => boundsFromPoints(points)));
  }

  return boundsFromPoints(shape.points);
}

function unionBounds(bounds: Bounds[]): Bounds {
  return bounds.reduce<Bounds>(
    (combined, next) => ({
      minX: Math.min(combined.minX, next.minX),
      minY: Math.min(combined.minY, next.minY),
      maxX: Math.max(combined.maxX, next.maxX),
      maxY: Math.max(combined.maxY, next.maxY),
    }),
    {
      minX: Number.POSITIVE_INFINITY,
      minY: Number.POSITIVE_INFINITY,
      maxX: Number.NEGATIVE_INFINITY,
      maxY: Number.NEGATIVE_INFINITY,
    },
  );
}

function isFiniteBounds(bounds: Bounds): boolean {
  return [bounds.minX, bounds.minY, bounds.maxX, bounds.maxY].every(Number.isFinite);
}

function rotatedFootprint(object: FurnitureObject): { widthM: number; depthM: number } {
  const radians = (object.rotation_deg * Math.PI) / 180;
  const cos = Math.abs(Math.cos(radians));
  const sin = Math.abs(Math.sin(radians));

  return {
    widthM: object.width_m * cos + object.depth_m * sin,
    depthM: object.width_m * sin + object.depth_m * cos,
  };
}

function objectBoundsMetres(object: FurnitureObject): Bounds {
  const footprint = rotatedFootprint(object);
  const halfWidth = footprint.widthM / 2;
  const halfDepth = footprint.depthM / 2;

  return {
    minX: object.x_m - halfWidth,
    minY: object.y_m - halfDepth,
    maxX: object.x_m + halfWidth,
    maxY: object.y_m + halfDepth,
  };
}

function objectBoundsSvg(object: FurnitureObject, transform: PlanTransform): Bounds {
  const bounds = objectBoundsMetres(object);

  return {
    minX: transform.origin_svg_px.x + bounds.minX * transform.px_per_m,
    minY: transform.origin_svg_px.y + bounds.minY * transform.px_per_m,
    maxX: transform.origin_svg_px.x + bounds.maxX * transform.px_per_m,
    maxY: transform.origin_svg_px.y + bounds.maxY * transform.px_per_m,
  };
}

function containsBounds(container: Bounds, inner: Bounds, tolerance = 0): boolean {
  return (
    inner.minX >= container.minX - tolerance &&
    inner.maxX <= container.maxX + tolerance &&
    inner.minY >= container.minY - tolerance &&
    inner.maxY <= container.maxY + tolerance
  );
}

function overlapSize(a: Bounds, b: Bounds): { width: number; height: number } {
  return {
    width: Math.max(0, Math.min(a.maxX, b.maxX) - Math.max(a.minX, b.minX)),
    height: Math.max(0, Math.min(a.maxY, b.maxY) - Math.max(a.minY, b.minY)),
  };
}

function canIntentionallyOverlap(a: FurnitureObject, b: FurnitureObject): boolean {
  const typeA = normalisedType(a);
  const typeB = normalisedType(b);
  return (
    (TV_TYPES.has(typeA) && TV_SUPPORT_TYPES.has(typeB)) ||
    (TV_TYPES.has(typeB) && TV_SUPPORT_TYPES.has(typeA))
  );
}

function roomBoundsForScenario(scenarioId: string): Bounds[] {
  const model: PlanVectorModel = planVectorModelForScenario(scenarioId);
  return model.rooms.map((room) => shapeBounds(room.shape)).filter(isFiniteBounds);
}

function hasFinalVectorModel(scenarioId: string): boolean {
  return scenarioId === CURRENT_SCENARIO_ID || FINAL_VECTOR_SCENARIO_IDS.has(scenarioId);
}

function findOverlaps(objects: FurnitureObject[]): string[] {
  const details: string[] = [];

  objects.forEach((object, objectIndex) => {
    objects.slice(objectIndex + 1).forEach((otherObject) => {
      if (canIntentionallyOverlap(object, otherObject)) {
        return;
      }

      const overlap = overlapSize(objectBoundsMetres(object), objectBoundsMetres(otherObject));
      if (overlap.width > OVERLAP_TOLERANCE_M && overlap.height > OVERLAP_TOLERANCE_M) {
        details.push(`${objectLabel(object)} overlaps ${objectLabel(otherObject)}.`);
      }
    });
  });

  return details;
}

function findObjectsOutsideRooms(layout: FurnitureLayout, roomBounds: Bounds[]): string[] {
  if (roomBounds.length === 0) {
    return [];
  }

  return layout.objects
    .filter((object) => {
      const bounds = objectBoundsSvg(object, layout.plan_transform);
      return !roomBounds.some((room) => containsBounds(room, bounds, OUTSIDE_TOLERANCE_PX));
    })
    .map((object) => `${objectLabel(object)} sits outside the current proposed room envelopes.`);
}

export function buildDesignSanityChecks(input: DesignSanityCheckInput): DesignSanityCheck[] {
  if (input.scenarioId === CURRENT_SCENARIO_ID) {
    return [];
  }

  const checks: DesignSanityCheck[] = [];
  const finalVectorModelAvailable = hasFinalVectorModel(input.scenarioId);

  if (!finalVectorModelAvailable && planVectorModelForScenario(input.scenarioId) === currentPlanVectorModel) {
    checks.push({
      id: "final-vector-model-missing",
      severity: "info",
      title: "Final 2D plan still needs mapping",
      details: ["This design is still using the current 2D wall model until its detailed plan is drawn."],
    });
  }

  if (input.layoutSource === "saved") {
    checks.push({
      id: "saved-layout-may-be-stale",
      severity: "info",
      title: "Saved furniture may need a fresh pass",
      details: ["This view is using a saved layout, so it may predate the latest scenario seed or wall changes."],
    });
  }

  const overlapDetails = findOverlaps(input.layout.objects);
  if (overlapDetails.length > 0) {
    checks.push({
      id: "furniture-overlap",
      severity: "warning",
      title: "Furniture overlaps need review",
      details: overlapDetails.slice(0, 6),
    });
  }

  if (finalVectorModelAvailable) {
    const outsideDetails = findObjectsOutsideRooms(input.layout, roomBoundsForScenario(input.scenarioId));
    if (outsideDetails.length > 0) {
      checks.push({
        id: "furniture-outside-proposed-rooms",
        severity: "warning",
        title: "Furniture sits outside the proposed room layout",
        details: outsideDetails.slice(0, 6),
      });
    }
  }

  return checks;
}
