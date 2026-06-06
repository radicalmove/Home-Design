import {
  CURRENT_SCENARIO_ID,
} from "./designScenarios";
import {
  currentPlanVectorModel,
  planVectorModelForScenario,
  type PlanVectorFeature,
  type PlanVectorModel,
  type PlanVectorRoom,
  type PlanVectorShape,
  type PlanVectorSiteElement,
} from "./planVectorModel";

type JsonRecord = Record<string, unknown>;

type DisplayGeometry =
  | { type: "rect"; x: number; y: number; width: number; height: number }
  | { type: "polygon"; points: number[][] }
  | { type: "multi_polygon"; polygons: number[][][] };

type ScenarioFeatureMetadata = {
  room?: string;
  between?: string[];
  swing?: string;
  window_context?: string;
  wall_id?: string;
  width_m?: number;
  height_m?: number;
};

const SCENARIO_FEATURE_METADATA: Record<string, ScenarioFeatureMetadata> = {
  future_front_door: {
    between: ["future_living_dining_day_room", "deck"],
    swing: "closed_glazed_entry",
    wall_id: "plan-vector-wall:entrance-deck-wall-east",
    width_m: 0.68,
    height_m: 2.05,
  },
  lounge_north_left_window: {
    room: "current_lounge_bedroom",
    width_m: 0.42,
    height_m: 1.08,
  },
  lounge_north_right_window: {
    room: "current_lounge_bedroom",
    width_m: 0.42,
    height_m: 1.08,
  },
  deck_side_dining_window: {
    room: "kitchen_dining_chill_zone",
    wall_id: "plan-vector-wall:kitchen-dining-east-wall",
    width_m: 0.57,
    height_m: 1.08,
  },
  dining_west_window: {
    room: "kitchen_dining_chill_zone",
    wall_id: "plan-vector-wall:kitchen-dining-west-wall",
    width_m: 0.66,
    height_m: 1.08,
  },
  future_wet_core_office_south_window: {
    room: "relocated_service_rooms",
    width_m: 1.05,
    height_m: 0.85,
  },
  future_wet_core_bathroom_south_window: {
    room: "relocated_service_rooms",
    width_m: 1.08,
    height_m: 0.85,
  },
  future_main_lounge_south_window: {
    room: "future_living_dining_day_room",
    width_m: 1.95,
    height_m: 1.15,
  },
  future_day_room_east_full_height_window: {
    room: "future_living_dining_day_room",
    width_m: 1.05,
    height_m: 2.2,
  },
  future_main_entry_west_floor_window: {
    room: "future_living_dining_day_room",
    wall_id: "plan-vector-wall:entrance-deck-wall-west",
    width_m: 0.3,
    height_m: 1.95,
  },
  future_main_entry_east_floor_window: {
    room: "future_living_dining_day_room",
    wall_id: "plan-vector-wall:entrance-deck-wall-east",
    width_m: 0.3,
    height_m: 1.95,
  },
  future_old_laundry_north_floor_window: {
    room: "future_living_dining_day_room",
    width_m: 1.35,
    height_m: 1.08,
  },
};

const SCENARIO_REMOVED_OPENING_IDS: Record<string, Set<string>> = {
  "back-side-living-sunroom-bedroom": new Set([
    "lounge_to_kitchen_dining",
  ]),
};

const DESIGN_2_DAYLIGHT_ROOM_NOTES: Record<string, string> = {
  future_living_dining_day_room:
    "Back-side living gains the useful morning and early-afternoon light previously landing in entrance, laundry, toilet, and Bedroom 2.",
  kitchen_dining_chill_zone:
    "The renovated kitchen stays put while the former dining strip becomes a quieter reading or overflow sitting edge.",
  replacement_insulated_bedroom:
    "Replacement bedroom uses the former sunroom position, so glazing, insulation, heating, cooling, and privacy treatments matter.",
  relocated_service_rooms:
    "Service functions move away from the brightest back-side wall; artificial task lighting and ventilation become more important here.",
  current_lounge_bedroom:
    "The current lounge becomes a private bedroom with a new larger north window and less through-traffic pressure.",
};

function asRecord(value: unknown): JsonRecord {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? value as JsonRecord
    : {};
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function shapeToDisplayGeometry(shape: PlanVectorShape): DisplayGeometry {
  if (shape.kind === "rect") {
    return {
      type: "rect",
      x: shape.x,
      y: shape.y,
      width: shape.width,
      height: shape.height,
    };
  }
  if (shape.kind === "multi_polygon") {
    return {
      type: "multi_polygon",
      polygons: shape.polygons,
    };
  }
  return {
    type: "polygon",
    points: shape.points,
  };
}

function shapeBounds(shape: PlanVectorShape): { widthPx: number; heightPx: number } {
  if (shape.kind === "rect") {
    return { widthPx: shape.width, heightPx: shape.height };
  }
  const points = shape.kind === "polygon" ? shape.points : shape.polygons.flatMap((polygon) => polygon);
  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  return {
    widthPx: Math.max(...xs) - Math.min(...xs),
    heightPx: Math.max(...ys) - Math.min(...ys),
  };
}

function roomDefinitionFromVectorRoom(room: PlanVectorRoom, pxPerM: number, existingRooms: Map<string, JsonRecord>): JsonRecord {
  const existingRoom = existingRooms.get(room.id);
  if (existingRoom) {
    return {
      ...existingRoom,
      name: room.name,
      category: room.category,
    };
  }

  const bounds = shapeBounds(room.shape);
  return {
    id: room.id,
    name: room.name,
    category: room.category,
    confidence: "scenario-concept",
    dimensions_m: {
      length: bounds.heightPx / pxPerM,
      width: bounds.widthPx / pxPerM,
      height: 2.4,
    },
    notes: [`Scenario room generated from the Design 2 final 2D plan geometry.`],
  };
}

function spaceFromVectorRoom(room: PlanVectorRoom): JsonRecord {
  return {
    id: room.id,
    name: room.name,
    category: room.category,
    display_px: shapeToDisplayGeometry(room.shape),
  };
}

function siteFromVectorElement(element: PlanVectorSiteElement): JsonRecord {
  return {
    id: element.id,
    type: element.type,
    category: element.category,
    display_px: shapeToDisplayGeometry(element.shape),
  };
}

function featureFromVectorFeature(feature: PlanVectorFeature): JsonRecord {
  return {
    id: feature.id,
    type: feature.type,
    render_group: feature.renderGroup,
    display_px: shapeToDisplayGeometry(feature.shape),
    ...(SCENARIO_FEATURE_METADATA[feature.id] ?? {}),
  };
}

function topLevelOpeningsForScenario(model: JsonRecord, scenarioId: string | null | undefined): unknown[] {
  const removedIds = scenarioId ? SCENARIO_REMOVED_OPENING_IDS[scenarioId] : undefined;
  if (!removedIds) {
    return asArray(model.openings);
  }
  return asArray(model.openings).filter((openingValue) => {
    const opening = asRecord(openingValue);
    const id = opening.id;
    return typeof id !== "string" || !removedIds.has(id);
  });
}

function daylightEntryForRoom(room: PlanVectorRoom): JsonRecord {
  const note = DESIGN_2_DAYLIGHT_ROOM_NOTES[room.id] ?? "Scenario room daylight has not been separately modelled yet.";
  if (room.id === "future_living_dining_day_room") {
    return {
      summer: { morning: "high", midday: "medium", afternoon: "medium" },
      autumn: { morning: "medium", midday: "medium", afternoon: "low" },
      winter: { morning: "medium", midday: "low", afternoon: "low" },
      spring: { morning: "high", midday: "medium", afternoon: "medium" },
      notes: note,
    };
  }
  if (room.id === "replacement_insulated_bedroom") {
    return {
      summer: { morning: "high", midday: "medium", afternoon: "medium" },
      autumn: { morning: "medium", midday: "medium", afternoon: "medium" },
      winter: { morning: "medium", midday: "medium", afternoon: "low" },
      spring: { morning: "high", midday: "medium", afternoon: "medium" },
      notes: note,
    };
  }
  return {
    summer: { morning: "medium", midday: "medium", afternoon: "low" },
    autumn: { morning: "medium", midday: "low", afternoon: "low" },
    winter: { morning: "low", midday: "low", afternoon: "low" },
    spring: { morning: "medium", midday: "medium", afternoon: "low" },
    notes: note,
  };
}

function scenarioDaylightRooms(planModel: PlanVectorModel, originalModel: JsonRecord): JsonRecord {
  const originalRooms = asRecord(asRecord(asRecord(originalModel.daylight).rooms));
  return Object.fromEntries(
    planModel.rooms.map((room) => [
      room.id,
      originalRooms[room.id] ?? daylightEntryForRoom(room),
    ]),
  );
}

function scenarioRooms(model: JsonRecord, planModel: PlanVectorModel, pxPerM: number): JsonRecord[] {
  const originalRooms = new Map(
    asArray(model.rooms)
      .map(asRecord)
      .map((room) => [String(room.id ?? ""), room] as const)
      .filter(([id]) => id.length > 0),
  );
  return planModel.rooms.map((room) => roomDefinitionFromVectorRoom(room, pxPerM, originalRooms));
}

export function houseModelForScenario(
  houseModel: unknown,
  scenarioId: string | null | undefined,
  pxPerM: number,
): JsonRecord {
  const model = asRecord(houseModel);
  if (!scenarioId || scenarioId === CURRENT_SCENARIO_ID) {
    return model;
  }

  const planModel = planVectorModelForScenario(scenarioId);
  if (planModel === currentPlanVectorModel) {
    return model;
  }

  const currentStructure = asRecord(model.current_structure);
  return {
    ...model,
    rooms: scenarioRooms(model, planModel, pxPerM),
    openings: topLevelOpeningsForScenario(model, scenarioId),
    current_structure: {
      ...currentStructure,
      spaces: planModel.rooms.map(spaceFromVectorRoom),
      features: planModel.features.map(featureFromVectorFeature),
      built_ins: asArray(currentStructure.built_ins),
    },
    current_site: {
      ...asRecord(model.current_site),
      elements: planModel.site.map(siteFromVectorElement),
    },
    daylight: {
      ...asRecord(model.daylight),
      rooms: scenarioDaylightRooms(planModel, model),
    },
  };
}

export function isScenarioHouseModelAvailable(scenarioId: string | null | undefined): boolean {
  return Boolean(scenarioId)
    && scenarioId !== CURRENT_SCENARIO_ID
    && planVectorModelForScenario(scenarioId) !== currentPlanVectorModel;
}
