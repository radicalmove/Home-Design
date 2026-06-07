import { describe, expect, it } from "vitest";
import {
  HORIZONTAL_PLANE_ROTATION_X,
  openingPanelSpecsForGeometry,
} from "./renderGeometry";
import type { SceneGeometry } from "./geometry";

describe("3D render geometry helpers", () => {
  it("maps 2D floor polygons to positive Three.js Z instead of mirroring them", () => {
    expect(HORIZONTAL_PLANE_ROTATION_X).toBe(Math.PI / 2);
  });

  it("converts narrow opening geometry into vertical wall-height panels", () => {
    const geometry: SceneGeometry = {
      type: "rect",
      x: 10,
      z: 3,
      width: 0.18,
      depth: 2.4,
    };

    const panels = openingPanelSpecsForGeometry(geometry, 0.3);

    expect(panels).toHaveLength(1);
    expect(panels[0]).toMatchObject({
      depthM: 0.035,
      heightM: 1.95,
      rotationY: Math.PI / 2,
    });
    expect(panels[0].widthM).toBeCloseTo(2.4);
    expect(panels[0].position.y).toBeGreaterThan(1);
    expect(panels[0].position.z).toBeCloseTo(4.2);
  });

  it("can lift window panels above a sill instead of starting every opening at floor level", () => {
    const geometry: SceneGeometry = {
      type: "rect",
      x: 12,
      z: 6,
      width: 1.6,
      depth: 0.14,
    };

    const panels = openingPanelSpecsForGeometry(geometry, 0.3, 1.1, 0.035, 0.85);

    expect(panels).toHaveLength(1);
    expect(panels[0]).toMatchObject({
      heightM: 1.1,
      sillHeightM: 0.85,
      rotationY: 0,
    });
    expect(panels[0].position.y).toBeCloseTo(1.7);
  });
});
