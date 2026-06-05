import type { PlanTransform } from "../../types";
import {
  displayPointToScene,
  sceneGeometryBoundsList,
  type SceneBounds,
  type SceneGeometry,
  type ScenePoint,
} from "./geometry";

export type ThreeDWallClass = "exterior" | "interior" | "thin-exterior" | "thin-interior";

export type ThreeDWallSegment = {
  x1: number;
  z1: number;
  x2: number;
  z2: number;
};

export type ThreeDWall = {
  id: string;
  class: ThreeDWallClass;
  pixelPath: string;
  segments: ThreeDWallSegment[];
  sourceRoomIds: string[];
  heightM: number;
  thicknessM: number;
  material: "paintedWall";
};

export type ThreeDWallOpening = {
  type: string;
  geometry: SceneGeometry;
};

export type ThreeDWallRoomInput = {
  id: string;
  geometry: SceneGeometry;
};

type CuratedWallPath = [id: string, wallClass: ThreeDWallClass, path: string];

const CURATED_WALL_PATHS: CuratedWallPath[] = [
  ["sunroom_glazing_frame", "interior", "M536 486 V452 H552 L597 408 V360 H667.1 V380.4 M667.1 462.6 V486"],
  ["lounge_exterior", "exterior", "M657.2 358 H762.8"],
  ["lounge_sunroom_wall", "exterior", "M659.1 358 V380.4 M659.1 462.6 V485"],
  ["master_sunroom_old_external_wall", "exterior", "M518 485 H608"],
  ["hallway_north_wall", "exterior", "M608 485 H634 M654.4 485 H667.1"],
  ["lounge_hallway_wall", "interior", "M659.1 488.5 H701.5 M723.5 488.5 H760.9"],
  ["kitchen_east_wall", "exterior", "M758.8 358 V302.3 H833 V498.5"],
  ["entrance_deck_wall", "thin-exterior", "M834.3 496 H841.9 M881.8 496 H940"],
  ["kitchen_entrance_return_wall", "thin-interior", "M834.3 496 V502.8 H803.7"],
  ["private_rooms_south_wall", "exterior", "M518 610 H940"],
  ["bedroom2_east_wall", "interior", "M890 518.5 V610"],
  ["master_west_wall", "exterior", "M518 485 V610"],
  ["dining_west_external_wall", "exterior", "M758.8 302.3 V358"],
  ["kitchen_lounge_nub", "interior", "M760.9 358 V370.8"],
  ["lounge_kitchen_divider", "interior", "M760.9 395 V493"],
  ["hallway_south_wall", "interior", "M608 523 H657 M679 523 H688 M722 523 H758"],
  ["hallway_kitchen_door_wall", "interior", "M760.9 515 V523"],
  ["bedroom2_north_wall", "interior", "M758 523 H762 M784 523 H890"],
  ["master_office_wall", "interior", "M608 485 V494 M608 516 V610"],
  ["office_bathroom_wall", "interior", "M688 520.5 V610"],
  ["bathroom_bedroom2_wall", "interior", "M758 523 V610"],
  ["entrance_laundry_wall", "interior", "M890 496 V504"],
  ["laundry_toilet_wall", "thin-interior", "M890 580 H896 M912 580 H940"],
  ["kitchen_entrance_door_wall", "interior", "M803.7 496 V499.6 M803.7 519.4 V523"],
  ["laundry_toilet_exterior", "exterior", "M940 496 V610"],
];

const WALL_CLASS_SPECS: Record<ThreeDWallClass, { heightM: number; thicknessM: number }> = {
  exterior: { heightM: 2.35, thicknessM: 0.16 },
  interior: { heightM: 2.35, thicknessM: 0.1 },
  "thin-exterior": { heightM: 2.35, thicknessM: 0.08 },
  "thin-interior": { heightM: 2.35, thicknessM: 0.07 },
};

const OPENING_WALL_PROXIMITY_M = 0.14;
const OPENING_GAP_MARGIN_M = 0.015;
const MIN_OPENING_OVERLAP_M = 0.08;
const MIN_WALL_PIECE_LENGTH_M = 0.08;
const WALL_PATH_TOKEN_RE = /[MLHVZ]|-?\d+(?:\.\d+)?/g;
const WALL_POINT_PRECISION = 1000;

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

function pointKey(point: ScenePoint): string {
  return `${Math.round(point.x * WALL_POINT_PRECISION)},${Math.round(point.z * WALL_POINT_PRECISION)}`;
}

function canonicalSegmentKey(start: ScenePoint, end: ScenePoint): string {
  const startKey = pointKey(start);
  const endKey = pointKey(end);
  return startKey < endKey ? `${startKey}|${endKey}` : `${endKey}|${startKey}`;
}

function axisAlignedOrientation(segment: ThreeDWallSegment): "horizontal" | "vertical" | null {
  if (Math.abs(segment.z1 - segment.z2) < 0.001) {
    return "horizontal";
  }
  if (Math.abs(segment.x1 - segment.x2) < 0.001) {
    return "vertical";
  }
  return null;
}

function segmentRangeOverlap(
  first: [number, number],
  second: [number, number],
): number {
  const firstLow = Math.min(...first);
  const firstHigh = Math.max(...first);
  const secondLow = Math.min(...second);
  const secondHigh = Math.max(...second);
  return Math.min(firstHigh, secondHigh) - Math.max(firstLow, secondLow);
}

function nearParallelRoomEdge(
  first: ThreeDWallSegment,
  second: ThreeDWallSegment,
): boolean {
  const orientation = axisAlignedOrientation(first);
  if (!orientation || orientation !== axisAlignedOrientation(second)) {
    return false;
  }
  if (orientation === "horizontal") {
    return Math.abs(first.z1 - second.z1) <= 0.32
      && segmentRangeOverlap([first.x1, first.x2], [second.x1, second.x2]) > 0.18;
  }
  return Math.abs(first.x1 - second.x1) <= 0.32
    && segmentRangeOverlap([first.z1, first.z2], [second.z1, second.z2]) > 0.18;
}

function nearParallelOverlapRatio(first: ThreeDWallSegment, second: ThreeDWallSegment): number {
  const orientation = axisAlignedOrientation(first);
  if (!orientation || orientation !== axisAlignedOrientation(second)) {
    return 0;
  }
  const firstLength = Math.hypot(first.x2 - first.x1, first.z2 - first.z1);
  const secondLength = Math.hypot(second.x2 - second.x1, second.z2 - second.z1);
  if (firstLength <= 0.001 || secondLength <= 0.001) {
    return 0;
  }
  const overlap = orientation === "horizontal"
    ? segmentRangeOverlap([first.x1, first.x2], [second.x1, second.x2])
    : segmentRangeOverlap([first.z1, first.z2], [second.z1, second.z2]);
  return overlap / Math.min(firstLength, secondLength);
}

function mergedNearParallelSegment(first: ThreeDWallSegment, second: ThreeDWallSegment): ThreeDWallSegment {
  const orientation = axisAlignedOrientation(first);
  if (orientation === "horizontal") {
    const xLow = Math.max(Math.min(first.x1, first.x2), Math.min(second.x1, second.x2));
    const xHigh = Math.min(Math.max(first.x1, first.x2), Math.max(second.x1, second.x2));
    const z = (first.z1 + second.z1) / 2;
    return { x1: xLow, z1: z, x2: xHigh, z2: z };
  }
  const zLow = Math.max(Math.min(first.z1, first.z2), Math.min(second.z1, second.z2));
  const zHigh = Math.min(Math.max(first.z1, first.z2), Math.max(second.z1, second.z2));
  const x = (first.x1 + second.x1) / 2;
  return { x1: x, z1: zLow, x2: x, z2: zHigh };
}

export function buildMeasuredWallsFromRooms(rooms: ThreeDWallRoomInput[]): ThreeDWall[] {
  const measuredSegments = new Map<string, {
    segment: ThreeDWallSegment;
    sourceRoomIds: Set<string>;
  }>();

  for (const room of rooms) {
    for (const polygon of geometryPolygons(room.geometry)) {
      polygon.forEach((point, index) => {
        const next = polygon[(index + 1) % polygon.length];
        if (!next || (Math.abs(point.x - next.x) < 0.001 && Math.abs(point.z - next.z) < 0.001)) {
          return;
        }
        const key = canonicalSegmentKey(point, next);
        const existing = measuredSegments.get(key);
        if (existing) {
          existing.sourceRoomIds.add(room.id);
          return;
        }
        measuredSegments.set(key, {
          segment: { x1: point.x, z1: point.z, x2: next.x, z2: next.z },
          sourceRoomIds: new Set([room.id]),
        });
      });
    }
  }

  const entries = Array.from(measuredSegments.entries());
  const consumed = new Set<number>();
  const walls: ThreeDWall[] = [];

  entries.forEach(([key, entry], index) => {
    if (consumed.has(index)) {
      return;
    }
    const mergeIndex = entries.findIndex(([, other], otherIndex) => {
      if (otherIndex <= index || consumed.has(otherIndex) || other === entry) {
        return false;
      }
      const otherRoomIds = Array.from(other.sourceRoomIds);
      return Array.from(entry.sourceRoomIds).every((roomId) => !other.sourceRoomIds.has(roomId))
        && otherRoomIds.every((roomId) => !entry.sourceRoomIds.has(roomId))
        && nearParallelRoomEdge(entry.segment, other.segment)
        && nearParallelOverlapRatio(entry.segment, other.segment) >= 0.85;
    });
    const mergeEntry = mergeIndex >= 0 ? entries[mergeIndex]?.[1] : null;
    if (mergeEntry) {
      consumed.add(mergeIndex);
    }
    const sourceRoomIds = Array.from(entry.sourceRoomIds).sort();
    const mergedSourceRoomIds = mergeEntry
      ? Array.from(new Set([...sourceRoomIds, ...Array.from(mergeEntry.sourceRoomIds)])).sort()
      : sourceRoomIds;
    const segment = mergeEntry ? mergedNearParallelSegment(entry.segment, mergeEntry.segment) : entry.segment;
    const hasNearbyRoomFace = !mergeEntry && sourceRoomIds.length === 1 && entries.some(([, other]) => {
      const otherRoomIds = Array.from(other.sourceRoomIds);
      return other !== entry
        && otherRoomIds.every((roomId) => !entry.sourceRoomIds.has(roomId))
        && nearParallelRoomEdge(entry.segment, other.segment);
    });
    const wallClass: ThreeDWallClass = mergedSourceRoomIds.length > 1 || hasNearbyRoomFace ? "interior" : "exterior";
    const spec = WALL_CLASS_SPECS[wallClass];
    walls.push({
      id: `measured-wall:${index}:${key}`,
      class: wallClass,
      pixelPath: "",
      sourceRoomIds: mergedSourceRoomIds,
      segments: [segment],
      heightM: spec.heightM,
      thicknessM: spec.thicknessM,
      material: "paintedWall",
    });
  });

  return walls;
}

function parseWallPathSegments(pathData: string): Array<[ScenePoint, ScenePoint]> {
  const tokens = pathData.match(WALL_PATH_TOKEN_RE) ?? [];
  const segments: Array<[ScenePoint, ScenePoint]> = [];
  const commands = new Set(["M", "L", "H", "V", "Z"]);
  let command = "";
  let current: ScenePoint | null = null;
  let subpathStart: ScenePoint | null = null;
  let index = 0;

  while (index < tokens.length) {
    const token = tokens[index];
    if (commands.has(token)) {
      command = token;
      index += 1;
    }

    if (command === "M") {
      current = { x: Number(tokens[index]), z: Number(tokens[index + 1]) };
      subpathStart = current;
      index += 2;
      command = "L";
      continue;
    }

    if (command === "L" && current) {
      const next: ScenePoint = { x: Number(tokens[index]), z: Number(tokens[index + 1]) };
      if (next.x !== current.x || next.z !== current.z) {
        segments.push([current, next]);
      }
      current = next;
      index += 2;
      continue;
    }

    if (command === "H" && current) {
      const next: ScenePoint = { x: Number(tokens[index]), z: current.z };
      if (next.x !== current.x) {
        segments.push([current, next]);
      }
      current = next;
      index += 1;
      continue;
    }

    if (command === "V" && current) {
      const next: ScenePoint = { x: current.x, z: Number(tokens[index]) };
      if (next.z !== current.z) {
        segments.push([current, next]);
      }
      current = next;
      index += 1;
      continue;
    }

    if (command === "Z" && current && subpathStart) {
      if (current.x !== subpathStart.x || current.z !== subpathStart.z) {
        segments.push([current, subpathStart]);
      }
      current = subpathStart;
      command = "";
      continue;
    }

    throw new Error(`Unsupported wall path near token ${token}: ${pathData}`);
  }

  return segments;
}

function subtractIntervals(source: [number, number], cuts: Array<[number, number]>): Array<[number, number]> {
  const [sourceLow, sourceHigh] = [...source].sort((left, right) => left - right);
  let pieces: Array<[number, number]> = [[sourceLow, sourceHigh]];

  for (const [cutLow, cutHigh] of cuts.sort((left, right) => left[0] - right[0])) {
    if (cutHigh <= sourceLow || cutLow >= sourceHigh) {
      continue;
    }
    const overlap = Math.min(sourceHigh, cutHigh) - Math.max(sourceLow, cutLow);
    if (overlap < MIN_OPENING_OVERLAP_M) {
      continue;
    }

    const nextPieces: Array<[number, number]> = [];
    for (const [pieceLow, pieceHigh] of pieces) {
      if (cutHigh <= pieceLow || cutLow >= pieceHigh) {
        nextPieces.push([pieceLow, pieceHigh]);
        continue;
      }
      const left: [number, number] = [pieceLow, Math.min(cutLow, pieceHigh)];
      const right: [number, number] = [Math.max(cutHigh, pieceLow), pieceHigh];
      if (left[1] - left[0] >= MIN_WALL_PIECE_LENGTH_M) {
        nextPieces.push(left);
      }
      if (right[1] - right[0] >= MIN_WALL_PIECE_LENGTH_M) {
        nextPieces.push(right);
      }
    }
    pieces = nextPieces;
  }

  return pieces;
}

function splitWallSegmentForOpenings(
  startPoint: ScenePoint,
  endPoint: ScenePoint,
  openingGaps: SceneBounds[],
): ThreeDWallSegment[] {
  const x1 = startPoint.x;
  const z1 = startPoint.z;
  const x2 = endPoint.x;
  const z2 = endPoint.z;
  const vertical = Math.abs(x1 - x2) < 1e-6;
  const horizontal = Math.abs(z1 - z2) < 1e-6;

  if (!vertical && !horizontal) {
    return [{ x1, z1, x2, z2 }];
  }

  if (vertical) {
    const cutIntervals = openingGaps
      .filter((gap) => gap.minX - OPENING_WALL_PROXIMITY_M <= x1 && x1 <= gap.maxX + OPENING_WALL_PROXIMITY_M)
      .map((gap): [number, number] => [
        gap.minZ - OPENING_GAP_MARGIN_M,
        gap.maxZ + OPENING_GAP_MARGIN_M,
      ]);
    let pieces = subtractIntervals([z1, z2], cutIntervals);
    if (z1 > z2) {
      pieces = pieces.map(([low, high]) => [high, low]);
    }
    return pieces.map(([low, high]) => ({ x1, z1: low, x2, z2: high }));
  }

  const cutIntervals = openingGaps
    .filter((gap) => gap.minZ - OPENING_WALL_PROXIMITY_M <= z1 && z1 <= gap.maxZ + OPENING_WALL_PROXIMITY_M)
    .map((gap): [number, number] => [
      gap.minX - OPENING_GAP_MARGIN_M,
      gap.maxX + OPENING_GAP_MARGIN_M,
    ]);
  let pieces = subtractIntervals([x1, x2], cutIntervals);
  if (x1 > x2) {
    pieces = pieces.map(([low, high]) => [high, low]);
  }
  return pieces.map(([low, high]) => ({ x1: low, z1, x2: high, z2 }));
}

function shouldCutWallForOpening(openingType: string): boolean {
  return openingType.includes("door")
    || openingType.includes("slider")
    || openingType === "opening"
    || openingType === "large_opening";
}

export function buildCuratedWalls(transform: PlanTransform, openings: ThreeDWallOpening[]): ThreeDWall[] {
  const openingGaps = openings
    .filter((opening) => shouldCutWallForOpening(opening.type))
    .flatMap((opening) => sceneGeometryBoundsList(opening.geometry));
  return CURATED_WALL_PATHS.map(([id, wallClass, pathData]) => {
    const spec = WALL_CLASS_SPECS[wallClass];
    const segments = parseWallPathSegments(pathData).flatMap(([start, end]) => {
      const startPoint = displayPointToScene({ x: start.x, y: start.z }, transform);
      const endPoint = displayPointToScene({ x: end.x, y: end.z }, transform);
      return splitWallSegmentForOpenings(startPoint, endPoint, openingGaps);
    });

    return {
      id,
      class: wallClass,
      pixelPath: pathData,
      sourceRoomIds: [],
      segments,
      heightM: spec.heightM,
      thicknessM: spec.thicknessM,
      material: "paintedWall",
    };
  });
}
