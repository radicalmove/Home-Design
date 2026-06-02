import { svgToMetres } from "./furnitureGeometry";
import type { DesignReviewData, FurnitureLayout, FurnitureObject, PlanPoint, PlanTransform } from "../types";

type JsonRecord = Record<string, unknown>;

type Geometry =
  | { type: "rect"; x: number; y: number; width: number; height: number }
  | { type: "polygon"; points: number[][] }
  | { type: "multi_polygon"; polygons: number[][][] };

export type ReviewSeverity = "good" | "watch" | "problem";

export type AssignedFurnitureObject = FurnitureObject & {
  roomId: string | null;
};

export type ReviewRoom = {
  id: string;
  name: string;
  category: string;
  dimensionsLabel: string;
  daylightSummary: string;
  objects: AssignedFurnitureObject[];
  fixedCount: number;
  moveableCount: number;
  notes: string[];
};

export type DesignReviewMetrics = {
  totalFurnitureObjects: number;
  fixedFurnitureObjects: number;
  moveableFurnitureObjects: number;
  roomCount: number;
  lowWinterLightRooms: string[];
  savedLayoutSource: "seed" | "saved";
};

export type DesignReviewWarning = {
  id: string;
  severity: ReviewSeverity;
  title: string;
  body: string;
};

export type DesignReviewReportSection = {
  id: string;
  title: string;
  summary: string;
  points: string[];
};

export type DesignReviewSnippet = {
  id: string;
  title: string;
  body: string;
  viewBox: string;
  focusRoomIds: string[];
  highlightObjectIds: string[];
};

export type DesignReviewPhotoEvidence = {
  id: string;
  summary: string;
  photos: Array<{
    path: string;
    view: string;
  }>;
};

export type DesignReviewAnalysis = {
  modelSource: string;
  layoutSource: "seed" | "saved";
  metrics: DesignReviewMetrics;
  rooms: ReviewRoom[];
  assignedObjects: AssignedFurnitureObject[];
  offPlanObjects: AssignedFurnitureObject[];
  unassignedObjects: AssignedFurnitureObject[];
  dynamicWarnings: DesignReviewWarning[];
  reportSections: DesignReviewReportSection[];
  snippets: DesignReviewSnippet[];
  photoEvidence: DesignReviewPhotoEvidence[];
};

type RoomGeometry = {
  id: string;
  geometry: Geometry;
};

const IMPORTANT_PHOTO_EVIDENCE_IDS = new Set([
  "deck_doors_and_kitchen_window",
  "lounge_photo_context",
  "sunroom_lounge_slider",
  "sunroom_wraparound_glazing",
  "hallway_spine_and_room_connections",
  "master_bedroom_photo_context",
  "bedroom2_photo_context",
  "entrance_laundry_back_entry",
  "toilet_laundry_connection",
]);

function asRecord(value: unknown): JsonRecord {
  return value && typeof value === "object" && !Array.isArray(value) ? value as JsonRecord : {};
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function roomNameById(model: JsonRecord): Map<string, string> {
  return new Map(
    asArray(model.rooms).map((roomValue) => {
      const room = asRecord(roomValue);
      const id = asString(room.id);
      return [id, asString(room.name, id)] as const;
    }).filter(([id]) => id.length > 0),
  );
}

function roomDefinitionById(model: JsonRecord): Map<string, JsonRecord> {
  return new Map(
    asArray(model.rooms).map((roomValue) => {
      const room = asRecord(roomValue);
      const id = asString(room.id);
      return [id, room] as const;
    }).filter(([id]) => id.length > 0),
  );
}

function geometryFromRecord(value: unknown): Geometry | null {
  const geometry = asRecord(value);
  const type = asString(geometry.type);
  if (type === "rect") {
    const x = asNumber(geometry.x);
    const y = asNumber(geometry.y);
    const width = asNumber(geometry.width);
    const height = asNumber(geometry.height);
    if (x !== null && y !== null && width !== null && height !== null) {
      return { type, x, y, width, height };
    }
  }
  if (type === "polygon") {
    const points = asArray(geometry.points).filter(Array.isArray) as number[][];
    if (points.length >= 3) {
      return { type, points };
    }
  }
  if (type === "multi_polygon") {
    const polygons = asArray(geometry.polygons).filter(Array.isArray) as number[][][];
    if (polygons.length > 0) {
      return { type, polygons };
    }
  }
  return null;
}

function roomGeometries(model: JsonRecord): RoomGeometry[] {
  const spaces = asArray(asRecord(model.current_structure).spaces);
  return spaces.flatMap((spaceValue) => {
    const space = asRecord(spaceValue);
    const id = asString(space.id);
    const geometry = geometryFromRecord(space.display_px);
    return id && geometry ? [{ id, geometry }] : [];
  });
}

function pointInPolygon(point: PlanPoint, polygon: PlanPoint[]): boolean {
  let inside = false;
  for (let index = 0, previous = polygon.length - 1; index < polygon.length; previous = index++) {
    const currentPoint = polygon[index];
    const previousPoint = polygon[previous];
    const intersects = currentPoint.y > point.y !== previousPoint.y > point.y
      && point.x < ((previousPoint.x - currentPoint.x) * (point.y - currentPoint.y))
        / (previousPoint.y - currentPoint.y)
        + currentPoint.x;
    if (intersects) {
      inside = !inside;
    }
  }
  return inside;
}

function svgPoint(point: number[], transform: PlanTransform): PlanPoint | null {
  const x = asNumber(point[0]);
  const y = asNumber(point[1]);
  return x === null || y === null ? null : svgToMetres({ x, y }, transform);
}

function geometryContainsPoint(geometry: Geometry, point: PlanPoint, transform: PlanTransform): boolean {
  if (geometry.type === "rect") {
    const topLeft = svgToMetres({ x: geometry.x, y: geometry.y }, transform);
    const bottomRight = svgToMetres(
      { x: geometry.x + geometry.width, y: geometry.y + geometry.height },
      transform,
    );
    return point.x >= Math.min(topLeft.x, bottomRight.x)
      && point.x <= Math.max(topLeft.x, bottomRight.x)
      && point.y >= Math.min(topLeft.y, bottomRight.y)
      && point.y <= Math.max(topLeft.y, bottomRight.y);
  }

  if (geometry.type === "polygon") {
    const points = geometry.points
      .map((rawPoint) => svgPoint(rawPoint, transform))
      .filter((rawPoint): rawPoint is PlanPoint => rawPoint !== null);
    return points.length >= 3 && pointInPolygon(point, points);
  }

  return geometry.polygons.some((polygon) => {
    const points = polygon
      .map((rawPoint) => svgPoint(rawPoint, transform))
      .filter((rawPoint): rawPoint is PlanPoint => rawPoint !== null);
    return points.length >= 3 && pointInPolygon(point, points);
  });
}

function isOffPlan(object: FurnitureObject, layout: FurnitureLayout): boolean {
  const transform = layout.plan_transform;
  const minX = -transform.origin_svg_px.x / transform.px_per_m;
  const minY = -transform.origin_svg_px.y / transform.px_per_m;
  const maxX = (transform.svg_width_px - transform.origin_svg_px.x) / transform.px_per_m;
  const maxY = (transform.svg_height_px - transform.origin_svg_px.y) / transform.px_per_m;
  const toleranceM = 1.2;
  return object.x_m < minX - toleranceM
    || object.x_m > maxX + toleranceM
    || object.y_m < minY - toleranceM
    || object.y_m > maxY + toleranceM;
}

function assignObjects(layout: FurnitureLayout, model: JsonRecord): AssignedFurnitureObject[] {
  const geometries = roomGeometries(model);
  return layout.objects.map((object) => {
    const point = { x: object.x_m, y: object.y_m };
    const room = geometries.find(({ geometry }) => geometryContainsPoint(geometry, point, layout.plan_transform));
    return { ...object, roomId: room?.id ?? null };
  });
}

function dimensionsLabel(room: JsonRecord): string {
  const dimensions = asRecord(room.dimensions_m);
  const length = asNumber(dimensions.length);
  const width = asNumber(dimensions.width);
  if (length !== null && width !== null) {
    return `${length.toFixed(2)} m x ${width.toFixed(2)} m`;
  }
  return "Irregular or partly measured";
}

function winterLightLevels(daylightRoom: JsonRecord): string[] {
  return Object.values(asRecord(daylightRoom.winter))
    .map((value) => asString(value))
    .filter((value) => value.length > 0);
}

function roomDaylightSummary(model: JsonRecord, roomId: string): string {
  const daylightRoom = asRecord(asRecord(asRecord(model.daylight).rooms)[roomId]);
  const winterLevels = winterLightLevels(daylightRoom);
  const notes = asString(daylightRoom.notes);
  if (winterLevels.length === 0) {
    return notes || "No daylight summary recorded yet.";
  }
  const lowCount = winterLevels.filter((level) => level === "low").length;
  const winterSummary = lowCount >= 2 ? "winter light is limited" : "winter light remains usable";
  return notes ? `${winterSummary}; ${notes}` : winterSummary;
}

function lowWinterLightRooms(model: JsonRecord, names: Map<string, string>): string[] {
  const daylightRooms = asRecord(asRecord(model.daylight).rooms);
  return Object.entries(daylightRooms).flatMap(([roomId, roomValue]) => {
    const levels = winterLightLevels(asRecord(roomValue));
    const lowCount = levels.filter((level) => level === "low").length;
    return levels.length > 0 && lowCount === levels.length ? [names.get(roomId) ?? roomId] : [];
  });
}

function buildRooms(model: JsonRecord, assignedObjects: AssignedFurnitureObject[]): ReviewRoom[] {
  const definitions = roomDefinitionById(model);
  const names = roomNameById(model);
  return roomGeometries(model).map(({ id }) => {
    const definition = definitions.get(id) ?? {};
    const objects = assignedObjects.filter((object) => object.roomId === id);
    return {
      id,
      name: names.get(id) ?? id,
      category: asString(definition.category, "unknown"),
      dimensionsLabel: dimensionsLabel(definition),
      daylightSummary: roomDaylightSummary(model, id),
      objects,
      fixedCount: objects.filter((object) => object.layer === "fixed").length,
      moveableCount: objects.filter((object) => object.layer === "moveable").length,
      notes: asArray(definition.notes).map((note) => asString(note)).filter(Boolean),
    };
  });
}

function warningForCrowdedTeenRoom(rooms: ReviewRoom[]): DesignReviewWarning | null {
  const bedroom2 = rooms.find((room) => room.id === "bedroom_2");
  if (!bedroom2 || bedroom2.objects.length < 7) {
    return null;
  }
  return {
    id: "bedroom-2-density",
    severity: "watch",
    title: "Bedroom 2 is working hard",
    body: "Bedroom 2 contains a bed, storage, media, partition/wardrobe pieces, and shelving in a long narrow room. That can work for a teenager, but clear floor space and the door-to-window route need watching.",
  };
}

function buildWarnings(
  rooms: ReviewRoom[],
  offPlanObjects: AssignedFurnitureObject[],
  lowLightRooms: string[],
): DesignReviewWarning[] {
  const warnings: Array<DesignReviewWarning | null> = [
    {
      id: "sunroom-daylight-strength",
      severity: "good",
      title: "Sunroom and dining edge are the strongest daylight assets",
      body: "The model and photos both point to the sunroom and kitchen/dining edge as the most useful daylight zones, especially outside winter.",
    },
    offPlanObjects.length > 0
      ? {
        id: "off-plan-objects",
        severity: "problem",
        title: "Some furniture is still off the plan",
        body: `${offPlanObjects.length} object${offPlanObjects.length === 1 ? "" : "s"} appear outside the plan canvas and should be moved or deleted before relying on the review fully.`,
      }
      : null,
    lowLightRooms.length > 0
      ? {
        id: "winter-light-risk",
        severity: "watch",
        title: "Winter daylight is uneven",
        body: `${lowLightRooms.join(", ")} show low winter light in the model. These rooms should rely on task lighting, pale finishes, and uncluttered window zones.`,
      }
      : null,
    warningForCrowdedTeenRoom(rooms),
    {
      id: "hallway-spine",
      severity: "watch",
      title: "The hallway is a narrow circulation spine",
      body: "The measured hallway is about 1.30 m wide, so door swings, storage overflow, and furniture creep from adjoining rooms will quickly affect movement flow.",
    },
  ];
  return warnings.filter((warning): warning is DesignReviewWarning => warning !== null);
}

function buildReportSections(rooms: ReviewRoom[], metrics: DesignReviewMetrics): DesignReviewReportSection[] {
  const bedroom2 = rooms.find((room) => room.id === "bedroom_2");
  const lounge = rooms.find((room) => room.id === "lounge");
  const kitchen = rooms.find((room) => room.id === "kitchen_dining");

  return [
    {
      id: "executive-view",
      title: "Executive View",
      summary: "The house now reads as a compact, practical family layout with a strong light-side living sequence and a more private bedroom/service band.",
      points: [
        "For two adults in the master bedroom and a teenage girl in Bedroom 2, the basic zoning is sensible: adults at one end, teen bedroom near the service/entrance end, and shared living in the middle.",
        `The current saved layout has ${metrics.totalFurnitureObjects} furniture objects, split across ${metrics.fixedFurnitureObjects} fixed and ${metrics.moveableFurnitureObjects} moveable items.`,
        "The best design asset is the connected kitchen/dining, lounge, and sunroom sequence. The main weakness is that circulation and storage are tight, so small furniture shifts matter.",
      ],
    },
    {
      id: "movement-flow",
      title: "Movement Flow",
      summary: "Movement is workable but depends on keeping the hallway, kitchen door line, and lounge-to-sunroom slider free of clutter.",
      points: [
        "The hallway is the key internal spine. It connects the adults' room, office, bathroom, lounge, kitchen/dining, entrance, laundry, and toilet, so it has little tolerance for overflow storage.",
        "The kitchen/dining strip is long and narrow. It suits a linear kitchen, but dining chairs, stools, and open appliance doors need to stay out of the work aisle.",
        lounge
          ? `The lounge currently carries ${lounge.objects.length} furniture objects. That is acceptable if the sofa, coffee table, media unit, and work chair do not block the sunroom slider.`
          : "The lounge should be reviewed as the main social sitting space and as the passage to the sunroom.",
      ],
    },
    {
      id: "light-and-seasons",
      title: "Light And Seasons",
      summary: "The sunlight model is qualitative, but it is useful enough to identify which spaces should be bright, which need task lighting, and where seasonal comfort risks sit.",
      points: [
        "The sunroom is the primary daylight room and likely the strongest place for reading, plants, casual work, and relaxed sitting.",
        "Kitchen/dining has useful light through the deck-side glazing and dining window, but winter morning and afternoon light are weaker in the model.",
        "Bedroom 2, bathroom, hallway, and toilet are the least forgiving in winter. Keep window areas clear and use deliberate task lighting rather than relying on ambient light.",
      ],
    },
    {
      id: "room-by-room-review",
      title: "Room-By-Room Review",
      summary: "The room roles mostly make sense, but the narrow rooms need furniture to support movement rather than simply fit on paper.",
      points: [
        kitchen
          ? `Kitchen / Dining is ${kitchen.dimensionsLabel}. The fixed cabinetry works with the galley shape, but the dining end should remain visually lighter.`
          : "Kitchen / Dining should remain the practical work and meals zone rather than absorbing too much storage.",
        bedroom2
          ? `Bedroom 2 is ${bedroom2.dimensionsLabel} and currently has ${bedroom2.objects.length} assigned objects. This is the room most likely to feel crowded if every wall becomes storage.`
          : "Bedroom 2 should prioritise bed position, desk or reading use, and clean access to the window.",
        "The master bedroom has the right role for two adults, but it benefits from balanced bedside clearance and keeping the window/wardrobe circulation legible.",
      ],
    },
    {
      id: "furniture-fit",
      title: "Furniture Fit",
      summary: "The furniture plan is strongest where pieces support clear zones: sleeping, cooking, sitting, work, storage, and service tasks.",
      points: [
        "Built-in and fixed items are doing useful work in the kitchen, wet areas, wardrobes, and laundry. They should define edges without narrowing already-tight routes.",
        "Moveable furniture adds the real lifestyle value: lounge seating, books, piano, desks, and bedroom storage. The tradeoff is visual and circulation density.",
        "The layout should keep at least one obvious walking line through each room. If a room only works when chairs are tucked perfectly, it will feel frustrating in daily use.",
      ],
    },
    {
      id: "priority-actions",
      title: "Priority Actions",
      summary: "The practical next step is not major building work yet. It is clearance checking, daylight checking, and furniture simplification in the highest-pressure zones.",
      points: [
        "First check the off-plan or unassigned furniture items, then review the kitchen/dining chair clearances and Bedroom 2 floor space.",
        "Second, compare winter morning and afternoon light for Bedroom 2, hallway, bathroom, and kitchen/dining before choosing darker finishes or tall furniture near windows.",
        "Third, preserve the sunroom as the flexible high-value space: reading, overflow entertaining, piano/creative use, and seasonal daylight rather than pure storage.",
      ],
    },
  ];
}

function buildSnippets(rooms: ReviewRoom[]): DesignReviewSnippet[] {
  const objectIdsForRooms = (roomIds: string[]) =>
    rooms
      .filter((room) => roomIds.includes(room.id))
      .flatMap((room) => room.objects.map((object) => object.id));

  return [
    {
      id: "lounge-sunroom-flow",
      title: "Lounge To Sunroom Flow",
      body: "Shows the main sitting zone, media/fireplace wall, and the daylight connection through to the sunroom.",
      viewBox: "500 320 390 230",
      focusRoomIds: ["lounge", "sunroom"],
      highlightObjectIds: objectIdsForRooms(["lounge", "sunroom"]),
    },
    {
      id: "kitchen-dining-service-run",
      title: "Kitchen / Dining Working Strip",
      body: "Shows the long galley-style working zone, fixed cabinetry, appliances, and the dining end.",
      viewBox: "720 280 220 260",
      focusRoomIds: ["kitchen_dining", "entrance", "laundry"],
      highlightObjectIds: objectIdsForRooms(["kitchen_dining", "entrance", "laundry"]),
    },
    {
      id: "bedroom-2-teen-zone",
      title: "Bedroom 2 Teen Zone",
      body: "Shows the narrow bedroom, storage wall pressure, and the need to keep bed-to-door movement clear.",
      viewBox: "740 500 240 160",
      focusRoomIds: ["bedroom_2"],
      highlightObjectIds: objectIdsForRooms(["bedroom_2"]),
    },
    {
      id: "private-room-band",
      title: "Private Rooms And Hallway",
      body: "Shows how the master bedroom, office, bathroom, Bedroom 2, and hallway share the same circulation band.",
      viewBox: "510 455 430 190",
      focusRoomIds: ["master_bedroom", "office", "bathroom", "bedroom_2", "hallway"],
      highlightObjectIds: objectIdsForRooms(["master_bedroom", "office", "bathroom", "bedroom_2", "hallway"]),
    },
  ];
}

function photoEvidence(model: JsonRecord): DesignReviewPhotoEvidence[] {
  const checks = asArray(asRecord(model.photo_evidence).checks);
  return checks.flatMap((checkValue) => {
    const check = asRecord(checkValue);
    const id = asString(check.id);
    if (!IMPORTANT_PHOTO_EVIDENCE_IDS.has(id)) {
      return [];
    }
    const photos = asArray(check.photos)
      .map((photoValue) => {
        const photo = asRecord(photoValue);
        return {
          path: asString(photo.path),
          view: asString(photo.view, "Project photo evidence"),
        };
      })
      .filter((photo) => photo.path.length > 0)
      .slice(0, 4);
    return [{
      id,
      summary: asString(check.summary),
      photos,
    }];
  });
}

export function buildDesignReviewAnalysis(data: DesignReviewData): DesignReviewAnalysis {
  const model = asRecord(data.house_model);
  const layout = data.furniture_layout.layout;
  const assignedObjects = assignObjects(layout, model);
  const offPlanObjects = assignedObjects.filter((object) => isOffPlan(object, layout));
  const unassignedObjects = assignedObjects.filter((object) => !object.roomId && !isOffPlan(object, layout));
  const rooms = buildRooms(model, assignedObjects);
  const lowLightRooms = lowWinterLightRooms(model, roomNameById(model));
  const metrics: DesignReviewMetrics = {
    totalFurnitureObjects: layout.objects.length,
    fixedFurnitureObjects: layout.objects.filter((object) => object.layer === "fixed").length,
    moveableFurnitureObjects: layout.objects.filter((object) => object.layer === "moveable").length,
    roomCount: rooms.length,
    lowWinterLightRooms: lowLightRooms,
    savedLayoutSource: data.furniture_layout.source,
  };

  return {
    modelSource: data.model_source,
    layoutSource: data.furniture_layout.source,
    metrics,
    rooms,
    assignedObjects,
    offPlanObjects,
    unassignedObjects,
    dynamicWarnings: buildWarnings(rooms, offPlanObjects, lowLightRooms),
    reportSections: buildReportSections(rooms, metrics),
    snippets: buildSnippets(rooms),
    photoEvidence: photoEvidence(model),
  };
}
