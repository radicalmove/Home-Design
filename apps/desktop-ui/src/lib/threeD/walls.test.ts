import { describe, expect, it } from "vitest";
import { buildMeasuredWallsFromRooms } from "./walls";
import type { SceneGeometry } from "./geometry";

describe("measured 3D wall generation", () => {
  it("builds walls from room footprint edges instead of curated SVG paths", () => {
    const rooms = [
      {
        id: "lounge",
        geometry: { type: "rect", x: 0, z: 0, width: 3, depth: 4 } satisfies SceneGeometry,
      },
      {
        id: "hallway",
        geometry: { type: "rect", x: 0, z: 4, width: 3, depth: 1 } satisfies SceneGeometry,
      },
    ];

    const walls = buildMeasuredWallsFromRooms(rooms);

    expect(walls.every((wall) => wall.id.startsWith("measured-wall:"))).toBe(true);
    expect(walls.some((wall) => wall.class === "interior")).toBe(true);
    expect(walls.some((wall) => wall.class === "exterior")).toBe(true);
  });

  it("follows polygon room outlines so sunroom-style angled walls are represented", () => {
    const walls = buildMeasuredWallsFromRooms([
      {
        id: "sunroom",
        geometry: {
          type: "polygon",
          points: [
            { x: 0, z: 0 },
            { x: 2, z: 0 },
            { x: 2, z: 1 },
            { x: 1, z: 2 },
            { x: 0, z: 1 },
          ],
        },
      },
    ]);

    expect(walls).toHaveLength(5);
    expect(walls.some((wall) => {
      const segment = wall.segments[0];
      return segment && Math.abs(segment.x1 - segment.x2) > 0.1 && Math.abs(segment.z1 - segment.z2) > 0.1;
    })).toBe(true);
  });

  it("merges close parallel room faces so shared thick walls do not render as double walls", () => {
    const walls = buildMeasuredWallsFromRooms([
      {
        id: "sunroom",
        geometry: { type: "rect", x: 0, z: 0, width: 3, depth: 4 } satisfies SceneGeometry,
      },
      {
        id: "lounge",
        geometry: { type: "rect", x: 3.16, z: 0, width: 3, depth: 4 } satisfies SceneGeometry,
      },
    ]);

    const sharedWallSegments = walls
      .filter((wall) => wall.class === "interior")
      .flatMap((wall) => wall.segments)
      .filter((segment) => Math.abs(segment.x1 - segment.x2) < 0.001 && segment.z1 === 0 && segment.z2 === 4);

    expect(sharedWallSegments).toHaveLength(1);
    expect(sharedWallSegments[0]?.x1).toBeCloseTo(3.08, 2);
  });
});
