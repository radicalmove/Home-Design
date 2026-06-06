import houseModel from "../../../../DATA/house_model.json";

export type PlanVectorPoint = [number, number];

export type PlanVectorShape =
  | {
      kind: "rect";
      x: number;
      y: number;
      width: number;
      height: number;
    }
  | {
      kind: "polygon";
      points: PlanVectorPoint[];
    }
  | {
      kind: "multi_polygon";
      polygons: PlanVectorPoint[][];
    };

export type PlanVectorRoom = {
  id: string;
  name: string;
  category: string;
  shape: PlanVectorShape;
};

export type PlanVectorSiteElement = {
  id: string;
  type: string;
  category: string;
  shape: PlanVectorShape;
};

export type PlanVectorFeature = {
  id: string;
  type: string;
  renderGroup: "window" | "door" | "opening";
  shape: PlanVectorShape;
};

export type PlanVectorWallShape =
  | {
      kind: "line";
      x1: number;
      y1: number;
      x2: number;
      y2: number;
    }
  | {
      kind: "path";
      d: string;
    };

export type PlanVectorWall = {
  id: string;
  shape: PlanVectorWallShape;
  thicknessPx: number;
};

export type PlanVectorModel = {
  rooms: PlanVectorRoom[];
  site: PlanVectorSiteElement[];
  features: PlanVectorFeature[];
  walls: PlanVectorWall[];
};

type DisplayRect = {
  type: "rect";
  x: number;
  y: number;
  width: number;
  height: number;
};

type DisplayPolygon = {
  type: "polygon";
  points: PlanVectorPoint[];
};

type DisplayMultiPolygon = {
  type: "multi_polygon";
  polygons: PlanVectorPoint[][];
};

type DisplayGeometry = DisplayRect | DisplayPolygon | DisplayMultiPolygon;

type SourceSpace = {
  id: string;
  name: string;
  category: string;
  display_px?: DisplayGeometry;
};

type SourceSiteElement = {
  id: string;
  type: string;
  category: string;
  display_px?: DisplayGeometry;
};

type SourceFeature = {
  id: string;
  type: string;
  display_px?: DisplayGeometry;
};

type SourceHouseModel = {
  current_structure: {
    spaces: SourceSpace[];
    features: SourceFeature[];
  };
  current_site: {
    elements: SourceSiteElement[];
  };
};

const WALL_THICKNESS_PX = {
  exterior: 8,
  thinExterior: 3.7,
  toiletExterior: 7.2,
  interior: 3.7,
  thinInterior: 3.3,
} as const;

const EXTERIOR_WALL_IDS = new Set([
  "lounge-exterior",
  "lounge-sunroom-wall",
  "lounge-sunroom-lower-wall",
  "master-sunroom-old-external-wall",
  "hallway-north-wall",
  "hallway-sunroom-right-jamb",
  "kitchen-dining-west-wall",
  "kitchen-dining-north-wall",
  "kitchen-dining-east-wall",
  "private-rooms-south-wall",
  "master-west-wall",
  "laundry-toilet-exterior",
]);

const THIN_EXTERIOR_WALL_IDS = new Set([
  "entrance-deck-wall-west",
  "entrance-deck-wall-east",
]);

const TOILET_EXTERIOR_WALL_IDS = new Set(["toilet-south-external-wall"]);

const THIN_INTERIOR_WALL_IDS = new Set([
  "kitchen-entrance-return-wall",
  "entrance-north-return-wall",
  "bedroom2-north-wall-west",
  "bedroom2-north-wall-east",
  "master-office-wall-upper",
  "master-office-wall-mid-upper",
  "master-office-wall-mid-lower",
  "master-office-wall-lower",
  "wardrobe-office-wall",
  "office-bathroom-wall",
  "bathroom-bedroom2-wall",
  "laundry-toilet-wall-west",
  "laundry-toilet-wall-east",
]);

const CURRENT_WALL_LINES: Array<{
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}> = [
  { id: "sunroom-west-frame", x1: 549.2, y1: 483.4, x2: 549.2, y2: 442.3 },
  { id: "sunroom-front-frame", x1: 549.2, y1: 442.3, x2: 568, y2: 442.3 },
  { id: "sunroom-east-frame", x1: 606, y1: 401.6, x2: 606, y2: 346.7 },
  { id: "sunroom-north-frame", x1: 606, y1: 346.7, x2: 663.1, y2: 346.7 },
  { id: "lounge-exterior", x1: 659.1, y1: 348.8, x2: 762.8, y2: 348.8 },
  { id: "lounge-sunroom-wall", x1: 663.1, y1: 348.8, x2: 663.1, y2: 377.8 },
  { id: "lounge-sunroom-lower-wall", x1: 663.1, y1: 460, x2: 663.1, y2: 484.6 },
  { id: "master-sunroom-old-external-wall", x1: 533.9, y1: 482.4, x2: 627.1, y2: 482.4 },
  { id: "hallway-north-wall", x1: 627.1, y1: 482.4, x2: 635.2, y2: 482.4 },
  { id: "hallway-sunroom-right-jamb", x1: 655.4, y1: 482.4, x2: 663.1, y2: 482.4 },
  { id: "lounge-hallway-wall-west", x1: 663.1, y1: 484.6, x2: 701.5, y2: 484.6 },
  { id: "lounge-hallway-wall-east", x1: 723.5, y1: 484.6, x2: 760.9, y2: 484.6 },
  { id: "kitchen-dining-west-wall", x1: 758.8, y1: 348.8, x2: 758.8, y2: 302.3 },
  { id: "kitchen-dining-north-wall", x1: 758.8, y1: 302.3, x2: 833, y2: 302.3 },
  { id: "kitchen-dining-east-wall", x1: 833, y1: 302.3, x2: 833, y2: 491.9 },
  { id: "entrance-deck-wall-west", x1: 834.3, y1: 489.1, x2: 841.9, y2: 489.1 },
  { id: "entrance-deck-wall-east", x1: 881.8, y1: 489.1, x2: 956.4, y2: 489.1 },
  { id: "kitchen-entrance-return-wall", x1: 834.3, y1: 489.1, x2: 834.3, y2: 495.9 },
  { id: "entrance-north-return-wall", x1: 834.3, y1: 495.9, x2: 803.7, y2: 495.9 },
  { id: "private-rooms-south-wall", x1: 533.9, y1: 601.8, x2: 902.8, y2: 601.8 },
  { id: "toilet-south-external-wall", x1: 900.6, y1: 602.2, x2: 960.4, y2: 602.2 },
  { id: "bedroom2-east-wall", x1: 902.8, y1: 516.1, x2: 902.8, y2: 602.2 },
  { id: "master-west-wall", x1: 533.9, y1: 482.4, x2: 533.9, y2: 601.8 },
  { id: "kitchen-lounge-nub", x1: 760.9, y1: 348.8, x2: 760.9, y2: 361.3 },
  { id: "lounge-kitchen-divider", x1: 760.9, y1: 392.4, x2: 760.9, y2: 493 },
  { id: "hallway-south-wall-west", x1: 627.1, y1: 523, x2: 695.5, y2: 523 },
  { id: "hallway-south-wall-centre", x1: 717.3, y1: 523, x2: 727.1, y2: 523 },
  { id: "hallway-south-wall-east", x1: 743.4, y1: 523, x2: 773.9, y2: 523 },
  { id: "hallway-kitchen-door-wall", x1: 760.9, y1: 515, x2: 760.9, y2: 523 },
  { id: "bedroom2-north-wall-west", x1: 773.9, y1: 523.3, x2: 778.6, y2: 523.3 },
  { id: "bedroom2-north-wall-east", x1: 800.6, y1: 523.3, x2: 902.8, y2: 523.3 },
  { id: "master-office-wall-upper", x1: 627.1, y1: 482.4, x2: 627.1, y2: 494 },
  { id: "master-office-wall-mid-upper", x1: 627.1, y1: 516, x2: 627.1, y2: 527 },
  { id: "master-office-wall-mid-lower", x1: 627.1, y1: 558, x2: 627.1, y2: 567 },
  { id: "master-office-wall-lower", x1: 627.1, y1: 598, x2: 627.1, y2: 601.8 },
  { id: "wardrobe-office-wall", x1: 646.8, y1: 523, x2: 646.8, y2: 601.8 },
  { id: "office-bathroom-wall", x1: 727.1, y1: 521.2, x2: 727.1, y2: 601.8 },
  { id: "bathroom-bedroom2-wall", x1: 773.9, y1: 523, x2: 773.9, y2: 601.8 },
  { id: "entrance-laundry-wall", x1: 902.8, y1: 489.1, x2: 902.8, y2: 496.5 },
  { id: "laundry-toilet-wall-west", x1: 902.8, y1: 572.9, x2: 908.8, y2: 572.9 },
  { id: "laundry-toilet-wall-east", x1: 924.8, y1: 572.9, x2: 956.4, y2: 572.9 },
  { id: "kitchen-entrance-door-wall-upper", x1: 803.7, y1: 495.9, x2: 803.7, y2: 499.7 },
  { id: "kitchen-entrance-door-wall-lower", x1: 803.7, y1: 519.5, x2: 803.7, y2: 523.3 },
  { id: "laundry-toilet-exterior", x1: 956.4, y1: 487.3, x2: 956.4, y2: 602.2 },
];

function wallThicknessForId(wallId: string): number {
  if (EXTERIOR_WALL_IDS.has(wallId)) {
    return WALL_THICKNESS_PX.exterior;
  }
  if (THIN_EXTERIOR_WALL_IDS.has(wallId)) {
    return WALL_THICKNESS_PX.thinExterior;
  }
  if (TOILET_EXTERIOR_WALL_IDS.has(wallId)) {
    return WALL_THICKNESS_PX.toiletExterior;
  }
  if (THIN_INTERIOR_WALL_IDS.has(wallId)) {
    return WALL_THICKNESS_PX.thinInterior;
  }
  return WALL_THICKNESS_PX.interior;
}

function currentWalls(): PlanVectorWall[] {
  return CURRENT_WALL_LINES.map((wall) => ({
    id: wall.id,
    shape: {
      kind: "line",
      x1: wall.x1,
      y1: wall.y1,
      x2: wall.x2,
      y2: wall.y2,
    },
    thicknessPx: wallThicknessForId(wall.id),
  }));
}

function displayGeometryToShape(display: DisplayGeometry): PlanVectorShape {
  if (display.type === "rect") {
    return {
      kind: "rect",
      x: display.x,
      y: display.y,
      width: display.width,
      height: display.height,
    };
  }

  if (display.type === "multi_polygon") {
    return {
      kind: "multi_polygon",
      polygons: display.polygons,
    };
  }

  return {
    kind: "polygon",
    points: display.points,
  };
}

function featureRenderGroup(type: string): PlanVectorFeature["renderGroup"] {
  if (type === "window" || type === "window_group") {
    return "window";
  }
  if (type === "opening") {
    return "opening";
  }
  return "door";
}

function buildPlanVectorModel(model: SourceHouseModel): PlanVectorModel {
  return {
    rooms: model.current_structure.spaces
      .filter((space) => Boolean(space.display_px))
      .map((space) => ({
        id: space.id,
        name: space.name,
        category: space.category,
        shape: displayGeometryToShape(space.display_px as DisplayGeometry),
      })),
    site: model.current_site.elements
      .filter((element) => Boolean(element.display_px))
      .map((element) => ({
        id: element.id,
        type: element.type,
        category: element.category,
        shape: displayGeometryToShape(element.display_px as DisplayGeometry),
      })),
    features: model.current_structure.features
      .filter((feature) => Boolean(feature.display_px))
      .map((feature) => ({
        id: feature.id,
        type: feature.type,
        renderGroup: featureRenderGroup(feature.type),
        shape: displayGeometryToShape(feature.display_px as DisplayGeometry),
      })),
    walls: currentWalls(),
  };
}

const DESIGN_2_REMOVED_ROOM_IDS = new Set([
  "sunroom",
  "lounge",
  "office",
  "bathroom",
  "bedroom_2",
  "laundry",
  "toilet",
  "entrance",
]);

const DESIGN_2_REPLACEMENT_ROOMS: PlanVectorRoom[] = [
  {
    id: "future_living_dining_day_room",
    name: "Living / Dining Day Room",
    category: "living",
    shape: {
      kind: "polygon",
      points: [
        [803.7, 489.1],
        [956.4, 489.1],
        [956.4, 602.2],
        [773.9, 602.2],
        [773.9, 523],
        [803.7, 523],
      ],
    },
  },
  {
    id: "kitchen_dining_chill_zone",
    name: "Kitchen Chill / Reading Edge",
    category: "living",
    shape: {
      kind: "polygon",
      points: [
        [758.8, 302.3],
        [833, 302.3],
        [833, 489.1],
        [834.3, 489.1],
        [834.3, 495.9],
        [803.7, 495.9],
        [803.7, 523.3],
        [760.9, 523],
        [760.9, 348.8],
        [758.8, 348.8],
      ],
    },
  },
  {
    id: "replacement_insulated_bedroom",
    name: "Replacement Bedroom",
    category: "bedroom",
    shape: {
      kind: "rect",
      x: 533.9,
      y: 348.8,
      width: 129.2,
      height: 133.6,
    },
  },
  {
    id: "relocated_service_rooms",
    name: "Separated Laundry / WC Service Rooms",
    category: "wet",
    shape: {
      kind: "rect",
      x: 646.8,
      y: 523,
      width: 127.1,
      height: 78.8,
    },
  },
  {
    id: "current_lounge_bedroom",
    name: "Current Lounge Bedroom",
    category: "bedroom",
    shape: {
      kind: "rect",
      x: 659.1,
      y: 348.8,
      width: 101.8,
      height: 133.6,
    },
  },
];

const DESIGN_2_REMOVED_WALL_IDS = new Set([
  "sunroom-west-frame",
  "sunroom-front-frame",
  "sunroom-east-frame",
  "sunroom-north-frame",
  "lounge-sunroom-wall",
  "lounge-sunroom-lower-wall",
  "bedroom2-east-wall",
  "bedroom2-north-wall-east",
  "kitchen-entrance-return-wall",
  "entrance-north-return-wall",
  "entrance-laundry-wall",
  "hallway-kitchen-door-wall",
  "kitchen-entrance-door-wall-upper",
  "kitchen-entrance-door-wall-lower",
  "laundry-toilet-wall-west",
  "laundry-toilet-wall-east",
]);

const DESIGN_2_ADDED_WALLS: PlanVectorWall[] = [
  {
    id: "replacement-bedroom-envelope",
    shape: {
      kind: "path",
      d: "M 533.9 482.4 L 533.9 348.8 L 663.1 348.8 L 663.1 482.4 M 533.9 482.4 L 635.2 482.4 M 655.4 482.4 L 663.1 482.4",
    },
    thicknessPx: 8,
  },
  {
    id: "lounge-bedroom-chill-wall-infill",
    shape: {
      kind: "line",
      x1: 760.9,
      y1: 361.3,
      x2: 760.9,
      y2: 392.4,
    },
    thicknessPx: WALL_THICKNESS_PX.interior,
  },
  {
    id: "bathroom-laundry-divider",
    shape: {
      kind: "line",
      x1: 727.1,
      y1: 523,
      x2: 727.1,
      y2: 601.8,
    },
    thicknessPx: WALL_THICKNESS_PX.interior,
  },
];

const DESIGN_2_REMOVED_FEATURE_IDS = new Set([
  "sunroom_lounge_slider",
  "sunroom_wraparound_glazing",
  "sunroom_front_double_doors",
  "laundry_north_window",
  "laundry_east_window",
  "toilet_frosted_window",
  "entrance_deck_slider",
  "entrance_to_laundry_opening",
  "laundry_to_toilet_door",
  "kitchen_dining_to_bedroom2_door",
  "entrance_to_kitchen_dining_door",
  "lounge_to_kitchen_dining",
]);

const DESIGN_2_ADDED_FEATURES: PlanVectorFeature[] = [
  {
    id: "future_front_door",
    type: "door",
    renderGroup: "door",
    shape: {
      kind: "polygon",
      points: [
        [881, 486.6],
        [898, 486.6],
        [898, 491.6],
        [881, 491.6],
      ],
    },
  },
  {
    id: "future_wet_core_office_south_window",
    type: "window",
    renderGroup: "window",
    shape: {
      kind: "polygon",
      points: [
        [672.8, 597.8],
        [701.1, 597.8],
        [701.1, 605.8],
        [672.8, 605.8],
      ],
    },
  },
  {
    id: "future_wet_core_bathroom_south_window",
    type: "window",
    renderGroup: "window",
    shape: {
      kind: "polygon",
      points: [
        [735.9, 597.8],
        [765.1, 597.8],
        [765.1, 605.8],
        [735.9, 605.8],
      ],
    },
  },
  {
    id: "future_main_lounge_south_window",
    type: "window",
    renderGroup: "window",
    shape: {
      kind: "polygon",
      points: [
        [811.7, 597.8],
        [864.8, 597.8],
        [864.8, 605.8],
        [811.7, 605.8],
      ],
    },
  },
  {
    id: "future_day_room_east_full_height_window",
    type: "window",
    renderGroup: "window",
    shape: {
      kind: "polygon",
      points: [
        [952.4, 514.3],
        [960.4, 514.3],
        [960.4, 543.5],
        [952.4, 543.5],
      ],
    },
  },
  {
    id: "future_main_entry_west_floor_window",
    type: "window",
    renderGroup: "window",
    shape: {
      kind: "polygon",
      points: [
        [846, 485.1],
        [854, 485.1],
        [854, 493.1],
        [846, 493.1],
      ],
    },
  },
  {
    id: "future_main_entry_east_floor_window",
    type: "window",
    renderGroup: "window",
    shape: {
      kind: "polygon",
      points: [
        [902, 485.1],
        [910, 485.1],
        [910, 493.1],
        [902, 493.1],
      ],
    },
  },
  {
    id: "future_old_laundry_north_floor_window",
    type: "window",
    renderGroup: "window",
    shape: {
      kind: "polygon",
      points: [
        [914, 485.1],
        [950.6, 485.1],
        [950.6, 493.1],
        [914, 493.1],
      ],
    },
  },
];

function design2PlanVectorModel(): PlanVectorModel {
  return {
    rooms: [
      ...currentPlanVectorModel.rooms.filter((room) => !DESIGN_2_REMOVED_ROOM_IDS.has(room.id)),
      ...DESIGN_2_REPLACEMENT_ROOMS,
    ],
    site: currentPlanVectorModel.site,
    features: [
      ...currentPlanVectorModel.features.filter((feature) => !DESIGN_2_REMOVED_FEATURE_IDS.has(feature.id)),
      ...DESIGN_2_ADDED_FEATURES,
    ],
    walls: [
      ...currentPlanVectorModel.walls.filter((wall) => !DESIGN_2_REMOVED_WALL_IDS.has(wall.id)),
      ...DESIGN_2_ADDED_WALLS,
    ],
  };
}

export function polygonPath(points: PlanVectorPoint[]): string {
  const [firstPoint, ...remainingPoints] = points;
  if (!firstPoint) {
    return "";
  }

  return [
    `M ${firstPoint[0]} ${firstPoint[1]}`,
    ...remainingPoints.map((point) => `L ${point[0]} ${point[1]}`),
    "Z",
  ].join(" ");
}

export const currentPlanVectorModel = buildPlanVectorModel(houseModel as unknown as SourceHouseModel);

export function planVectorModelForScenario(scenarioId: string | null | undefined): PlanVectorModel {
  if (scenarioId === "back-side-living-sunroom-bedroom") {
    return design2PlanVectorModel();
  }
  return currentPlanVectorModel;
}
