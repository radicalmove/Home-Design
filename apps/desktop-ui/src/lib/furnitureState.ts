import type { FurnitureCatalogItem, FurnitureLayout, FurnitureObject, PlanPoint } from "../types";
import { normaliseDegrees } from "./furnitureGeometry";

type FurnitureSize = {
  width_m: number;
  depth_m: number;
};

function roundMetres(value: number): number {
  return Math.round(value * 100) / 100;
}

function nextObjectId(existingIds: Set<string>, baseId: string): string {
  let index = 1;
  let candidate = `${baseId}-${index}`;
  while (existingIds.has(candidate)) {
    index += 1;
    candidate = `${baseId}-${index}`;
  }
  return candidate;
}

function updateObject(
  layout: FurnitureLayout,
  objectId: string,
  updater: (object: FurnitureObject) => FurnitureObject,
): FurnitureLayout {
  return {
    ...layout,
    objects: layout.objects.map((object) => (object.id === objectId ? updater(object) : object)),
  };
}

function normaliseFurnitureObject(object: FurnitureObject): FurnitureObject {
  return {
    ...object,
    x_m: roundMetres(object.x_m),
    y_m: roundMetres(object.y_m),
    width_m: roundMetres(Math.max(0.2, object.width_m)),
    depth_m: roundMetres(Math.max(0.2, object.depth_m)),
  };
}

export function normaliseFurnitureLayout(layout: FurnitureLayout): FurnitureLayout {
  return {
    ...layout,
    objects: layout.objects.map(normaliseFurnitureObject),
  };
}

export function addCatalogItem(
  layout: FurnitureLayout,
  item: FurnitureCatalogItem,
  point: PlanPoint,
): FurnitureLayout {
  const object: FurnitureObject = {
    id: nextObjectId(new Set(layout.objects.map(({ id }) => id)), item.id),
    catalog_id: item.id,
    layer: item.layer,
    type: item.type,
    label: item.label,
    abbreviation: item.abbreviation,
    x_m: point.x,
    y_m: point.y,
    width_m: item.default_width_m,
    depth_m: item.default_depth_m,
    rotation_deg: 0,
    colour: item.colour,
    locked: false,
    notes: null,
    evidence: null,
  };

  return {
    ...layout,
    objects: [...layout.objects, object],
  };
}

export function moveObject(layout: FurnitureLayout, objectId: string, point: PlanPoint): FurnitureLayout {
  return updateObject(layout, objectId, (object) => ({
    ...object,
    x_m: roundMetres(point.x),
    y_m: roundMetres(point.y),
  }));
}

export function resizeObject(
  layout: FurnitureLayout,
  objectId: string,
  size: FurnitureSize,
): FurnitureLayout {
  return updateObject(layout, objectId, (object) => ({
    ...object,
    width_m: roundMetres(Math.max(0.2, size.width_m)),
    depth_m: roundMetres(Math.max(0.2, size.depth_m)),
  }));
}

export function rotateObject(
  layout: FurnitureLayout,
  objectId: string,
  rotationDeg: number,
): FurnitureLayout {
  return updateObject(layout, objectId, (object) => ({
    ...object,
    rotation_deg: normaliseDegrees(rotationDeg),
  }));
}

export function recolourObject(
  layout: FurnitureLayout,
  objectId: string,
  colour: string,
): FurnitureLayout {
  return updateObject(layout, objectId, (object) => ({
    ...object,
    colour,
  }));
}

export function duplicateObject(layout: FurnitureLayout, objectId: string): FurnitureLayout {
  const source = layout.objects.find((object) => object.id === objectId);
  if (!source) {
    return layout;
  }

  const copy: FurnitureObject = {
    ...source,
    id: nextObjectId(new Set(layout.objects.map(({ id }) => id)), `${source.id}-copy`),
    x_m: source.x_m + 0.25,
    y_m: source.y_m + 0.25,
    locked: false,
  };

  return {
    ...layout,
    objects: [...layout.objects, copy],
  };
}

export function deleteObject(layout: FurnitureLayout, objectId: string): FurnitureLayout {
  return {
    ...layout,
    objects: layout.objects.filter((object) => object.id !== objectId),
  };
}
