import { svgToMetres } from "./furnitureGeometry";
import { CURRENT_SCENARIO_ID } from "./designScenarios";
import {
  FURNITURE_REUSE_CATEGORY_LABELS,
  designScenarioConceptById,
  type DesignScenarioFurnitureReuse,
  type DesignScenarioConcept,
} from "./designScenarioConcepts";
import { houseModelForScenario } from "./scenarioHouseModel";
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

export type DesignReviewSummarySection = {
  id: string;
  title: string;
  points: string[];
};

export type DesignReviewOverallAssessment = {
  title: string;
  paragraphs: string[];
  priorities: string[];
};

export type DesignReviewPracticalFinding = {
  id: string;
  severity: ReviewSeverity;
  title: string;
  body: string;
};

export type DesignReviewRoomAnalysis = {
  id: string;
  name: string;
  dimensions: string;
  use: string;
  light: string;
  furniture: string;
  improvement: string;
};

export type DesignReviewMovementPoint = {
  x: number;
  y: number;
  label: string;
};

export type DesignReviewMovementScenario = {
  id: string;
  person: string;
  routine: string;
  rooms: string[];
  points: DesignReviewMovementPoint[];
  colour: string;
  note: string;
};

export type DesignReviewExpertReview = {
  role: string;
  pushback: string;
  added: string;
  passedBy: string;
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
  overallAssessment: DesignReviewOverallAssessment;
  summarySections: DesignReviewSummarySection[];
  practicalFindings: DesignReviewPracticalFinding[];
  roomAnalyses: DesignReviewRoomAnalysis[];
  movementMapViewBox: string;
  movementScenarios: DesignReviewMovementScenario[];
  expertReview: DesignReviewExpertReview[];
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

function titleFromId(id: string): string {
  return id
    .split("_")
    .map((word) => word.length > 0 ? `${word[0].toUpperCase()}${word.slice(1)}` : word)
    .join(" ");
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

function geometryCenterSvg(geometry: Geometry): PlanPoint {
  if (geometry.type === "rect") {
    return {
      x: geometry.x + geometry.width / 2,
      y: geometry.y + geometry.height / 2,
    };
  }

  const points = geometry.type === "polygon"
    ? geometry.points
    : geometry.polygons.flatMap((polygon) => polygon);
  const xs = points.map((point) => asNumber(point[0])).filter((value): value is number => value !== null);
  const ys = points.map((point) => asNumber(point[1])).filter((value): value is number => value !== null);
  if (xs.length === 0 || ys.length === 0) {
    return { x: 0, y: 0 };
  }
  return {
    x: (Math.min(...xs) + Math.max(...xs)) / 2,
    y: (Math.min(...ys) + Math.max(...ys)) / 2,
  };
}

function roomSvgCenters(model: JsonRecord): Map<string, PlanPoint> {
  return new Map(roomGeometries(model).map(({ id, geometry }) => [id, geometryCenterSvg(geometry)]));
}

function displayGeometryById(value: unknown, targetId: string): Geometry | null {
  if (Array.isArray(value)) {
    for (const item of value) {
      const geometry = displayGeometryById(item, targetId);
      if (geometry) {
        return geometry;
      }
    }
    return null;
  }

  const record = asRecord(value);
  if (Object.keys(record).length === 0) {
    return null;
  }

  if (asString(record.id) === targetId) {
    const geometry = geometryFromRecord(record.display_px);
    if (geometry) {
      return geometry;
    }
  }

  for (const nested of Object.values(record)) {
    const geometry = displayGeometryById(nested, targetId);
    if (geometry) {
      return geometry;
    }
  }
  return null;
}

function featureCenterSvg(model: JsonRecord, featureId: string): PlanPoint | null {
  const geometry = displayGeometryById(model, featureId);
  return geometry ? geometryCenterSvg(geometry) : null;
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

const DAYLIGHT_LEVEL_SCORES: Record<string, number> = {
  low: 0,
  medium: 1,
  high: 2,
  unknown: 0,
};

const DAYLIGHT_SEASONS = ["summer", "autumn", "winter", "spring"];
const ACTIVE_DAYLIGHT_TIMES = ["morning", "midday"];
const LOW_USE_LIGHT_ROOM_IDS = new Set(["entrance", "laundry"]);

function daylightRoomFor(model: JsonRecord, roomId: string): JsonRecord {
  return asRecord(asRecord(asRecord(model.daylight).rooms)[roomId]);
}

function daylightScoreForTime(daylightRoom: JsonRecord, season: string, timeBand: string): number | null {
  const level = asString(asRecord(daylightRoom[season])[timeBand]);
  if (!level) {
    return null;
  }
  return DAYLIGHT_LEVEL_SCORES[level] ?? 0;
}

function averageDaylightScore(daylightRoom: JsonRecord, seasons: string[], timeBands: string[]): number {
  const scores = seasons.flatMap((season) =>
    timeBands.flatMap((timeBand) => {
      const score = daylightScoreForTime(daylightRoom, season, timeBand);
      return score === null ? [] : [score];
    }));
  if (scores.length === 0) {
    return 0;
  }
  return scores.reduce((total, score) => total + score, 0) / scores.length;
}

function usefulLowUseLightRoomNames(model: JsonRecord, rooms: ReviewRoom[]): string[] {
  return rooms
    .filter((room) => LOW_USE_LIGHT_ROOM_IDS.has(room.id))
    .filter((room) =>
      averageDaylightScore(daylightRoomFor(model, room.id), DAYLIGHT_SEASONS, ACTIVE_DAYLIGHT_TIMES) >= 0.7)
    .map((room) => room.name);
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

function buildOverallAssessment(
  rooms: ReviewRoom[],
  metrics: DesignReviewMetrics,
  serviceLightRooms: string[],
  scenarioId: string,
): DesignReviewOverallAssessment {
  if (scenarioId === "back-side-living-sunroom-bedroom") {
    return {
      title: "Overall Assessment",
      paragraphs: [
        "Design 2 is a genuine whole-house rebalancing rather than a furniture shuffle. Its strongest idea is moving everyday living toward the brighter back side of the house, while turning the old lounge into a quieter bedroom and replacing the thermally awkward sunroom with an insulated bedroom.",
        "The plan is promising because it puts the best morning and early-afternoon light into a room people would actually occupy: the new living/dining/day room. It also keeps the renovated kitchen largely intact, creates a clearer arrival point, and gives the teenager a bedroom position that is less overloaded by the current long narrow Bedroom 2 constraints.",
        `The trade-off is build complexity. With ${metrics.totalFurnitureObjects} furniture objects to reuse or relocate, this option only works if the new lounge furniture grouping, relocated service rooms, and bedroom storage are designed as a coordinated package. It is not prohibitively extravagant compared with adding another storey, but it is still a high-disruption renovation.`,
      ],
      priorities: [
        "Keep the renovated kitchen in place unless a later costing proves a minor adjustment is worth it.",
        "Resolve the relocated bathroom, laundry, and WC as proper separated service rooms, not a combined bathroom/laundry compromise.",
        "Use the new back-side living room for daily sitting, dining, homework, and entertaining so the best light is no longer wasted on service rooms.",
        "Make the old lounge bedroom feel intentional: correct door swing, a large north window, calm storage, and enough acoustic separation from the kitchen/chill edge.",
        "Treat the former sunroom replacement bedroom as a real insulated room with privacy, heating/cooling, and window coverings, not as a glazed add-on.",
      ],
    };
  }

  const bedroom2 = rooms.find((room) => room.id === "bedroom_2");
  return {
    title: "Overall Assessment",
    paragraphs: [
      "Overall, the house reads as a compact, workable family home with a real lifestyle upside, but its main design weakness is a threshold problem. The front door sequence is unclear, the sunroom is visually important but seasonally unstable, the deck is appealing but exposed, and the lounge is asked to be both the main sitting room and a through-route.",
      `The best part of the plan is the connected kitchen, dining, lounge, sunroom, and deck sequence: it gives the house a social heart and useful flexibility. The tension is that some of the better morning and early-afternoon light lands in ${serviceLightRooms.length > 0 ? serviceLightRooms.join(" and ") : "the service end of the house"}, while the lounge, Bedroom 2, office, and hallway need more deliberate furniture placement and lighting.`,
      `The current furniture layout is close enough to review seriously, with ${metrics.totalFurnitureObjects} placed objects${bedroom2 ? ` and Bedroom 2 working within ${bedroom2.dimensionsLabel}` : ""}. The next improvement should not be more furniture. The best move is to simplify and clarify: make arrival obvious, make the sunroom/deck reliable enough to use, protect lounge circulation, and keep Bedroom 2 calm enough for a teenager to sleep, study, store belongings, and retreat without the room feeling packed.`,
    ],
    priorities: [
      "Clarify arrival and the front door before making major furniture or redesign decisions.",
      "Decide whether the sunroom and deck are true daily living spaces or seasonal overflow; if they are daily spaces, solve thermal comfort, shade, wind, and glare first.",
      "Protect the lounge as a sitting room by reducing route conflict between kitchen/dining, hallway, and sunroom.",
      "Treat the laundry and entrance daylight as useful service light, not as a substitute for better living-room and bedroom comfort.",
      "Treat the lack of a second toilet as a practical design issue; if the bathroom is redesigned, test whether a second WC can be added without compromising shower, basin, storage, ventilation, or circulation clearances.",
      "Edit Bedroom 2 around one clear movement path, one calm wall, and reliable task lighting instead of filling every edge with storage.",
    ],
  };
}

function buildSummarySections(
  rooms: ReviewRoom[],
  metrics: DesignReviewMetrics,
  offPlanObjects: AssignedFurnitureObject[],
  serviceLightRooms: string[],
  scenarioId: string,
): DesignReviewSummarySection[] {
  if (scenarioId === "back-side-living-sunroom-bedroom") {
    return [
      {
        id: "strengths",
        title: "Strengths",
        points: [
          "The main strength is that the best back-side light is reassigned to a room people would actually use for sitting, eating, homework, and entertaining.",
          "The kitchen can remain largely as renovated, which protects recent investment while still changing the house's daily centre of gravity.",
          "Replacing the sunroom with an insulated bedroom solves the current seasonal comfort problem more decisively than trying to make the old sunroom do everything.",
          "The current lounge can become a calmer bedroom because it no longer has to operate as both the main sitting room and a through-route.",
          offPlanObjects.length === 0
            ? "The furniture layout is currently all on-plan, so the review can focus on whether reuse and placement support the new room purposes."
            : `${offPlanObjects.length} item${offPlanObjects.length === 1 ? "" : "s"} still need placement cleanup before this option can be judged fully.`,
        ],
      },
      {
        id: "weaknesses",
        title: "Weaknesses",
        points: [
          "This is the highest-risk of the worked-through options because it relocates service functions, changes room purposes, and depends on good detailing around new walls, doors, windows, and flooring.",
          "The relocated laundry, bathroom, and WC must be separated and properly ventilated. A combined bathroom/laundry would undermine the design and feel awkward day to day.",
          "The old lounge bedroom needs careful acoustic and privacy treatment because it remains close to kitchen/chill activity.",
          "The replacement bedroom on the former sunroom footprint must be built as a proper insulated room; if it inherits sunroom-like thermal behaviour, the design fails at its biggest promise.",
          "Furniture reuse is helpful for cost control, but reused pieces can easily become clutter if the new living/dining/day room is treated as a dumping ground for everything that used to fit elsewhere.",
        ],
      },
      {
        id: "moveable-opportunities",
        title: "Moveable Furniture Opportunities",
        points: [
          `Reuse the existing sofa, armchairs, dining table, chairs, and media pieces only where they reinforce the new back-side living room's daily purpose.`,
          "Use the kitchen/dining chill edge for a lighter reading or quiet sitting setup rather than duplicating the main lounge furniture.",
          "Keep the old lounge bedroom simple: bed, storage, bedside pieces, and possibly a small reading/media piece, but avoid recreating a second lounge in that room.",
          "If the teenager moves into the old lounge bedroom, reuse existing bedroom furniture selectively and prioritise desk/storage positions that protect the new door and window clearances.",
          `Because there are ${metrics.moveableFurnitureObjects} moveable objects, the review should test subtraction as much as relocation: some pieces may be better stored, sold, or replaced with slimmer versions.`,
        ],
      },
    ];
  }

  const bedroom2 = rooms.find((room) => room.id === "bedroom_2");
  const lounge = rooms.find((room) => room.id === "lounge");
  const kitchen = rooms.find((room) => room.id === "kitchen_dining");

  return [
    {
      id: "strengths",
      title: "Strengths",
      points: [
        "The basic zoning is sensible: adults in the Master Bedroom, a teenager in Bedroom 2, and shared living through the kitchen/dining, lounge, and sunroom sequence.",
        "The sunroom and deck-side dining edge give the house a real lifestyle asset for reading, casual sitting, plants, music, and overflow entertaining.",
        `The fixed furniture mostly sits where fixed furniture should sit: kitchen, laundry, bathroom, toilet, and wardrobe zones, leaving moveable furniture to do the lifestyle work.`,
        offPlanObjects.length === 0
          ? "The current saved layout is fully on the plan, so the review can now focus on design quality rather than cleanup."
          : `${offPlanObjects.length} furniture item${offPlanObjects.length === 1 ? "" : "s"} still need placement cleanup before the review is fully reliable.`,
      ],
    },
    {
      id: "weaknesses",
      title: "Weaknesses",
      points: [
        serviceLightRooms.length > 0
          ? `${serviceLightRooms.join(" and ")} receive useful morning to early-afternoon daylight, but they are low-use service or transition rooms. That means some of the house's best light is not landing in the places people linger.`
          : "The daylight model suggests the best light is unevenly distributed, so furniture decisions should be made room by room rather than assuming the whole house behaves the same.",
        "The hallway, entrance, kitchen/dining strip, and Bedroom 2 are all narrow enough that furniture can technically fit while still making daily movement feel tight.",
        lounge
          ? "The lounge is a particular pressure point: it is expected to be the main sitting room, but it also has large openings to kitchen/dining and sunroom, acts as a movement junction, and relies heavily on borrowed rather than abundant direct light."
          : "The main sitting room should be checked for both comfort and movement pressure, not just furniture fit.",
        "The original front door sits awkwardly inside the sunroom and leads into the hallway, so visitors may not get a clear, intuitive arrival sequence. The deck/entrance side also functions like a daily entry, but not necessarily like an obvious formal front door.",
        "The sunroom and deck both have seasonal comfort issues: the sunroom can be too cold in winter or too hot in summer, while the deck is useful as an outdoor sitting area but lacks reliable shade and wind-stable shelter.",
        "The house currently has only one toilet, accessed through the laundry. For two adults, a teenager, and guests, that is a practical bottleneck; the likely solution is redoing the bathroom layout to include a second WC, subject to fixture clearances, ventilation, and not making the wet-area layout feel cramped.",
        bedroom2
          ? `Bedroom 2 is ${bedroom2.dimensionsLabel} and has to support sleeping, storage, study/media, and teenage privacy in one long room. It needs clear floor space more than extra furniture.`
          : "Bedroom 2 is the room most likely to feel overloaded if storage and study furniture are allowed to creep into every wall.",
        "Winter and afternoon light are weaker in several of the rooms people are likely to use for relaxing, working, or studying, so finishes and task lighting matter.",
      ],
    },
    {
      id: "moveable-opportunities",
      title: "Moveable Furniture Opportunities",
      points: [
        bedroom2
          ? "In Bedroom 2, prioritise fewer but better pieces: a slimmer dresser, low book storage, and a desk/reading setup that does not block the window or the door-to-bed route."
          : "In Bedroom 2, test whether a smaller dresser, lower storage, or a different desk position would give better floor space and daylight access.",
        lounge
          ? `In the lounge, keep the sofa/media/fireplace relationship simple and protect the route to the sunroom. If a chair, bookcase, or music piece crowds that route, it is a candidate to move toward the brighter sunroom edge.`
          : "In the lounge, treat any extra chair, bookcase, or music piece as optional unless it improves sitting, reading, or entertaining without blocking the sunroom connection.",
        kitchen
          ? "In kitchen/dining, use visually lighter dining chairs or stools and avoid tall moveable storage near the dining/window end, because the room is already doing a lot in a narrow strip."
          : "In kitchen/dining, favour smaller, lighter moveable pieces over bulky storage so the room still feels like a place to eat rather than a corridor with appliances.",
        "For the deck, test flexible seating only if shade and wind are solved. A basic umbrella is not enough if it becomes unusable in wind or misses the sun angle at the times you want to sit there.",
        `Because there are ${metrics.moveableFurnitureObjects} moveable objects, the most valuable next exercise is not adding more. It is testing two or three simplified layouts and comparing circulation, daylight, and comfort.`,
      ],
    },
  ];
}

function buildPracticalFindings(
  rooms: ReviewRoom[],
  lowLightRooms: string[],
  serviceLightRooms: string[],
): DesignReviewPracticalFinding[] {
  const bedroom2 = rooms.find((room) => room.id === "bedroom_2");
  const findings: DesignReviewPracticalFinding[] = [];

  if (serviceLightRooms.length > 0) {
    findings.push({
      id: "service-light-mismatch",
      severity: "watch",
      title: "Good daylight is partly landing in low-use service spaces",
      body: `${serviceLightRooms.join(" and ")} get comparatively useful morning to early-afternoon light, but they are short-stay rooms. That light is still helpful for arrival, laundry tasks, and visual freshness, but the design should not treat it as equal to daylight in the lounge, Bedroom 2, office, or main dining area.`,
    });
  }

  if (lowLightRooms.length > 0) {
    findings.push({
      id: "winter-use-rooms",
      severity: "watch",
      title: "Winter light needs to be matched with actual room use",
      body: `${lowLightRooms.join(", ")} show consistently low winter light. The practical response is layered lighting, lighter finishes, clear window zones, and avoiding tall dark furniture in places used for study, reading, grooming, or circulation.`,
    });
  }

  const lounge = rooms.find((room) => room.id === "lounge");
  if (lounge) {
    findings.push({
      id: "lounge-circulation-light",
      severity: "watch",
      title: "The lounge is a sitting room and a movement junction",
      body: "The lounge has large openings to kitchen/dining and the sunroom, plus it sits on the main internal movement route. Its daylight is mostly borrowed light from the sunroom and related openings, so it should not be overloaded with furniture that narrows routes or makes the room feel darker.",
    });
  }

  if (bedroom2) {
    findings.push({
      id: "teen-room-pressure",
      severity: "watch",
      title: "Bedroom 2 needs editing more than filling",
      body: `Bedroom 2 is ${bedroom2.dimensionsLabel}, long and narrow, and currently has ${bedroom2.objects.length} assigned furniture objects. It can work for a teenager if the layout protects one clear movement line and one calm wall, rather than treating every edge as storage.`,
    });
  }

  findings.push(
    {
      id: "sunroom-seasonal-comfort",
      severity: "watch",
      title: "Sunroom comfort is seasonal",
      body: "The sunroom is a major daylight and lifestyle asset, but it may be too cold in winter and too hot in summer. Treat it as a flexible seasonal room unless insulation, ventilation, shading, and heating/cooling are improved.",
    },
    {
      id: "front-door-ambiguity",
      severity: "problem",
      title: "The front door sequence is not obvious",
      body: "The original front door is inside the sunroom and awkwardly leads to the hallway. For visitors, that can make arrival feel unclear: the house has entries, but not a legible front door moment.",
    },
    {
      id: "deck-shade-wind",
      severity: "watch",
      title: "Deck use depends on shade and wind control",
      body: "The Deck should be considered as an outdoor sitting area connected to kitchen/dining and entrance, but the current shade is weak. A basic umbrella does not solve wind or low-angle sun, so a better fixed, retractable, or wind-stable shade strategy should be assessed.",
    },
  );

  return findings;
}

function buildReportSections(rooms: ReviewRoom[], metrics: DesignReviewMetrics): DesignReviewReportSection[] {
  const bedroom2 = rooms.find((room) => room.id === "bedroom_2");
  const lounge = rooms.find((room) => room.id === "lounge");
  const kitchen = rooms.find((room) => room.id === "kitchen_dining");

  return [
    {
      id: "useful-light-rhythm",
      title: "Useful Light And Daily Rhythm",
      summary: "The daylight model is most useful when read against daily routines: breakfast, work or study, after-school use, evening sitting, and weekend entertaining.",
      points: [
        "Morning to early-afternoon light is not automatically valuable if it lands in rooms people pass through quickly. The laundry and entrance light is useful, but the main lifestyle value still needs to be created in the lounge, sunroom, dining area, office, and Bedroom 2.",
        "The sunroom should be treated as the house's main daylight asset: reading, plants, coffee, quiet time, music, or overflow entertaining are better uses than dead storage.",
        "Bedroom 2 is likely to be used most after school, in the evening, and on weekends. Because its afternoon and winter light are weaker, the desk or reading position should have deliberate task lighting and should not be buried behind tall storage.",
      ],
    },
    {
      id: "movement-furniture-priorities",
      title: "Movement And Furniture Priorities",
      summary: "The layout works best when furniture reinforces the main walking routes rather than just filling available wall space.",
      points: [
        "Keep the hallway as a clean spine. It is the route between bedrooms, bathroom, lounge, kitchen, entrance, laundry, and toilet, so it should not become an overflow storage zone.",
        "The kitchen/dining strip suits a linear working arrangement, but dining chairs, stools, appliance doors, and tall storage need to respect the work aisle.",
        lounge
          ? `The lounge has ${lounge.objects.length} assigned furniture objects. That can work, but only if the sofa, media/fireplace wall, and sunroom route read as one simple sitting arrangement.`
          : "The lounge should be judged by whether it creates a simple sitting arrangement and a clean route to the sunroom.",
      ],
    },
    {
      id: "room-priority-checks",
      title: "Room Priorities Worth Checking",
      summary: "These are the checks that are more useful than a raw room-by-room object list.",
      points: [
        kitchen
          ? `Kitchen / Dining is ${kitchen.dimensionsLabel}. Check dining-chair pull-out, stool clearance, and whether the window end stays visually lighter than the kitchen work run.`
          : "Kitchen / Dining should remain the practical work and meals zone rather than absorbing too much storage.",
        bedroom2
          ? `Bedroom 2 is ${bedroom2.dimensionsLabel}. Check whether the bed, dresser, desk/media, and wardrobe pieces still leave a clear daily path and one uncluttered visual zone.`
          : "Bedroom 2 should prioritise bed position, desk or reading use, and clean access to the window.",
        `There are ${metrics.fixedFurnitureObjects} fixed and ${metrics.moveableFurnitureObjects} moveable items. The high-value review is whether moveable pieces improve a room's purpose, not whether every item has a place on the drawing.`,
      ],
    },
  ];
}

function buildScenarioReportSections(scenarioId: string): DesignReviewReportSection[] {
  if (scenarioId === CURRENT_SCENARIO_ID) {
    return [];
  }

  const concept: DesignScenarioConcept | null = designScenarioConceptById(scenarioId);
  if (!concept) {
    return [];
  }

  const sections: DesignReviewReportSection[] = [
    {
      id: `scenario-${concept.id}`,
      title: concept.label,
      summary: `${concept.room_changes[0] ?? concept.summary} ${concept.summary}`,
      points: [
        `Cost band: ${concept.cost_band}.`,
        ...concept.room_changes,
        ...concept.daylight_strategy.map((point) => `Daylight: ${point}`),
        ...concept.movement_strategy.map((point) => `Movement: ${point}`),
        ...concept.build_scope.map((point) => `Build scope: ${point}`),
        ...concept.risks,
      ],
    },
  ];

  const reuseSection = buildFurnitureReuseSection(concept);
  if (reuseSection) {
    sections.push(reuseSection);
  }

  return sections;
}

function furnitureReusePoint(entry: DesignScenarioFurnitureReuse): string {
  const label = FURNITURE_REUSE_CATEGORY_LABELS[entry.category];
  const locationSuffix = entry.proposed_location && entry.category !== "new_required"
    ? ` -> ${entry.proposed_location}`
    : "";
  return `${label}: ${entry.item}${locationSuffix}.`;
}

function buildFurnitureReuseSection(
  concept: DesignScenarioConcept,
): DesignReviewReportSection | null {
  if (!concept.furniture_reuse || concept.furniture_reuse.length === 0) {
    return null;
  }

  return {
    id: `scenario-furniture-reuse-${concept.id}`,
    title: "Furniture Reuse And New Items",
    summary: "This option should reuse as much of the current furniture and joinery as possible, but only where the reused item supports the new room purpose rather than cluttering it.",
    points: concept.furniture_reuse.map(furnitureReusePoint),
  };
}

function countLabel(count: number, singular: string, plural = `${singular}s`): string {
  return `${count} ${count === 1 ? singular : plural}`;
}

function roomUseAnalysis(room: ReviewRoom): string {
  switch (room.id) {
    case "future_living_dining_day_room":
      return "The main everyday living, dining, homework, shared screen time, and entertaining zone. This is where Design 2 deliberately relocates the family's daily life to capture the better back-side light.";
    case "kitchen_dining_chill_zone":
      return "Renovated kitchen plus a quieter chill or reading edge. It should support food, coffee, conversation, and short retreat without competing with the main day room.";
    case "replacement_insulated_bedroom":
      return "New insulated bedroom replacing the old sunroom footprint. It must behave like a proper bedroom, not a seasonal glazed porch.";
    case "relocated_service_rooms":
      return "Separated bathroom, laundry, WC, and storage service core. The aim is practical function and privacy without wasting the brightest back-side wall.";
    case "current_lounge_bedroom":
      return "Bedroom 2 in the former lounge position, giving the teenager more privacy and removing the room from the narrow back-side service strip.";
    case "kitchen_dining":
      return "Daily meals, food preparation, household gathering, and the route between the living areas and service end.";
    case "lounge":
      return "Main sitting room, shared screen/fireplace zone, and movement junction between kitchen/dining, hallway, and sunroom.";
    case "sunroom":
      return "Flexible daylight room: reading, quiet sitting, plants, music, casual work, visitor arrival spillover, and seasonal overflow entertaining.";
    case "hallway":
      return "Primary circulation spine rather than a room to furnish. It needs to stay visually and physically clear.";
    case "master_bedroom":
      return "Adult sleeping and dressing room for two people, with a need for calm, balanced bedside and wardrobe circulation.";
    case "office":
      return "Small work, study, or overflow quiet room. Its success depends on desk position, lighting, and avoiding spare-room clutter.";
    case "bathroom":
      return "Compact wet room where grooming, showering, and bath use compete for a small footprint.";
    case "bedroom_2":
      return "Teen bedroom for sleeping, privacy, storage, study/media, and retreat. It has to do more than its narrow shape naturally wants to do.";
    case "entrance":
      return "Daily arrival, shoes, coats, and transition from deck/driveway into the kitchen and laundry side, but not a clear formal front-door sequence.";
    case "laundry":
      return "Service room for laundry, cleaning storage, and back-of-house tasks, with more useful daylight than its use pattern normally deserves.";
    case "toilet":
      return "Short-stay service room. It needs clarity, ventilation, and easy access more than extra visual treatment.";
    default:
      return `${room.name} should be treated according to its main daily purpose before adding more furniture.`;
  }
}

function roomLightAnalysis(room: ReviewRoom): string {
  switch (room.id) {
    case "future_living_dining_day_room":
      return `${room.daylightSummary}. This is the key daylight win: morning and early-afternoon light moves into the room most likely to be occupied during waking hours.`;
    case "kitchen_dining_chill_zone":
      return `${room.daylightSummary}. Keep finishes and furniture visually light so the renovated kitchen and chill edge still borrow brightness from the deck-side glazing.`;
    case "replacement_insulated_bedroom":
      return `${room.daylightSummary}. It needs curtains, privacy, and thermal control because the old sunroom position has the best light but also the greatest comfort risk.`;
    case "relocated_service_rooms":
      return `${room.daylightSummary}. This area can rely more on controlled artificial light, extraction, and practical finishes than on prime daylight.`;
    case "current_lounge_bedroom":
      return `${room.daylightSummary}. The proposed larger north window is important because the old lounge position should become a believable bedroom, not a leftover dark room.`;
    case "lounge":
      return `${room.daylightSummary}. This is borrowed light rather than a bright, direct-light lounge, so pale finishes and uncluttered openings matter.`;
    case "entrance":
    case "laundry":
      return `${room.daylightSummary}. This is useful light, but it lands in a short-stay service/transition area rather than a room people occupy for long periods.`;
    case "sunroom":
      return `${room.daylightSummary}. Treat this as the main daylight asset, but test heat gain, glare, winter cold, and ventilation before relying on it as an all-season sitting room.`;
    case "bedroom_2":
      return `${room.daylightSummary}. Because use is likely after school, evening, and weekends, task lighting matters as much as daytime sun.`;
    default:
      return room.daylightSummary;
  }
}

function roomFurnitureAnalysis(room: ReviewRoom): string {
  const layerSummary = `${countLabel(room.fixedCount, "fixed item")} and ${countLabel(room.moveableCount, "moveable item")}`;
  if (room.objects.length === 0) {
    return "No saved furniture is assigned to this room yet.";
  }
  const keyObjects = room.objects
    .slice(0, 5)
    .map((object) => object.label)
    .join(", ");
  return `${layerSummary}. Main placed pieces: ${keyObjects}${room.objects.length > 5 ? ", and related smaller pieces" : ""}.`;
}

function roomImprovementAnalysis(room: ReviewRoom): string {
  switch (room.id) {
    case "future_living_dining_day_room":
      return "Group sofa, dining, and circulation deliberately: clear entry path, no furniture crossing the bedroom/service routes, and enough open floor for three people plus guests.";
    case "kitchen_dining_chill_zone":
      return "Keep this quieter than the main day room: a reading chair, slim storage, or small music/coffee spot works better than a full second lounge setup.";
    case "replacement_insulated_bedroom":
      return "Design the envelope first: insulation, window size, privacy treatment, heating/cooling, and a normal door. Furniture should follow those decisions.";
    case "relocated_service_rooms":
      return "Separate bathroom, WC, laundry, and storage cleanly; check plumbing runs, ventilation, acoustic privacy, and usable appliance clearances before committing.";
    case "current_lounge_bedroom":
      return "Make the former lounge read as a bedroom with a clear door, large north window, simple storage wall, and controlled connection to the kitchen/chill edge.";
    case "kitchen_dining":
      return "Keep dining furniture light, preserve chair pull-out space, and avoid tall moveable storage near the brighter dining/window end.";
    case "lounge":
      return "Simplify the sitting group and protect routes to the kitchen/dining opening, hallway side, and sunroom doors. Any optional chair or storage should earn its place.";
    case "sunroom":
      return "Use it deliberately as a light-rich retreat or overflow entertaining zone, but solve summer heat, winter cold, and visitor-entry awkwardness before treating it as a normal living room.";
    case "hallway":
      return "Do not allow furniture creep. Keep wall storage shallow, doors unobstructed, and sightlines simple.";
    case "master_bedroom":
      return "Keep bedside clearance balanced for two adults and avoid blocking the wardrobe/window circulation line.";
    case "office":
      return "Place the desk to make the most of morning light, then add task lighting so the room remains useful later in the day.";
    case "bathroom":
      return "Prioritise clear wet-area movement, pale finishes, and practical lighting over extra storage.";
    case "bedroom_2":
      return "Reduce visual load where possible: slimmer storage, one clear movement line, and a desk or reading zone with reliable task lighting.";
    case "entrance":
      return "Clarify the front door experience for visitors, then keep storage disciplined so the narrow entry/deck-side arrival path does not become a bottleneck.";
    case "laundry":
      return "Use the daylight for practical tasks, but do not over-invest lifestyle value here unless it supports storage, cleaning, or garden access.";
    case "toilet":
      return "Keep it simple, bright, and easy to clean; avoid adding visual clutter to a very small service room.";
    default:
      return "Test whether the current furniture improves use, light, and movement before adding anything else.";
  }
}

function buildRoomAnalyses(rooms: ReviewRoom[]): DesignReviewRoomAnalysis[] {
  return rooms.map((room) => ({
    id: room.id,
    name: room.name,
    dimensions: room.dimensionsLabel,
    use: roomUseAnalysis(room),
    light: roomLightAnalysis(room),
    furniture: roomFurnitureAnalysis(room),
    improvement: roomImprovementAnalysis(room),
  }));
}

function movementRouteDefinitions(scenarioId: string) {
  if (scenarioId === "back-side-living-sunroom-bedroom") {
    return [
      {
        id: "adult-1-morning",
        person: "Adult 1",
        routine: "Morning start",
        roomIds: ["master_bedroom", "hallway", "relocated_service_rooms", "kitchen_dining", "future_living_dining_day_room"],
        colour: "#2f6f9f",
        note: "Shows the adult route from sleeping to the relocated service core, kitchen, and brighter back-side living/day area.",
      },
      {
        id: "adult-2-home-evening",
        person: "Adult 2",
        routine: "Evening home loop",
        roomIds: ["future_living_dining_day_room", "kitchen_dining", "kitchen_dining_chill_zone", "current_lounge_bedroom", "master_bedroom"],
        colour: "#8b5d9f",
        note: "Shows arrival into the new day room, food, quieter chill space, checking the new bedroom, and return to the adult bedroom end.",
      },
      {
        id: "teen-after-school",
        person: "Teenager",
        routine: "After-school pattern",
        roomIds: ["current_lounge_bedroom", "relocated_service_rooms", "kitchen_dining", "future_living_dining_day_room", "current_lounge_bedroom"],
        colour: "#c46f2d",
        note: "Shows the teen loop from the new Bedroom 2 position to bathroom/service rooms, food, shared sitting, and retreat.",
      },
    ];
  }

  return [
    {
      id: "adult-1-morning",
      person: "Adult 1",
      routine: "Morning start",
      roomIds: ["master_bedroom", "hallway", "bathroom", "kitchen_dining", "entrance"],
      colour: "#2f6f9f",
      note: "Shows the adult route from sleeping to bathroom, breakfast, and leaving the house.",
    },
    {
      id: "adult-2-home-evening",
      person: "Adult 2",
      routine: "Evening home loop",
      roomIds: ["entrance", "deck", "kitchen_dining", "lounge", "sunroom", "master_bedroom"],
      colour: "#8b5d9f",
      note: "Shows arrival, deck use if shade/wind allow it, dinner, sitting, daylight/quiet time, and return to the bedroom end.",
    },
    {
      id: "teen-after-school",
      person: "Teenager",
      routine: "After-school pattern",
      roomIds: ["bedroom_2", "bathroom", "kitchen_dining", "lounge", "bedroom_2"],
      colour: "#c46f2d",
      note: "Shows the likely teen loop between bedroom, bathroom, food, shared sitting, and retreat.",
    },
  ];
}

function buildMovementScenarios(model: JsonRecord, scenarioId: string): DesignReviewMovementScenario[] {
  const names = roomNameById(model);
  const centers = roomSvgCenters(model);
  const deckPoint = featureCenterSvg(model, "rear_timber_deck");
  const namedPoint = (roomId: string): DesignReviewMovementPoint[] => {
    const point = roomId === "deck" ? deckPoint : centers.get(roomId);
    if (!point) {
      return [];
    }
    return [{
      ...point,
      label: roomId === "deck" ? "Deck" : names.get(roomId) ?? titleFromId(roomId),
    }];
  };

  const scenarios = movementRouteDefinitions(scenarioId);

  return scenarios.map((scenario) => ({
    id: scenario.id,
    person: scenario.person,
    routine: scenario.routine,
    rooms: scenario.roomIds.map((roomId) => roomId === "deck" ? "Deck" : names.get(roomId) ?? titleFromId(roomId)),
    points: scenario.roomIds.flatMap(namedPoint),
    colour: scenario.colour,
    note: scenario.note,
  }));
}

function movementMapViewBox(layout: FurnitureLayout, scenarios: DesignReviewMovementScenario[]): string {
  const points = scenarios.flatMap((scenario) => scenario.points);
  if (points.length === 0) {
    return `0 0 ${layout.plan_transform.svg_width_px} ${layout.plan_transform.svg_height_px}`;
  }
  const padding = 48;
  const minX = Math.max(0, Math.min(...points.map((point) => point.x)) - padding);
  const minY = Math.max(0, Math.min(...points.map((point) => point.y)) - padding);
  const maxX = Math.min(layout.plan_transform.svg_width_px, Math.max(...points.map((point) => point.x)) + padding);
  const maxY = Math.min(layout.plan_transform.svg_height_px, Math.max(...points.map((point) => point.y)) + padding);
  return `${minX.toFixed(1)} ${minY.toFixed(1)} ${(maxX - minX).toFixed(1)} ${(maxY - minY).toFixed(1)}`;
}

function buildExpertReview(): DesignReviewExpertReview[] {
  return [
    {
      role: "Interior Designer",
      pushback: "Do not call a room successful just because furniture fits on the plan. The report must judge comfort, visual calm, visitor arrival, and whether the best light supports real daily habits.",
      added: "The revised report leads with strengths, weaknesses, and moveable-furniture opportunities, then gives each room a practical use/light/furniture/improvement analysis including the sunroom, front door ambiguity, and deck use.",
      passedBy: "It now treats the lounge, sunroom, deck, and Bedroom 2 as lived-in places with competing demands, not just measured rectangles.",
    },
    {
      role: "Builder / Renovation Practicality",
      pushback: "Separate furniture changes from building issues. Do not imply structural work before checking whether movement, entry clarity, shade, and storage can be improved with lighter interventions.",
      added: "The report prioritises furniture simplification, circulation protection, door/opening clearance, a clearer front door sequence, and deck shade/wind control before recommending major redesign.",
      passedBy: "It flags constraints that matter to buildability: narrow hall, lounge openings, unclear original front door, kitchen/dining aisle, compact wet/service rooms, and seasonal sunroom comfort.",
    },
    {
      role: "Daylight And Movement Planner",
      pushback: "Daylight should be weighted by time of day, likely occupancy, thermal comfort, and outdoor usability. A bright laundry or unshaded deck is not equal to a comfortable living zone.",
      added: "The report now calls out the service-light mismatch, sunroom overheating/cold risk, deck shade problem, and includes a cropped theoretical movement map for two adults and a teenager.",
      passedBy: "It connects light, movement, room use, and seasonal comfort, especially where the lounge is a circulation junction with only moderate borrowed light.",
    },
  ];
}

function buildSnippets(rooms: ReviewRoom[], scenarioId: string): DesignReviewSnippet[] {
  const objectIdsForRooms = (roomIds: string[]) =>
    rooms
      .filter((room) => roomIds.includes(room.id))
      .flatMap((room) => room.objects.map((object) => object.id));

  if (scenarioId === "back-side-living-sunroom-bedroom") {
    return [
      {
        id: "design-2-new-day-room",
        title: "New Back-Side Living / Dining Room",
        body: "Shows the main Design 2 move: the bright back-side service/Bedroom 2 end becomes the everyday living and dining room.",
        viewBox: "750 470 245 160",
        focusRoomIds: ["future_living_dining_day_room"],
        highlightObjectIds: objectIdsForRooms(["future_living_dining_day_room"]),
      },
      {
        id: "design-2-bedroom-replacement",
        title: "Replacement Bedroom And Bedroom 2",
        body: "Shows the former sunroom rebuilt as a proper bedroom and the old lounge repurposed as Bedroom 2.",
        viewBox: "510 325 280 190",
        focusRoomIds: ["replacement_insulated_bedroom", "current_lounge_bedroom"],
        highlightObjectIds: objectIdsForRooms(["replacement_insulated_bedroom", "current_lounge_bedroom"]),
      },
      {
        id: "design-2-service-core",
        title: "Relocated Service Core",
        body: "Shows the high-risk part of the option: laundry, WC, bathroom, and storage need to work as separated service rooms.",
        viewBox: "625 500 180 130",
        focusRoomIds: ["relocated_service_rooms"],
        highlightObjectIds: objectIdsForRooms(["relocated_service_rooms"]),
      },
      {
        id: "design-2-kitchen-chill-edge",
        title: "Kitchen And Chill / Reading Edge",
        body: "Shows the retained renovated kitchen and the former dining strip becoming a quieter support space rather than the only living zone.",
        viewBox: "730 285 135 245",
        focusRoomIds: ["kitchen_dining", "kitchen_dining_chill_zone"],
        highlightObjectIds: objectIdsForRooms(["kitchen_dining", "kitchen_dining_chill_zone"]),
      },
    ];
  }

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
  const layout = data.furniture_layout.layout;
  const model = houseModelForScenario(data.house_model, layout.scenario_id, layout.plan_transform.px_per_m);
  const assignedObjects = assignObjects(layout, model);
  const offPlanObjects = assignedObjects.filter((object) => isOffPlan(object, layout));
  const unassignedObjects = assignedObjects.filter((object) => !object.roomId && !isOffPlan(object, layout));
  const rooms = buildRooms(model, assignedObjects);
  const lowLightRooms = lowWinterLightRooms(model, roomNameById(model));
  const serviceLightRooms = usefulLowUseLightRoomNames(model, rooms);
  const movementScenarios = buildMovementScenarios(model, layout.scenario_id);
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
    overallAssessment: buildOverallAssessment(rooms, metrics, serviceLightRooms, layout.scenario_id),
    summarySections: buildSummarySections(rooms, metrics, offPlanObjects, serviceLightRooms, layout.scenario_id),
    practicalFindings: buildPracticalFindings(rooms, lowLightRooms, serviceLightRooms),
    roomAnalyses: buildRoomAnalyses(rooms),
    movementMapViewBox: movementMapViewBox(layout, movementScenarios),
    movementScenarios,
    expertReview: buildExpertReview(),
    rooms,
    assignedObjects,
    offPlanObjects,
    unassignedObjects,
    dynamicWarnings: buildWarnings(rooms, offPlanObjects, lowLightRooms),
    reportSections: [
      ...buildScenarioReportSections(layout.scenario_id),
      ...buildReportSections(rooms, metrics),
    ],
    snippets: buildSnippets(rooms, layout.scenario_id),
    photoEvidence: photoEvidence(model),
  };
}
