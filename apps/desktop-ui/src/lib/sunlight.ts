type PlanVector = {
  x: number;
  y: number;
};

type RectGeometry = {
  type: "rect";
  x: number;
  y: number;
  width: number;
  height: number;
};

type PolygonGeometry = {
  type: "polygon";
  points: Array<[number, number]>;
};

type MultiPolygonGeometry = {
  type: "multi_polygon";
  polygons: Array<Array<[number, number]>>;
};

type RoomGeometry = RectGeometry | PolygonGeometry | MultiPolygonGeometry;

type SunlightRoom = {
  id: string;
  geometry: RoomGeometry;
};

type SunlightLine = {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  admit_direction?: PlanVector;
  room_directions?: Array<{ room: string } & PlanVector>;
};

type SunlightEntry = {
  id: string;
  kind: "external" | "internal";
  room: string | null;
  centerlines: SunlightLine[];
};

export type SunlightYearPoint = {
  index: number;
  month: number;
  day: number;
  label: string;
};

export type SunlightRoomClip = {
  id: string;
  path: string;
};

export type SunlightRay = {
  id: string;
  className: "sunlight-ray" | "sunlight-ray borrowed";
  path: string;
  clipId: string | null;
};

export type SunlightSunMarker = {
  pathCx: number;
  pathCy: number;
  pathRx: number;
  pathRy: number;
  sunX: number;
  sunY: number;
  sunRadius: number;
};

export type SunlightOverlayModel = {
  yearPoint: SunlightYearPoint;
  timeLabel: string;
  status: string;
  darkOpacity: number;
  roomClips: SunlightRoomClip[];
  rays: SunlightRay[];
  sunMarker: SunlightSunMarker | null;
};

export const SUNLIGHT_YEAR_POINTS: SunlightYearPoint[] = [
  { index: 0, month: 6, day: 21, label: "Winter Jun" },
  { index: 1, month: 7, day: 14, label: "Winter Jul" },
  { index: 2, month: 8, day: 6, label: "Winter Aug" },
  { index: 3, month: 8, day: 29, label: "Late Winter Aug" },
  { index: 4, month: 9, day: 21, label: "Spring Sep" },
  { index: 5, month: 10, day: 14, label: "Spring Oct" },
  { index: 6, month: 11, day: 6, label: "Spring Nov" },
  { index: 7, month: 11, day: 29, label: "Late Spring Nov" },
  { index: 8, month: 12, day: 21, label: "Summer Dec" },
  { index: 9, month: 1, day: 14, label: "Summer Jan" },
  { index: 10, month: 2, day: 6, label: "Summer Feb" },
  { index: 11, month: 2, day: 28, label: "Late Summer Feb" },
  { index: 12, month: 3, day: 21, label: "Autumn Mar" },
  { index: 13, month: 4, day: 14, label: "Autumn Apr" },
  { index: 14, month: 5, day: 7, label: "Autumn May" },
  { index: 15, month: 5, day: 30, label: "Late Autumn May" },
];

export const SUNLIGHT_TIME_SLIDER = {
  startMinutes: 240,
  endMinutes: 1320,
  stepMinutes: 30,
};

const CHRISTCHURCH = {
  latitude: -43.53333,
  longitude: 172.63333,
};

const PLAN_RIGHT_BEARING_DEGREES = 52.5;

const SUNLIGHT_ROOMS: SunlightRoom[] = [
  {
    id: "sunroom",
    geometry: {
      type: "polygon",
      points: [
        [549.2, 483.4],
        [667.1, 483.4],
        [667.1, 346.7],
        [606, 346.7],
        [606, 401.6],
        [568, 442.3],
        [549.2, 442.3],
        [549.2, 483.4],
      ],
    },
  },
  { id: "lounge", geometry: { type: "rect", x: 659.1, y: 348.8, width: 101.8, height: 133.6 } },
  {
    id: "kitchen_dining",
    geometry: {
      type: "polygon",
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
    id: "entrance",
    geometry: {
      type: "polygon",
      points: [
        [803.7, 495.9],
        [834.3, 495.9],
        [834.3, 489.1],
        [902.8, 489.1],
        [902.8, 523.3],
        [803.7, 523.3],
      ],
    },
  },
  { id: "laundry", geometry: { type: "rect", x: 902.8, y: 489.1, width: 53.6, height: 83.8 } },
  { id: "toilet", geometry: { type: "rect", x: 902.8, y: 572.9, width: 53.6, height: 29.3 } },
  {
    id: "hallway",
    geometry: {
      type: "polygon",
      points: [
        [627.1, 482.4],
        [760.9, 482.4],
        [760.9, 523],
        [627.1, 523],
      ],
    },
  },
  { id: "master_bedroom", geometry: { type: "rect", x: 533.9, y: 482.4, width: 93.2, height: 119.4 } },
  { id: "office", geometry: { type: "rect", x: 646.8, y: 523, width: 80.3, height: 78.8 } },
  { id: "bathroom", geometry: { type: "rect", x: 727.1, y: 523, width: 46.8, height: 78.8 } },
  { id: "bedroom_2", geometry: { type: "rect", x: 773.9, y: 523, width: 128.9, height: 78.8 } },
];

const SUNLIGHT_LIGHT_ENTRIES: SunlightEntry[] = [
  {
    id: "sunroom_lounge_slider",
    kind: "internal",
    room: null,
    centerlines: [
      {
        x1: 664.6,
        y1: 377.8,
        x2: 664.6,
        y2: 460,
        room_directions: [
          { room: "sunroom", x: -1, y: 0 },
          { room: "lounge", x: 1, y: 0 },
        ],
      },
    ],
  },
  {
    id: "sunroom_wraparound_glazing",
    kind: "external",
    room: "sunroom",
    centerlines: [
      { x1: 655.2, y1: 346.7, x2: 610, y2: 346.7, admit_direction: { x: 0, y: 1 } },
      { x1: 606, y1: 354.7, x2: 606, y2: 393.6, admit_direction: { x: -1, y: 0 } },
      { x1: 568, y1: 442.3, x2: 549.2, y2: 442.3, admit_direction: { x: 0, y: -1 } },
      { x1: 549.2, y1: 446.3, x2: 549.2, y2: 477.9, admit_direction: { x: 1, y: 0 } },
    ],
  },
  {
    id: "sunroom_front_double_doors",
    kind: "external",
    room: "sunroom",
    centerlines: [
      { x1: 606, y1: 401.6, x2: 568, y2: 442.3, admit_direction: { x: 0.7309, y: 0.6824 } },
    ],
  },
  {
    id: "lounge_north_left_window",
    kind: "external",
    room: "lounge",
    centerlines: [
      { x1: 687.2, y1: 351.8, x2: 675.8, y2: 351.8, admit_direction: { x: 0, y: 1 } },
    ],
  },
  {
    id: "lounge_north_right_window",
    kind: "external",
    room: "lounge",
    centerlines: [
      { x1: 742.7, y1: 351.8, x2: 731.3, y2: 351.8, admit_direction: { x: 0, y: 1 } },
    ],
  },
  {
    id: "deck_door_group",
    kind: "external",
    room: "kitchen_dining",
    centerlines: [
      { x1: 837, y1: 350.8, x2: 837, y2: 393.8, admit_direction: { x: -1, y: 0 } },
    ],
  },
  {
    id: "deck_side_dining_window",
    kind: "external",
    room: "kitchen_dining",
    centerlines: [
      { x1: 836, y1: 332.5, x2: 836, y2: 347.7, admit_direction: { x: -1, y: 0 } },
    ],
  },
  {
    id: "dining_west_window",
    kind: "external",
    room: "kitchen_dining",
    centerlines: [
      { x1: 761.8, y1: 316.8, x2: 761.8, y2: 334.3, admit_direction: { x: 1, y: 0 } },
    ],
  },
  {
    id: "entrance_deck_slider",
    kind: "external",
    room: "entrance",
    centerlines: [
      { x1: 881.8, y1: 492.1, x2: 841.9, y2: 492.1, admit_direction: { x: 0, y: 1 } },
    ],
  },
  {
    id: "laundry_north_window",
    kind: "external",
    room: "laundry",
    centerlines: [
      { x1: 914, y1: 489.1, x2: 950.6, y2: 489.1, admit_direction: { x: 0, y: 1 } },
    ],
  },
  {
    id: "laundry_east_window",
    kind: "external",
    room: "laundry",
    centerlines: [
      { x1: 954.4, y1: 514.3, x2: 954.4, y2: 543.5, admit_direction: { x: -1, y: 0 } },
    ],
  },
  {
    id: "toilet_frosted_window",
    kind: "external",
    room: "toilet",
    centerlines: [
      { x1: 954.4, y1: 580.7, x2: 954.4, y2: 594.4, admit_direction: { x: -1, y: 0 } },
    ],
  },
  {
    id: "master_street_window",
    kind: "external",
    room: "master_bedroom",
    centerlines: [
      { x1: 537.9, y1: 514, x2: 537.9, y2: 571, admit_direction: { x: 1, y: 0 } },
    ],
  },
  {
    id: "master_sunroom_window",
    kind: "internal",
    room: null,
    centerlines: [
      {
        x1: 608.9,
        y1: 485.4,
        x2: 552.1,
        y2: 485.4,
        room_directions: [
          { room: "sunroom", x: 0, y: -1 },
          { room: "master_bedroom", x: 0, y: 1 },
        ],
      },
    ],
  },
  {
    id: "master_rear_high_window",
    kind: "external",
    room: "master_bedroom",
    centerlines: [
      { x1: 589.6, y1: 598.8, x2: 571.4, y2: 598.8, admit_direction: { x: 0, y: -1 } },
    ],
  },
  {
    id: "office_se_window",
    kind: "external",
    room: "office",
    centerlines: [
      { x1: 701.1, y1: 598.8, x2: 672.8, y2: 598.8, admit_direction: { x: 0, y: -1 } },
    ],
  },
  {
    id: "bathroom_se_window",
    kind: "external",
    room: "bathroom",
    centerlines: [
      { x1: 765.1, y1: 598.8, x2: 735.9, y2: 598.8, admit_direction: { x: 0, y: -1 } },
    ],
  },
  {
    id: "bedroom2_se_window",
    kind: "external",
    room: "bedroom_2",
    centerlines: [
      { x1: 864.8, y1: 598.8, x2: 811.7, y2: 598.8, admit_direction: { x: 0, y: -1 } },
    ],
  },
  {
    id: "bedroom2_entrance_internal_window",
    kind: "internal",
    room: null,
    centerlines: [
      {
        x1: 878.7,
        y1: 523.3,
        x2: 854.4,
        y2: 523.3,
        room_directions: [
          { room: "bedroom_2", x: 0, y: 1 },
          { room: "entrance", x: 0, y: -1 },
        ],
      },
    ],
  },
];

const ROOM_CLIPS: SunlightRoomClip[] = SUNLIGHT_ROOMS.map((room) => ({
  id: roomClipId(room.id),
  path: geometryPath(room.geometry),
}));

export function sunlightYearPointAt(index: number): SunlightYearPoint {
  const clamped = Math.min(SUNLIGHT_YEAR_POINTS.length - 1, Math.max(0, Math.round(index)));
  return SUNLIGHT_YEAR_POINTS[clamped];
}

export function formatSunlightMinutes(minutes: number): string {
  const clamped = Math.min(SUNLIGHT_TIME_SLIDER.endMinutes, Math.max(SUNLIGHT_TIME_SLIDER.startMinutes, minutes));
  const hours = Math.floor(clamped / 60);
  const mins = clamped % 60;
  return `${String(hours).padStart(2, "0")}:${String(mins).padStart(2, "0")}`;
}

export function sunlightOverlayForPlan({
  yearIndex,
  timeMinutes,
}: {
  yearIndex: number;
  timeMinutes: number;
}): SunlightOverlayModel {
  const yearPoint = sunlightYearPointAt(yearIndex);
  const position = solarPosition(yearPoint, timeMinutes);
  const timeLabel = formatSunlightMinutes(timeMinutes);

  if (position.elevation <= 0) {
    return {
      yearPoint,
      timeLabel,
      status: "No direct natural light",
      darkOpacity: 0.68,
      roomClips: ROOM_CLIPS,
      rays: [],
      sunMarker: null,
    };
  }

  const sunVector = azimuthToPlanVector(position.azimuth, PLAN_RIGHT_BEARING_DEGREES);
  const lightVector = { x: -sunVector.x, y: -sunVector.y };
  return {
    yearPoint,
    timeLabel,
    status: `Az ${Math.round(position.azimuth)} deg / El ${Math.round(position.elevation)} deg`,
    darkOpacity: 0.42,
    roomClips: ROOM_CLIPS,
    rays: sunlightRays(lightVector, position.elevation),
    sunMarker: sunMarker(sunVector, position.elevation),
  };
}

function solarPosition(
  yearPoint: Pick<SunlightYearPoint, "month" | "day">,
  localMinutes: number,
): { azimuth: number; elevation: number } {
  const rad = Math.PI / 180;
  const dayOfYear = dayOfYearForMonthDay(yearPoint.month, yearPoint.day);
  const timezoneOffsetHours = daylightSavingMonth(yearPoint.month) ? 13 : 12;
  const gamma = 2 * Math.PI / 365 * (dayOfYear - 1 + (localMinutes - 720) / 1440);
  const equationOfTime = 229.18 * (
    0.000075 + 0.001868 * Math.cos(gamma) - 0.032077 * Math.sin(gamma)
    - 0.014615 * Math.cos(2 * gamma) - 0.040849 * Math.sin(2 * gamma)
  );
  const declination = (
    0.006918 - 0.399912 * Math.cos(gamma) + 0.070257 * Math.sin(gamma)
    - 0.006758 * Math.cos(2 * gamma) + 0.000907 * Math.sin(2 * gamma)
    - 0.002697 * Math.cos(3 * gamma) + 0.00148 * Math.sin(3 * gamma)
  );
  const trueSolarTime = positiveModulo(
    localMinutes + equationOfTime + 4 * CHRISTCHURCH.longitude - 60 * timezoneOffsetHours,
    1440,
  );
  const hourAngle = (trueSolarTime / 4 < 0 ? trueSolarTime / 4 + 180 : trueSolarTime / 4 - 180) * rad;
  const latRad = CHRISTCHURCH.latitude * rad;
  const cosZenith = Math.sin(latRad) * Math.sin(declination)
    + Math.cos(latRad) * Math.cos(declination) * Math.cos(hourAngle);
  const zenith = Math.acos(Math.min(1, Math.max(-1, cosZenith)));
  const elevation = 90 - zenith / rad;
  const azimuth = positiveModulo(
    Math.atan2(
      Math.sin(hourAngle),
      Math.cos(hourAngle) * Math.sin(latRad) - Math.tan(declination) * Math.cos(latRad),
    ) / rad + 180,
    360,
  );
  return { azimuth, elevation };
}

function sunlightRays(lightVector: PlanVector, elevation: number): SunlightRay[] {
  const rays: SunlightRay[] = [];
  const litRooms = new Set<string>();

  for (const lightEntry of SUNLIGHT_LIGHT_ENTRIES.filter((entry) => entry.kind === "external")) {
    for (const line of lightEntry.centerlines) {
      if (!isOpeningSunlit(line, lightVector)) {
        continue;
      }
      const direction = blendedLightDirection(line, lightVector);
      const length = Math.max(70, Math.min(260, elevation * 3.6));
      rays.push(renderSunlightRay(lightEntry, line, direction, length, "sunlight-ray"));
      if (lightEntry.room) {
        litRooms.add(lightEntry.room);
      }
    }
  }

  for (const lightEntry of SUNLIGHT_LIGHT_ENTRIES.filter((entry) => entry.kind === "internal")) {
    for (const line of lightEntry.centerlines) {
      const borrowedLight = borrowedLightTarget(line, lightVector, litRooms);
      if (!borrowedLight) {
        continue;
      }
      const direction = normalize({
        x: lightVector.x * 0.55 + borrowedLight.x * 0.45,
        y: lightVector.y * 0.55 + borrowedLight.y * 0.45,
      });
      const length = Math.max(34, Math.min(82, elevation * 1.35));
      rays.push(renderSunlightRay(
        { ...lightEntry, room: borrowedLight.room },
        line,
        direction,
        length,
        "sunlight-ray borrowed",
      ));
    }
  }

  return rays;
}

function renderSunlightRay(
  lightEntry: SunlightEntry,
  line: SunlightLine,
  direction: PlanVector,
  length: number,
  className: SunlightRay["className"],
): SunlightRay {
  const tangent = normalize({ x: line.x2 - line.x1, y: line.y2 - line.y1 });
  const taper = Math.max(5, Math.min(16, length * 0.1));
  const startA = { x: line.x1, y: line.y1 };
  const startB = { x: line.x2, y: line.y2 };
  const endB = {
    x: line.x2 + direction.x * length + tangent.x * taper,
    y: line.y2 + direction.y * length + tangent.y * taper,
  };
  const endA = {
    x: line.x1 + direction.x * length - tangent.x * taper,
    y: line.y1 + direction.y * length - tangent.y * taper,
  };
  const controlB = {
    x: line.x2 + direction.x * length * 0.52 + tangent.x * taper * 0.7,
    y: line.y2 + direction.y * length * 0.52 + tangent.y * taper * 0.7,
  };
  const controlA = {
    x: line.x1 + direction.x * length * 0.52 - tangent.x * taper * 0.7,
    y: line.y1 + direction.y * length * 0.52 - tangent.y * taper * 0.7,
  };
  return {
    id: `${lightEntry.id}-${raysafeNumber(line.x1)}-${raysafeNumber(line.y1)}-${className.replace(/\s+/g, "-")}`,
    className,
    path: [
      `M ${startA.x} ${startA.y}`,
      `L ${startB.x} ${startB.y}`,
      `Q ${controlB.x} ${controlB.y} ${endB.x} ${endB.y}`,
      `L ${endA.x} ${endA.y}`,
      `Q ${controlA.x} ${controlA.y} ${startA.x} ${startA.y}`,
      "Z",
    ].join(" "),
    clipId: lightEntry.room ? roomClipId(lightEntry.room) : null,
  };
}

function sunMarker(sunVector: PlanVector, elevation: number): SunlightSunMarker {
  const bounds = sunlightPlanBounds();
  const pathCx = (bounds.minX + bounds.maxX) / 2;
  const pathCy = (bounds.minY + bounds.maxY) / 2;
  const pathRx = (bounds.maxX - bounds.minX) / 2 + 78;
  const pathRy = (bounds.maxY - bounds.minY) / 2 + 78;
  return {
    pathCx,
    pathCy,
    pathRx,
    pathRy,
    sunX: pathCx + sunVector.x * pathRx,
    sunY: pathCy + sunVector.y * pathRy,
    sunRadius: Math.max(10, Math.min(16, 8 + elevation / 5)),
  };
}

function isOpeningSunlit(line: SunlightLine, lightVector: PlanVector): boolean {
  if (!line.admit_direction) {
    return false;
  }
  return dot(lightVector, line.admit_direction) > 0.12;
}

function blendedLightDirection(line: SunlightLine, lightVector: PlanVector): PlanVector {
  const admit = line.admit_direction ?? lightVector;
  return normalize({
    x: lightVector.x * 0.72 + admit.x * 0.28,
    y: lightVector.y * 0.72 + admit.y * 0.28,
  });
}

function borrowedLightTarget(
  line: SunlightLine,
  lightVector: PlanVector,
  litRooms: Set<string>,
): ({ room: string } & PlanVector) | null {
  if (!line.room_directions) {
    return null;
  }
  const target = [...line.room_directions]
    .map((direction) => ({ ...direction, score: dot(lightVector, direction) }))
    .sort((a, b) => b.score - a.score)[0];
  const source = [...line.room_directions]
    .filter((direction) => direction.room !== target.room)
    .map((direction) => ({
      ...direction,
      score: dot({ x: -lightVector.x, y: -lightVector.y }, direction),
    }))
    .sort((a, b) => b.score - a.score)[0];
  if (!target || !source || target.score <= 0.18 || !litRooms.has(source.room)) {
    return null;
  }
  return target;
}

function azimuthToPlanVector(azimuthDegrees: number, planRightBearingDegrees: number): PlanVector {
  const planAngle = (azimuthDegrees - planRightBearingDegrees) * Math.PI / 180;
  return { x: Math.cos(planAngle), y: Math.sin(planAngle) };
}

function normalize(vector: PlanVector): PlanVector {
  const length = Math.hypot(vector.x, vector.y);
  if (!length) {
    return { x: 0, y: 0 };
  }
  return { x: vector.x / length, y: vector.y / length };
}

function dot(a: PlanVector, b: PlanVector): number {
  return a.x * b.x + a.y * b.y;
}

function geometryPath(geometry: RoomGeometry): string {
  if (geometry.type === "rect") {
    return [
      `M ${geometry.x} ${geometry.y}`,
      `H ${geometry.x + geometry.width}`,
      `V ${geometry.y + geometry.height}`,
      `H ${geometry.x}`,
      "Z",
    ].join(" ");
  }
  if (geometry.type === "polygon") {
    return polygonPath(geometry.points);
  }
  return geometry.polygons.map(polygonPath).join(" ");
}

function polygonPath(points: Array<[number, number]>): string {
  if (points.length === 0) {
    return "";
  }
  const [first, ...rest] = points;
  return [`M ${first[0]} ${first[1]}`, ...rest.map(([x, y]) => `L ${x} ${y}`), "Z"].join(" ");
}

function roomClipId(roomId: string): string {
  return `sunlight-room-clip-${roomId}`;
}

function sunlightPlanBounds(): { minX: number; minY: number; maxX: number; maxY: number } {
  const points = SUNLIGHT_ROOMS.flatMap((room) => geometryPoints(room.geometry));
  return {
    minX: Math.min(...points.map((point) => point.x)),
    minY: Math.min(...points.map((point) => point.y)),
    maxX: Math.max(...points.map((point) => point.x)),
    maxY: Math.max(...points.map((point) => point.y)),
  };
}

function geometryPoints(geometry: RoomGeometry): PlanVector[] {
  if (geometry.type === "rect") {
    return [
      { x: geometry.x, y: geometry.y },
      { x: geometry.x + geometry.width, y: geometry.y + geometry.height },
    ];
  }
  if (geometry.type === "polygon") {
    return geometry.points.map(([x, y]) => ({ x, y }));
  }
  return geometry.polygons.flatMap((polygon) => polygon.map(([x, y]) => ({ x, y })));
}

function dayOfYearForMonthDay(month: number, day: number): number {
  const daysBeforeMonth = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
  return daysBeforeMonth[Math.max(0, Math.min(11, month - 1))] + day;
}

function daylightSavingMonth(month: number): boolean {
  return month <= 4 || month >= 10;
}

function positiveModulo(value: number, divisor: number): number {
  return ((value % divisor) + divisor) % divisor;
}

function raysafeNumber(value: number): string {
  return value.toFixed(1).replace(/[^0-9]/g, "");
}
