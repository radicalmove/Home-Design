import type { DesignReviewData, FurnitureLShapeDimensions, FurnitureObject, PlanTransform } from "../../types";
import {
  sceneGeometryArea,
  sceneGeometryBoundsList,
  sceneGeometryCentre,
  sceneGeometryFromDisplayPx,
  type SceneBounds,
  type SceneGeometry,
  type ScenePoint,
} from "./geometry";
import { furniture3DDepthFor, furniture3DMetadataFor } from "./furniture3d";
import { defaultThreeDMaterials, type ThreeDMaterialPreset } from "./materials";
import { defaultPhotoViewpoints, type ThreeDPhotoViewpoint } from "./photoViewpoints";
import { buildMeasuredWallsFromRooms, buildPlanVectorWalls, type ThreeDWall } from "./walls";
import { houseModelForScenario, isScenarioHouseModelAvailable } from "../scenarioHouseModel";
import { planVectorModelForScenario } from "../planVectorModel";

export const HOUSE_FLOOR_ELEVATION_M = 0.3;
export type { ThreeDMaterialPreset } from "./materials";
export type { ThreeDPhotoViewpoint } from "./photoViewpoints";

export type ThreeDRoom = {
  id: string;
  name: string;
  category: string;
  confidence: string;
  geometry: SceneGeometry;
  centre: ScenePoint;
  areaM2: number;
  heightM: number;
  floorMaterial: string;
  wallMaterial: string;
  notes: string[];
};

export type ThreeDSiteElement = {
  id: string;
  type: string;
  category: string | null;
  geometry: SceneGeometry;
  centre: ScenePoint;
  material: string;
  heightM: number;
  elevationM: number;
};

export type ThreeDGroundPlane = {
  material: "lawn";
  xM: number;
  zM: number;
  widthM: number;
  depthM: number;
  elevationM: number;
};

export type ThreeDOpening = {
  id: string;
  type: string;
  swing: string | null;
  windowContext: string | null;
  room: string | null;
  between: string[];
  sourceWallId: string | null;
  heightM: number | null;
  geometry: SceneGeometry;
  centre: ScenePoint;
  material: string;
  anchor: ThreeDOpeningAnchor | null;
  anchors: ThreeDOpeningAnchor[];
  evidencePhotoPaths: string[];
};

export type ThreeDOpeningAnchor = {
  sourceWallId: string;
  sourceRoomIds: string[];
  segment: {
    x1: number;
    z1: number;
    x2: number;
    z2: number;
  };
  centre: ScenePoint;
  widthM: number;
  wallThicknessM: number;
};

export type ThreeDFurnitureItem = {
  id: string;
  catalogId: string | null;
  layer: FurnitureObject["layer"];
  type: string;
  label: string;
  abbreviation: string | null;
  xM: number;
  zM: number;
  widthM: number;
  depthM: number;
  heightM: number;
  rotationDeg: number;
  colour: string;
  locked: boolean;
  zIndex: number;
  lShape: FurnitureLShapeDimensions | null;
  material: string;
  shape: string;
  supportSurfaceHeightM: number;
};

export type ThreeDFoundationSegment = {
  id: string;
  x1: number;
  z1: number;
  x2: number;
  z2: number;
  heightM: number;
  thicknessM: number;
  exteriorFaceOffsetM: number;
  material: "foundationMasonry";
};

export type ThreeDFoundationConfig = {
  floorElevationM: number;
  pileHeightM: number;
  piles: ScenePoint[];
  exposedPiles: ScenePoint[];
  skirtSegments: ThreeDFoundationSegment[];
  hiddenByMasonry: boolean;
};

export type ThreeDStepTread = {
  id: string;
  sourceElementId: string;
  material: "deckTimber";
  xM: number;
  zM: number;
  widthM: number;
  depthM: number;
  heightM: number;
  elevationM: number;
  topElevationM: number;
  rotationDeg: number;
};

export type ThreeDDeckEdge = {
  id: string;
  sourceElementId: string;
  material: "deckTimber";
  x1: number;
  z1: number;
  x2: number;
  z2: number;
  heightM: number;
  thicknessM: number;
  topElevationM: number;
};

export type ThreeDSceneConfig = {
  units: "metres";
  floorElevationM: number;
  foundation: ThreeDFoundationConfig;
  rooms: ThreeDRoom[];
  walls: ThreeDWall[];
  groundPlane: ThreeDGroundPlane;
  site: ThreeDSiteElement[];
  deckEdges: ThreeDDeckEdge[];
  steps: ThreeDStepTread[];
  openings: ThreeDOpening[];
  furniture: ThreeDFurnitureItem[];
  materials: Record<string, ThreeDMaterialPreset>;
  photoViewpoints: ThreeDPhotoViewpoint[];
};

type JsonRecord = Record<string, unknown>;

const CARPET_ROOM_IDS = new Set(["lounge", "sunroom", "hallway", "master_bedroom", "office", "bedroom_2"]);
const VINYL_ROOM_IDS = new Set(["kitchen_dining", "entrance", "laundry", "toilet"]);
const TILE_ROOM_IDS = new Set(["bathroom"]);
const OPENING_TYPES = new Set(["window", "window_group", "slider", "sliding_door", "door_group", "door", "opening", "large_opening"]);
const GLAZING_TYPES = new Set(["window", "window_group", "slider", "door_group"]);
const FOUNDATION_SKIRT_EXCLUDED_ROOM_IDS = new Set(["sunroom"]);
const FOUNDATION_SKIRT_EXCLUDED_SITE_MATERIALS = new Set(["deckTimber"]);
const THREE_RAD_TO_DEG = 180 / Math.PI;

function asRecord(value: unknown): JsonRecord {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? value as JsonRecord
    : {};
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function asString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function asStringArray(value: unknown): string[] {
  return asArray(value).filter((item): item is string => typeof item === "string");
}

function roomMaterial(roomId: string, category: string): string {
  if (category === "built_in") {
    return "carpet";
  }
  if (category === "bedroom") {
    return "carpet";
  }
  if (TILE_ROOM_IDS.has(roomId) || category === "wet") {
    return "tile";
  }
  if (VINYL_ROOM_IDS.has(roomId)) {
    return "vinylPlank";
  }
  if (CARPET_ROOM_IDS.has(roomId)) {
    return "carpet";
  }
  return "vinylPlank";
}

function featureMaterial(feature: JsonRecord): string {
  const type = asString(feature.type);
  const id = asString(feature.id);
  return GLAZING_TYPES.has(type) || id.includes("glazing") ? "glazing" : "paintedWall";
}

function siteMaterial(element: JsonRecord): string {
  const category = asString(element.category || element.surface || element.type);
  const type = asString(element.type);
  if (category.includes("deck") || type.includes("deck")) {
    return "deckTimber";
  }
  if (
    category === "hardscape"
    || category === "driveway"
    || category === "concrete_pad"
    || category === "concrete_path"
    || type.includes("path")
    || type.includes("driveway")
  ) {
    return "concrete";
  }
  if (category === "building" || category === "accessory_cottage" || type === "outbuilding") {
    return "paintedWall";
  }
  return "lawn";
}

function siteHeight(material: string): number {
  if (material === "paintedWall") {
    return 2.7;
  }
  if (material === "deckTimber") {
    return 0.12;
  }
  if (material === "concrete") {
    return 0.06;
  }
  return 0.01;
}

function siteElevation(material: string): number {
  return material === "deckTimber" ? 0.28 : 0;
}

function displayGeometryMap(items: unknown[], transform: PlanTransform): Map<string, SceneGeometry> {
  const map = new Map<string, SceneGeometry>();
  for (const itemValue of items) {
    const item = asRecord(itemValue);
    const id = asString(item.id);
    const geometry = sceneGeometryFromDisplayPx(item.display_px, transform);
    if (id && geometry) {
      map.set(id, geometry);
    }
  }
  return map;
}

function buildRooms(model: JsonRecord, transform: PlanTransform): ThreeDRoom[] {
  const currentStructure = asRecord(model.current_structure);
  const spaceGeometry = displayGeometryMap(asArray(currentStructure.spaces), transform);
  const builtInGeometry = displayGeometryMap(asArray(currentStructure.built_ins), transform);
  const modelRooms = asArray(model.rooms).map(asRecord);
  const rooms: JsonRecord[] = modelRooms.length > 0
    ? modelRooms
    : asArray(currentStructure.spaces).map((space) => {
      const record = asRecord(space);
      return { ...record, name: asString(record.id), category: "unknown" };
    });

  const roomRecords = rooms.flatMap((room) => {
    const id = asString(room.id);
    const geometry = spaceGeometry.get(id) ?? sceneGeometryFromDisplayPx(room.display_px, transform);
    if (!id || !geometry) {
      return [];
    }

    const dimensions = asRecord(room.dimensions_m);
    return [
      {
        id,
        name: asString(room.name) || id,
        category: asString(room.category) || "unknown",
        confidence: asString(room.confidence) || "unknown",
        geometry,
        centre: sceneGeometryCentre(geometry),
        areaM2: sceneGeometryArea(geometry),
        heightM: asNumber(dimensions.height) ?? 2.4,
        floorMaterial: roomMaterial(id, asString(room.category)),
        wallMaterial: "paintedWall",
        notes: asStringArray(room.notes),
      },
    ];
  });

  const builtInRecords = asArray(currentStructure.built_ins).flatMap((builtInValue) => {
    const builtIn = asRecord(builtInValue);
    const id = asString(builtIn.id);
    const geometry = builtInGeometry.get(id) ?? sceneGeometryFromDisplayPx(builtIn.display_px, transform);
    if (!id || !geometry) {
      return [];
    }
    return [{
      id,
      name: asString(builtIn.name) || id,
      category: "built_in",
      confidence: asString(builtIn.status) || "unknown",
      geometry,
      centre: sceneGeometryCentre(geometry),
      areaM2: sceneGeometryArea(geometry),
      heightM: 2.4,
      floorMaterial: roomMaterial(id, "built_in"),
      wallMaterial: "paintedWall",
      notes: asStringArray(builtIn.notes),
    }];
  });

  return [...roomRecords, ...builtInRecords];
}

function openingSourceRecords(model: JsonRecord): JsonRecord[] {
  const features = asArray(asRecord(model.current_structure).features).map(asRecord);
  const featureIds = new Set(features.map((feature) => asString(feature.id)).filter(Boolean));
  const fallbackOpenings = asArray(model.openings)
    .map(asRecord)
    .filter((opening) => {
      const id = asString(opening.id);
      return id && !featureIds.has(id);
    });
  return [...features, ...fallbackOpenings];
}

function buildOpenings(model: JsonRecord, transform: PlanTransform): ThreeDOpening[] {
  return openingSourceRecords(model).flatMap((feature) => {
    const id = asString(feature.id);
    const type = asString(feature.type) || "feature";
    const geometry = sceneGeometryFromDisplayPx(feature.display_px, transform);
    if (!id || !geometry || !OPENING_TYPES.has(type)) {
      return [];
    }
    return [
      {
        id,
        type,
        swing: asString(feature.swing) || null,
        windowContext: asString(feature.window_context) || null,
        room: asString(feature.room) || null,
        between: asStringArray(feature.between),
        sourceWallId: asString(feature.wall_id) || null,
        heightM: asNumber(feature.height_m),
        geometry,
        centre: sceneGeometryCentre(geometry),
        material: featureMaterial(feature),
        anchor: null,
        anchors: [],
        evidencePhotoPaths: asStringArray(feature.evidence_photo_paths),
      },
    ];
  });
}

function buildSite(model: JsonRecord, transform: PlanTransform): ThreeDSiteElement[] {
  const siteElements = asArray(asRecord(model.current_site).elements);
  const fallbackElements = asArray(model.external_features);
  const elements = siteElements.length > 0 ? siteElements : fallbackElements;

  return elements.flatMap((elementValue) => {
    const element = asRecord(elementValue);
    const id = asString(element.id);
    const type = asString(element.type) || "site";
    const category = asString(element.category);
    if (type.includes("steps") || type === "boundary" || category === "boundary" || id === "property_boundary") {
      return [];
    }
    const geometry = sceneGeometryFromDisplayPx(element.display_px || element.layout, transform);
    if (!id || !geometry) {
      return [];
    }
    const material = siteMaterial(element);
    return [
      {
        id,
        type,
        category: asString(element.category) || null,
        geometry,
        centre: sceneGeometryCentre(geometry),
        material,
        heightM: siteHeight(material),
        elevationM: siteElevation(material),
      },
    ];
  });
}

function groundPlaneFromBounds(
  minX: number,
  maxX: number,
  minZ: number,
  maxZ: number,
  paddingM = 0,
): ThreeDGroundPlane {
  return {
    material: "lawn",
    xM: (minX + maxX) / 2,
    zM: (minZ + maxZ) / 2,
    widthM: Math.max(1, maxX - minX + paddingM * 2),
    depthM: Math.max(1, maxZ - minZ + paddingM * 2),
    elevationM: -0.035,
  };
}

function buildGroundPlane(model: JsonRecord, transform: PlanTransform, rooms: ThreeDRoom[], site: ThreeDSiteElement[]): ThreeDGroundPlane {
  const boundary = siteSourceElements(model).find((element) => {
    const id = asString(element.id);
    const type = asString(element.type);
    const category = asString(element.category);
    return id === "property_boundary" || type === "boundary" || category === "boundary";
  });
  const boundaryGeometry = boundary ? sceneGeometryFromDisplayPx(boundary.display_px || boundary.layout, transform) : null;
  const boundaryBounds = boundaryGeometry ? sceneGeometryBoundsList(boundaryGeometry) : [];
  if (boundaryBounds.length > 0) {
    return groundPlaneFromBounds(
      Math.min(...boundaryBounds.map((bounds) => bounds.minX)),
      Math.max(...boundaryBounds.map((bounds) => bounds.maxX)),
      Math.min(...boundaryBounds.map((bounds) => bounds.minZ)),
      Math.max(...boundaryBounds.map((bounds) => bounds.maxZ)),
    );
  }

  const fallbackBounds = [
    ...rooms.flatMap((room) => sceneGeometryBoundsList(room.geometry)),
    ...site.flatMap((siteElement) => sceneGeometryBoundsList(siteElement.geometry)),
  ];
  if (fallbackBounds.length === 0) {
    return groundPlaneFromBounds(-8, 20, -8, 16);
  }
  return groundPlaneFromBounds(
    Math.min(...fallbackBounds.map((bounds) => bounds.minX)),
    Math.max(...fallbackBounds.map((bounds) => bounds.maxX)),
    Math.min(...fallbackBounds.map((bounds) => bounds.minZ)),
    Math.max(...fallbackBounds.map((bounds) => bounds.maxZ)),
    4,
  );
}

function siteSourceElements(model: JsonRecord): JsonRecord[] {
  const siteElements = asArray(asRecord(model.current_site).elements);
  const fallbackElements = asArray(model.external_features);
  return (siteElements.length > 0 ? siteElements : fallbackElements).map(asRecord);
}

function geometryPolygons(geometry: SceneGeometry): ScenePoint[][] {
  if (geometry.type === "rect") {
    return [[
      { x: geometry.x, z: geometry.z },
      { x: geometry.x + geometry.width, z: geometry.z },
      { x: geometry.x + geometry.width, z: geometry.z + geometry.depth },
      { x: geometry.x, z: geometry.z + geometry.depth },
    ]];
  }
  return geometry.type === "polygon" ? [geometry.points] : geometry.polygons;
}

function averagePoint(points: ScenePoint[]): ScenePoint {
  return {
    x: points.reduce((sum, point) => sum + point.x, 0) / points.length,
    z: points.reduce((sum, point) => sum + point.z, 0) / points.length,
  };
}

function wallSegmentLength(segment: ThreeDWall["segments"][number]): number {
  return Math.hypot(segment.x2 - segment.x1, segment.z2 - segment.z1);
}

function nearestPointOnSegment(
  point: ScenePoint,
  segment: ThreeDWall["segments"][number],
): { point: ScenePoint; t: number; distanceM: number } {
  const dx = segment.x2 - segment.x1;
  const dz = segment.z2 - segment.z1;
  const lengthSquared = dx * dx + dz * dz;
  if (lengthSquared <= 0.000001) {
    return {
      point: { x: segment.x1, z: segment.z1 },
      t: 0,
      distanceM: Math.hypot(point.x - segment.x1, point.z - segment.z1),
    };
  }
  const rawT = ((point.x - segment.x1) * dx + (point.z - segment.z1) * dz) / lengthSquared;
  const t = Math.max(0, Math.min(1, rawT));
  const projected = {
    x: segment.x1 + dx * t,
    z: segment.z1 + dz * t,
  };
  return {
    point: projected,
    t,
    distanceM: Math.hypot(point.x - projected.x, point.z - projected.z),
  };
}

function anchorSegmentAroundCentre(
  segment: ThreeDWall["segments"][number],
  centre: ScenePoint,
  widthM: number,
): ThreeDOpeningAnchor["segment"] {
  const length = wallSegmentLength(segment);
  if (length <= 0.001) {
    return { ...segment };
  }
  const dx = (segment.x2 - segment.x1) / length;
  const dz = (segment.z2 - segment.z1) / length;
  const halfWidth = Math.min(widthM / 2, Math.max(0.05, length / 2));
  return {
    x1: centre.x - dx * halfWidth,
    z1: centre.z - dz * halfWidth,
    x2: centre.x + dx * halfWidth,
    z2: centre.z + dz * halfWidth,
  };
}

function openingBoundsCentre(bounds: SceneBounds): ScenePoint {
  return {
    x: (bounds.minX + bounds.maxX) / 2,
    z: (bounds.minZ + bounds.maxZ) / 2,
  };
}

type OpeningPanelDescriptor = {
  centre: ScenePoint;
  widthM: number;
  angleRad: number | null;
};

function boundsPanelDescriptor(bounds: SceneBounds): OpeningPanelDescriptor {
  const width = bounds.maxX - bounds.minX;
  const depth = bounds.maxZ - bounds.minZ;
  return {
    centre: openingBoundsCentre(bounds),
    widthM: Math.max(width, depth),
    angleRad: depth > width ? Math.PI / 2 : 0,
  };
}

function polygonPanelDescriptor(points: ScenePoint[]): OpeningPanelDescriptor | null {
  if (points.length < 2) {
    return null;
  }
  const longestEdge = points.map((point, index) => {
    const next = points[(index + 1) % points.length];
    return {
      start: point,
      end: next,
      length: Math.hypot(next.x - point.x, next.z - point.z),
    };
  }).sort((left, right) => right.length - left.length)[0];
  if (!longestEdge) {
    return null;
  }
  return {
    centre: averagePoint(points),
    widthM: longestEdge.length,
    angleRad: Math.atan2(longestEdge.end.z - longestEdge.start.z, longestEdge.end.x - longestEdge.start.x),
  };
}

function openingPanelDescriptors(geometry: SceneGeometry): OpeningPanelDescriptor[] {
  if (geometry.type === "rect") {
    return sceneGeometryBoundsList(geometry).map(boundsPanelDescriptor);
  }
  if (geometry.type === "polygon") {
    const descriptor = polygonPanelDescriptor(geometry.points);
    return descriptor ? [descriptor] : [];
  }
  return geometry.polygons
    .map(polygonPanelDescriptor)
    .filter((descriptor): descriptor is OpeningPanelDescriptor => descriptor !== null);
}

function angleDifference(left: number, right: number): number {
  const difference = Math.abs(Math.atan2(Math.sin(left - right), Math.cos(left - right)));
  return Math.min(difference, Math.abs(Math.PI - difference));
}

function relevantWallsForOpening(opening: ThreeDOpening, walls: ThreeDWall[]): ThreeDWall[] {
  const roomIds = new Set([opening.room, ...opening.between].filter((roomId): roomId is string => Boolean(roomId)));
  const roomWalls = walls.filter((wall) => wall.sourceRoomIds.some((roomId) => roomIds.has(roomId)));
  return roomWalls.length > 0 ? roomWalls : walls;
}

function anchorOpeningBoundsToWallFromCandidates(
  opening: ThreeDOpening,
  descriptor: OpeningPanelDescriptor,
  wallCandidates: ThreeDWall[],
  requestedWidthM: number | null,
): ThreeDOpeningAnchor | null {
  const nearest = wallCandidates.flatMap((wall) => wall.segments.map((segment) => ({
    wall,
    segment,
    projection: nearestPointOnSegment(descriptor.centre, segment),
    angleScore: descriptor.angleRad === null
      ? 0
      : angleDifference(descriptor.angleRad, Math.atan2(segment.z2 - segment.z1, segment.x2 - segment.x1)) * 0.45,
  }))).sort((left, right) => {
    const leftScore = left.projection.distanceM + left.angleScore;
    const rightScore = right.projection.distanceM + right.angleScore;
    return leftScore - rightScore;
  })[0];

  if (!nearest) {
    return null;
  }

  const widthM = Math.max(0.12, requestedWidthM ?? descriptor.widthM);
  return {
    sourceWallId: nearest.wall.id,
    sourceRoomIds: nearest.wall.sourceRoomIds,
    segment: anchorSegmentAroundCentre(nearest.segment, nearest.projection.point, widthM),
    centre: nearest.projection.point,
    widthM,
    wallThicknessM: nearest.wall.thicknessM,
  };
}

function anchorOpeningBoundsToWall(
  opening: ThreeDOpening,
  descriptor: OpeningPanelDescriptor,
  walls: ThreeDWall[],
  requestedWidthM: number | null,
): ThreeDOpeningAnchor | null {
  const requestedWall = opening.sourceWallId
    ? walls.find((wall) => wall.id === opening.sourceWallId)
    : null;
  if (requestedWall) {
    return anchorOpeningBoundsToWallFromCandidates(opening, descriptor, [requestedWall], requestedWidthM);
  }
  return anchorOpeningBoundsToWallFromCandidates(
    opening,
    descriptor,
    relevantWallsForOpening(opening, walls),
    requestedWidthM,
  );
}

function uniqueOpeningAnchors(anchors: ThreeDOpeningAnchor[]): ThreeDOpeningAnchor[] {
  const seen = new Set<string>();
  return anchors.filter((anchor) => {
    const key = `${anchor.sourceWallId}:${anchor.centre.x.toFixed(3)}:${anchor.centre.z.toFixed(3)}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function formerExternalOpeningAnchors(
  opening: ThreeDOpening,
  descriptor: OpeningPanelDescriptor,
  walls: ThreeDWall[],
  requestedWidthM: number | null,
): ThreeDOpeningAnchor[] {
  const roomIds = [opening.room, "sunroom"].filter((roomId): roomId is string => Boolean(roomId));
  const anchors = roomIds.flatMap((roomId) => {
    const roomWalls = walls.filter((wall) => wall.sourceRoomIds.includes(roomId));
    const anchor = anchorOpeningBoundsToWallFromCandidates(opening, descriptor, roomWalls, requestedWidthM);
    return anchor ? [anchor] : [];
  });
  return uniqueOpeningAnchors(anchors);
}

function withWallAnchoredOpenings(openings: ThreeDOpening[], walls: ThreeDWall[], model: JsonRecord): ThreeDOpening[] {
  const featureWidths = new Map<string, number>();
  openingSourceRecords(model).forEach((feature) => {
    const id = asString(feature.id);
    const width = asNumber(feature.width_m);
    if (id && width !== null) {
      featureWidths.set(id, width);
    }
  });

  return openings.map((opening) => {
    const descriptors = openingPanelDescriptors(opening.geometry);
    const requestedWidth = descriptors.length === 1 ? featureWidths.get(opening.id) ?? null : null;
    const anchors = descriptors
      .flatMap((descriptor) => opening.windowContext === "former_external"
        ? formerExternalOpeningAnchors(opening, descriptor, walls, requestedWidth)
        : [anchorOpeningBoundsToWall(opening, descriptor, walls, requestedWidth)])
      .filter((anchor): anchor is ThreeDOpeningAnchor => anchor !== null);
    return {
      ...opening,
      anchor: anchors[0] ?? null,
      anchors,
    };
  });
}

function roomBoundsById(rooms: ThreeDRoom[]): Map<string, SceneBounds> {
  return new Map(rooms.flatMap((room) => {
    const bounds = sceneGeometryBoundsList(room.geometry)[0];
    return bounds ? [[room.id, bounds] as const] : [];
  }));
}

function supplementalMeasuredWalls(rooms: ThreeDRoom[], existingWalls: ThreeDWall[]): ThreeDWall[] {
  const bounds = roomBoundsById(rooms);
  const bedroom2 = bounds.get("bedroom_2");
  const laundry = bounds.get("laundry");
  const alreadyHasLaundryBedroomWall = existingWalls.some((wall) => (
    wall.sourceRoomIds.includes("bedroom_2")
    && wall.sourceRoomIds.includes("laundry")
  ));
  if (!bedroom2 || !laundry || alreadyHasLaundryBedroomWall) {
    return [];
  }

  const z1 = Math.max(bedroom2.minZ, laundry.minZ);
  const z2 = Math.min(bedroom2.maxZ, laundry.maxZ);
  if (z2 - z1 < 0.25) {
    return [];
  }
  const x = (bedroom2.maxX + laundry.minX) / 2;
  return [{
    id: "repair-wall:laundry-bedroom-2",
    class: "interior",
    pixelPath: "",
    sourceRoomIds: ["bedroom_2", "laundry"],
    segments: [{ x1: x, z1, x2: x, z2 }],
    heightM: 2.35,
    thicknessM: 0.1,
    material: "paintedWall",
  }];
}

function openingAnchorGeometry(anchor: ThreeDOpeningAnchor): SceneGeometry {
  const dx = anchor.segment.x2 - anchor.segment.x1;
  const dz = anchor.segment.z2 - anchor.segment.z1;
  const length = Math.hypot(dx, dz);
  if (length <= 0.001) {
    return {
      type: "rect",
      x: anchor.centre.x - anchor.widthM / 2,
      z: anchor.centre.z - anchor.wallThicknessM / 2,
      width: anchor.widthM,
      depth: anchor.wallThicknessM,
    };
  }
  const normal = {
    x: -dz / length,
    z: dx / length,
  };
  const halfDepth = Math.max(anchor.wallThicknessM, 0.08) / 2;
  return {
    type: "polygon",
    points: [
      { x: anchor.segment.x1 + normal.x * halfDepth, z: anchor.segment.z1 + normal.z * halfDepth },
      { x: anchor.segment.x2 + normal.x * halfDepth, z: anchor.segment.z2 + normal.z * halfDepth },
      { x: anchor.segment.x2 - normal.x * halfDepth, z: anchor.segment.z2 - normal.z * halfDepth },
      { x: anchor.segment.x1 - normal.x * halfDepth, z: anchor.segment.z1 - normal.z * halfDepth },
    ],
  };
}

function syntheticOpeningFromTopLevelRecord(record: JsonRecord, walls: ThreeDWall[]): ThreeDOpening | null {
  const id = asString(record.id);
  const type = asString(record.type);
  const between = asStringArray(record.between);
  if (!id || !OPENING_TYPES.has(type) || between.length < 2) {
    return null;
  }

  const matchingWall = walls
    .filter((wall) => between.every((roomId) => wall.sourceRoomIds.includes(roomId)))
    .sort((left, right) => {
      const leftLength = Math.max(...left.segments.map(wallSegmentLength));
      const rightLength = Math.max(...right.segments.map(wallSegmentLength));
      return rightLength - leftLength;
    })[0];
  const segment = matchingWall?.segments
    .filter((candidate) => wallSegmentLength(candidate) > 0.1)
    .sort((left, right) => wallSegmentLength(right) - wallSegmentLength(left))[0];
  if (!matchingWall || !segment) {
    return null;
  }

  const centre = {
    x: (segment.x1 + segment.x2) / 2,
    z: (segment.z1 + segment.z2) / 2,
  };
  const widthM = Math.max(0.3, Math.min(asNumber(record.width_m) ?? 1.2, wallSegmentLength(segment) - 0.08));
  const anchor: ThreeDOpeningAnchor = {
    sourceWallId: matchingWall.id,
    sourceRoomIds: matchingWall.sourceRoomIds,
    segment: anchorSegmentAroundCentre(segment, centre, widthM),
    centre,
    widthM,
    wallThicknessM: matchingWall.thicknessM,
  };
  const geometry = openingAnchorGeometry(anchor);
  return {
    id,
    type,
    swing: asString(record.swing) || null,
    windowContext: asString(record.window_context) || null,
    room: asString(record.room) || null,
    between,
    sourceWallId: asString(record.wall_id) || null,
    heightM: asNumber(record.height_m),
    geometry,
    centre: sceneGeometryCentre(geometry),
    material: featureMaterial(record),
    anchor,
    anchors: [anchor],
    evidencePhotoPaths: asStringArray(record.evidence_photo_paths),
  };
}

function withSyntheticTopLevelOpenings(openings: ThreeDOpening[], walls: ThreeDWall[], model: JsonRecord): ThreeDOpening[] {
  const openingIds = new Set(openings.map((opening) => opening.id));
  const syntheticOpenings = asArray(model.openings)
    .map(asRecord)
    .filter((record) => !openingIds.has(asString(record.id)))
    .map((record) => syntheticOpeningFromTopLevelRecord(record, walls))
    .filter((opening): opening is ThreeDOpening => opening !== null);
  return [...openings, ...syntheticOpenings];
}

function orientedStepFromPolygon(
  sourceElementId: string,
  points: ScenePoint[],
  index: number,
  topElevationM: number,
): ThreeDStepTread | null {
  if (points.length < 3) {
    return null;
  }

  const edges = points.map((point, pointIndex) => {
    const next = points[(pointIndex + 1) % points.length];
    return {
      start: point,
      end: next,
      length: Math.hypot(next.x - point.x, next.z - point.z),
    };
  }).sort((left, right) => right.length - left.length);
  const longEdge = edges[0];
  if (!longEdge || longEdge.length <= 0.05) {
    return null;
  }

  const angle = Math.atan2(longEdge.end.z - longEdge.start.z, longEdge.end.x - longEdge.start.x);
  const normalAngle = angle + Math.PI / 2;
  const normalValues = points.map((point) => point.x * Math.cos(normalAngle) + point.z * Math.sin(normalAngle));
  const heightM = 0.065;
  return {
    id: `${sourceElementId}:tread:${index + 1}`,
    sourceElementId,
    material: "deckTimber",
    xM: averagePoint(points).x,
    zM: averagePoint(points).z,
    widthM: longEdge.length,
    depthM: Math.max(0.16, Math.max(...normalValues) - Math.min(...normalValues)),
    heightM,
    elevationM: Math.max(0.015, topElevationM - heightM),
    topElevationM,
    rotationDeg: THREE_RAD_TO_DEG * angle,
  };
}

function buildTimberStepTreads(sourceElementId: string, geometry: SceneGeometry): ThreeDStepTread[] {
  const polygons = geometryPolygons(geometry);
  return polygons
    .map((points, index) => orientedStepFromPolygon(
      sourceElementId,
      points,
      index,
      Math.max(0.09, HOUSE_FLOOR_ELEVATION_M - index * 0.075),
    ))
    .filter((step): step is ThreeDStepTread => step !== null);
}

function buildRearDeckEdgeSteps(sourceElementId: string, geometry: SceneGeometry): ThreeDStepTread[] {
  const polygon = geometryPolygons(geometry)[0];
  if (!polygon || polygon.length < 3) {
    return [];
  }
  const centre = averagePoint(polygon);
  const candidate = polygon.map((point, index) => {
    const next = polygon[(index + 1) % polygon.length];
    const length = Math.hypot(next.x - point.x, next.z - point.z);
    return { start: point, end: next, length };
  }).filter((edge) => {
    const dx = Math.abs(edge.end.x - edge.start.x);
    const dz = Math.abs(edge.end.z - edge.start.z);
    return edge.length >= 0.45 && edge.length <= 1.35 && dx > 0.1 && dz > 0.1;
  }).sort((left, right) => left.length - right.length)[0];

  if (!candidate) {
    return [];
  }

  const midpoint = {
    x: (candidate.start.x + candidate.end.x) / 2,
    z: (candidate.start.z + candidate.end.z) / 2,
  };
  const angle = Math.atan2(candidate.end.z - candidate.start.z, candidate.end.x - candidate.start.x);
  const normalA = { x: -Math.sin(angle), z: Math.cos(angle) };
  const normalB = { x: Math.sin(angle), z: -Math.cos(angle) };
  const distanceA = Math.hypot(midpoint.x + normalA.x * 0.2 - centre.x, midpoint.z + normalA.z * 0.2 - centre.z);
  const distanceB = Math.hypot(midpoint.x + normalB.x * 0.2 - centre.x, midpoint.z + normalB.z * 0.2 - centre.z);
  const outward = distanceA >= distanceB ? normalA : normalB;
  const heightM = 0.06;
  return [0.22, 0.14, 0.06].map((topElevationM, index) => ({
    id: `${sourceElementId}:outer-step:${index + 1}`,
    sourceElementId,
    material: "deckTimber" as const,
    xM: midpoint.x + outward.x * (0.18 + index * 0.32),
    zM: midpoint.z + outward.z * (0.18 + index * 0.32),
    widthM: candidate.length,
    depthM: 0.32,
    heightM,
    elevationM: topElevationM - heightM,
    topElevationM,
    rotationDeg: THREE_RAD_TO_DEG * angle,
  }));
}

function buildDeckEdges(model: JsonRecord, transform: PlanTransform): ThreeDDeckEdge[] {
  return siteSourceElements(model).flatMap((element) => {
    const id = asString(element.id);
    const geometry = sceneGeometryFromDisplayPx(element.display_px || element.layout, transform);
    if (!id || !geometry || siteMaterial(element) !== "deckTimber") {
      return [];
    }
    const topElevationM = siteElevation("deckTimber");
    const heightM = 0.18;
    const thicknessM = 0.09;
    return geometryPolygons(geometry).flatMap((points, polygonIndex) => {
      return points.map((point, pointIndex): ThreeDDeckEdge => {
        const next = points[(pointIndex + 1) % points.length];
        return {
          id: `${id}:fascia:${polygonIndex}:${pointIndex}`,
          sourceElementId: id,
          material: "deckTimber",
          x1: point.x,
          z1: point.z,
          x2: next.x,
          z2: next.z,
          heightM,
          thicknessM,
          topElevationM,
        };
      });
    });
  });
}

function buildSteps(model: JsonRecord, transform: PlanTransform): ThreeDStepTread[] {
  return siteSourceElements(model).flatMap((element) => {
    const id = asString(element.id);
    const type = asString(element.type);
    const geometry = sceneGeometryFromDisplayPx(element.display_px || element.layout, transform);
    if (!id || !geometry) {
      return [];
    }
    if (type.includes("steps")) {
      return buildTimberStepTreads(id, geometry);
    }
    if (id === "rear_timber_deck") {
      return buildRearDeckEdgeSteps(id, geometry);
    }
    return [];
  });
}

function furnitureFootprintContains(
  support: FurnitureObject,
  object: FurnitureObject,
  marginM: number,
): boolean {
  return object.x_m >= support.x_m - support.width_m / 2 - marginM
    && object.x_m <= support.x_m + support.width_m / 2 + marginM
    && object.y_m >= support.y_m - support.depth_m / 2 - marginM
    && object.y_m <= support.y_m + support.depth_m / 2 + marginM;
}

function furnitureSupportSurfaceHeight(object: FurnitureObject, objects: FurnitureObject[]): number {
  if (object.type !== "tv") {
    return 0;
  }
  const support = objects.find((candidate) => (
    candidate.id !== object.id
    && ["dresser_drawers", "cabinet"].includes(candidate.type)
    && furnitureFootprintContains(candidate, object, 0.18)
  ));
  return support ? furniture3DMetadataFor(support.type).heightM : 0;
}

function buildFurniture(objects: FurnitureObject[]): ThreeDFurnitureItem[] {
  return [...objects]
    .sort((left, right) => left.z_index - right.z_index)
    .map((object) => {
      const metadata = furniture3DMetadataFor(object.type);
      return {
        id: object.id,
        catalogId: object.catalog_id,
        layer: object.layer,
        type: object.type,
        label: object.label,
        abbreviation: object.abbreviation,
        xM: object.x_m,
        zM: object.y_m,
        widthM: object.width_m,
        depthM: furniture3DDepthFor(object),
        heightM: metadata.heightM,
        rotationDeg: object.rotation_deg,
        colour: object.colour,
        locked: object.locked,
        zIndex: object.z_index,
        lShape: object.l_shape ?? null,
        material: metadata.material,
        shape: metadata.shape,
        supportSurfaceHeightM: furnitureSupportSurfaceHeight(object, objects),
      };
    });
}

function segmentIntersectsBounds(
  segment: { x1: number; z1: number; x2: number; z2: number },
  bounds: { minX: number; maxX: number; minZ: number; maxZ: number },
  marginM = 0,
): boolean {
  const minX = Math.min(segment.x1, segment.x2);
  const maxX = Math.max(segment.x1, segment.x2);
  const minZ = Math.min(segment.z1, segment.z2);
  const maxZ = Math.max(segment.z1, segment.z2);
  return maxX >= bounds.minX - marginM
    && minX <= bounds.maxX + marginM
    && maxZ >= bounds.minZ - marginM
    && minZ <= bounds.maxZ + marginM;
}

function rectangularFoundationSegments(
  minX: number,
  maxX: number,
  minZ: number,
  maxZ: number,
): ThreeDFoundationSegment[] {
  return [
    {
      id: "foundation:north-skirt",
      x1: minX,
      z1: minZ,
      x2: maxX,
      z2: minZ,
      heightM: HOUSE_FLOOR_ELEVATION_M,
      thicknessM: 0.12,
      exteriorFaceOffsetM: 0.06,
      material: "foundationMasonry",
    },
    {
      id: "foundation:east-skirt",
      x1: maxX,
      z1: minZ,
      x2: maxX,
      z2: maxZ,
      heightM: HOUSE_FLOOR_ELEVATION_M,
      thicknessM: 0.12,
      exteriorFaceOffsetM: 0.06,
      material: "foundationMasonry",
    },
    {
      id: "foundation:south-skirt",
      x1: maxX,
      z1: maxZ,
      x2: minX,
      z2: maxZ,
      heightM: HOUSE_FLOOR_ELEVATION_M,
      thicknessM: 0.12,
      exteriorFaceOffsetM: 0.06,
      material: "foundationMasonry",
    },
    {
      id: "foundation:west-skirt",
      x1: minX,
      z1: maxZ,
      x2: minX,
      z2: minZ,
      heightM: HOUSE_FLOOR_ELEVATION_M,
      thicknessM: 0.12,
      exteriorFaceOffsetM: 0.06,
      material: "foundationMasonry",
    },
  ];
}

function curatedFoundationSegments(
  rooms: ThreeDRoom[],
  walls: ThreeDWall[],
  site: ThreeDSiteElement[],
): ThreeDFoundationSegment[] {
  const excludedRoomBounds = rooms
    .filter((room) => FOUNDATION_SKIRT_EXCLUDED_ROOM_IDS.has(room.id))
    .flatMap((room) => sceneGeometryBoundsList(room.geometry));
  const excludedSiteBounds = site
    .filter((siteElement) => FOUNDATION_SKIRT_EXCLUDED_SITE_MATERIALS.has(siteElement.material))
    .flatMap((siteElement) => sceneGeometryBoundsList(siteElement.geometry));
  const excludedBounds = [...excludedRoomBounds, ...excludedSiteBounds];

  return walls.flatMap((wall) => {
    if (!wall.class.includes("exterior")) {
      return [];
    }
    return wall.segments.flatMap((segment, index) => {
      const length = Math.hypot(segment.x2 - segment.x1, segment.z2 - segment.z1);
      if (length <= 0.16 || excludedBounds.some((bounds) => segmentIntersectsBounds(segment, bounds, 0.08))) {
        return [];
      }
      return [{
        id: `foundation:${wall.id}:${index}`,
        ...segment,
        heightM: HOUSE_FLOOR_ELEVATION_M,
        thicknessM: 0.12,
        exteriorFaceOffsetM: 0.06,
        material: "foundationMasonry" as const,
      }];
    });
  });
}

function buildFoundation(rooms: ThreeDRoom[], walls: ThreeDWall[], site: ThreeDSiteElement[]): ThreeDFoundationConfig {
  const roomBounds = rooms.flatMap((room) => {
    if (!FOUNDATION_SKIRT_EXCLUDED_ROOM_IDS.has(room.id) && room.geometry.type === "rect") {
      return [{
        minX: room.geometry.x,
        maxX: room.geometry.x + room.geometry.width,
        minZ: room.geometry.z,
        maxZ: room.geometry.z + room.geometry.depth,
      }];
    }
    return [];
  });

  if (roomBounds.length === 0) {
    return {
      floorElevationM: HOUSE_FLOOR_ELEVATION_M,
      pileHeightM: HOUSE_FLOOR_ELEVATION_M,
      piles: [],
      exposedPiles: [],
      skirtSegments: [],
      hiddenByMasonry: true,
    };
  }

  const minX = Math.min(...roomBounds.map((bounds) => bounds.minX));
  const maxX = Math.max(...roomBounds.map((bounds) => bounds.maxX));
  const minZ = Math.min(...roomBounds.map((bounds) => bounds.minZ));
  const maxZ = Math.max(...roomBounds.map((bounds) => bounds.maxZ));
  const skirtSegments = curatedFoundationSegments(rooms, walls, site);
  const spacing = 1.5;
  const piles: ScenePoint[] = [];
  for (let x = minX; x <= maxX + 0.01; x += spacing) {
    piles.push({ x, z: minZ }, { x, z: maxZ });
  }
  for (let z = minZ + spacing; z < maxZ - 0.01; z += spacing) {
    piles.push({ x: minX, z }, { x: maxX, z });
  }

  return {
    floorElevationM: HOUSE_FLOOR_ELEVATION_M,
    pileHeightM: HOUSE_FLOOR_ELEVATION_M,
    piles,
    exposedPiles: [],
    hiddenByMasonry: true,
    skirtSegments: skirtSegments.length > 0 ? skirtSegments : rectangularFoundationSegments(minX, maxX, minZ, maxZ),
  };
}

export function buildThreeDSceneConfig(data: DesignReviewData): ThreeDSceneConfig {
  const transform = data.furniture_layout.layout.plan_transform;
  const scenarioId = data.furniture_layout.layout.scenario_id;
  const model = houseModelForScenario(
    data.house_model,
    scenarioId,
    transform.px_per_m,
  );
  const rooms = buildRooms(model, transform);
  const site = buildSite(model, transform);
  const scenarioWalls = isScenarioHouseModelAvailable(scenarioId)
    ? buildPlanVectorWalls(transform, planVectorModelForScenario(scenarioId).walls)
    : [];
  const measuredWalls = scenarioWalls.length > 0 ? [] : buildMeasuredWallsFromRooms(rooms.map((room) => ({
    id: room.id,
    geometry: room.geometry,
  })));
  const walls = scenarioWalls.length > 0
    ? scenarioWalls
    : [
        ...measuredWalls,
        ...supplementalMeasuredWalls(rooms, measuredWalls),
      ];
  const openings = withSyntheticTopLevelOpenings(
    withWallAnchoredOpenings(buildOpenings(model, transform), walls, model),
    walls,
    model,
  );
  const groundPlane = buildGroundPlane(model, transform, rooms, site);
  const deckEdges = buildDeckEdges(model, transform);

  return {
    units: "metres",
    floorElevationM: HOUSE_FLOOR_ELEVATION_M,
    foundation: buildFoundation(rooms, walls, site),
    rooms,
    walls,
    groundPlane,
    site,
    deckEdges,
    steps: buildSteps(model, transform),
    openings,
    furniture: buildFurniture(data.furniture_layout.layout.objects),
    materials: defaultThreeDMaterials,
    photoViewpoints: defaultPhotoViewpoints,
  };
}
