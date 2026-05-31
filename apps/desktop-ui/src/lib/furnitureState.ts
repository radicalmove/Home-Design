import type {
  FurnitureCatalogItem,
  FurnitureLayerKind,
  FurnitureLShapeDimensions,
  FurnitureLayout,
  FurnitureObject,
  PlanPoint,
} from "../types";
import { normaliseDegrees } from "./furnitureGeometry";

type FurnitureSize = {
  width_m: number;
  depth_m: number;
  l_shape?: FurnitureLShapeDimensions | null;
};

const DEFAULT_L_SHAPES: Record<string, FurnitureLShapeDimensions> = {
  l_sofa: { main_depth_m: 0.9, return_width_m: 1.05 },
  l_desk: { main_depth_m: 0.65, return_width_m: 0.65 },
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

function normaliseLShapeDimensions(
  lShape: FurnitureLShapeDimensions | null | undefined,
  widthM: number,
  depthM: number,
): FurnitureLShapeDimensions | undefined {
  if (!lShape) {
    return undefined;
  }

  return {
    main_depth_m: roundMetres(Math.min(depthM, Math.max(0.2, lShape.main_depth_m))),
    return_width_m: roundMetres(Math.min(widthM, Math.max(0.2, lShape.return_width_m))),
  };
}

function withLegacyLShapeDefaults(object: FurnitureObject): FurnitureObject {
  if (object.l_shape) {
    return object;
  }

  if (
    object.type === "l_sofa" ||
    object.catalog_id === "l_sofa" ||
    object.label.toLowerCase() === "l-shaped sofa" ||
    object.id === "lounge_sofa"
  ) {
    return {
      ...object,
      catalog_id: "l_sofa",
      type: "l_sofa",
      label: "L-shaped sofa",
      l_shape: DEFAULT_L_SHAPES.l_sofa,
    };
  }

  if (object.type === "l_desk" || object.catalog_id === "l_desk" || object.id === "office_desk") {
    return {
      ...object,
      catalog_id: "l_desk",
      type: "l_desk",
      label: object.label === "Office desk" ? "L-shaped desk" : object.label,
      l_shape: DEFAULT_L_SHAPES.l_desk,
    };
  }

  return object;
}

function normaliseFurnitureObject(object: FurnitureObject): FurnitureObject {
  const objectWithDefaults = withLegacyLShapeDefaults(object);
  const widthM = roundMetres(Math.max(0.2, objectWithDefaults.width_m));
  const depthM = roundMetres(Math.max(0.2, objectWithDefaults.depth_m));

  return {
    ...objectWithDefaults,
    x_m: roundMetres(objectWithDefaults.x_m),
    y_m: roundMetres(objectWithDefaults.y_m),
    width_m: widthM,
    depth_m: depthM,
    l_shape: normaliseLShapeDimensions(objectWithDefaults.l_shape, widthM, depthM),
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
    l_shape: normaliseLShapeDimensions(
      item.default_l_shape,
      item.default_width_m,
      item.default_depth_m,
    ),
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
    l_shape: normaliseLShapeDimensions(
      size.l_shape ?? object.l_shape,
      roundMetres(Math.max(0.2, size.width_m)),
      roundMetres(Math.max(0.2, size.depth_m)),
    ),
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

export function changeObjectLayer(
  layout: FurnitureLayout,
  objectId: string,
  layer: FurnitureLayerKind,
): FurnitureLayout {
  return updateObject(layout, objectId, (object) => ({
    ...object,
    layer,
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
