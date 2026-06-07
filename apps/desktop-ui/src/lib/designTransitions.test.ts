import { describe, expect, it } from "vitest";
import {
  DESIGN_TRANSITION_DURATION_MS,
  interpolateFurnitureLayouts,
  stagedFurnitureProgress,
  stagedStructuralTransitionProgress,
  transitionPercentLabel,
  transitionProgressAt,
} from "./designTransitions";
import type { FurnitureLayout } from "../types";

function layoutWithObjects(objects: FurnitureLayout["objects"]): FurnitureLayout {
  return {
    project_id: "current-house",
    scenario_id: "current",
    plan_transform: {
      units: "metres",
      svg_width_px: 1600,
      svg_height_px: 900,
      origin_svg_px: { x: 518, y: 314 },
      px_per_m: 27.16,
    },
    objects,
  };
}

function object(overrides: Partial<FurnitureLayout["objects"][number]>): FurnitureLayout["objects"][number] {
  return {
    id: "sofa",
    catalog_id: "sofa",
    layer: "moveable",
    type: "sofa",
    label: "Sofa",
    abbreviation: null,
    x_m: 1,
    y_m: 2,
    width_m: 2,
    depth_m: 1,
    z_index: 0,
    rotation_deg: 0,
    colour: "#333333",
    locked: false,
    notes: null,
    evidence: null,
    ...overrides,
  };
}

describe("design transition timing", () => {
  it("maps elapsed milliseconds onto a clamped 10 second progress value", () => {
    expect(transitionProgressAt(0, DESIGN_TRANSITION_DURATION_MS)).toBe(0);
    expect(transitionProgressAt(5_000, DESIGN_TRANSITION_DURATION_MS)).toBe(0.5);
    expect(transitionProgressAt(10_000, DESIGN_TRANSITION_DURATION_MS)).toBe(1);
    expect(transitionProgressAt(12_500, DESIGN_TRANSITION_DURATION_MS)).toBe(1);
    expect(transitionProgressAt(-250, DESIGN_TRANSITION_DURATION_MS)).toBe(0);
  });

  it("formats transition progress for status readouts", () => {
    expect(transitionPercentLabel(0)).toBe("0%");
    expect(transitionPercentLabel(0.456)).toBe("46%");
    expect(transitionPercentLabel(1)).toBe("100%");
  });

  it("stages structural changes before furniture movement", () => {
    expect(stagedStructuralTransitionProgress(0.1)).toBeGreaterThan(stagedFurnitureProgress(0.1));
    expect(stagedStructuralTransitionProgress(0.35)).toBe(1);
    expect(stagedFurnitureProgress(0.35)).toBe(0);
    expect(stagedFurnitureProgress(1)).toBe(1);
  });

  it("interpolates matching furniture objects from Design 1 to the target design", () => {
    const from = layoutWithObjects([
      object({
        id: "sofa",
        x_m: 1,
        y_m: 2,
        width_m: 2,
        depth_m: 1,
        rotation_deg: 0,
        l_shape: { main_depth_m: 0.8, return_width_m: 1 },
      }),
    ]);
    const to = {
      ...layoutWithObjects([
        object({
          id: "sofa",
          x_m: 5,
          y_m: 8,
          width_m: 3,
          depth_m: 2,
          rotation_deg: 90,
          l_shape: { main_depth_m: 1.2, return_width_m: 1.4 },
        }),
      ]),
      scenario_id: "back-side-living-sunroom-bedroom",
    };

    const interpolated = interpolateFurnitureLayouts(from, to, 0.5);

    expect(interpolated.scenario_id).toBe("back-side-living-sunroom-bedroom");
    expect(interpolated.objects[0]).toEqual(expect.objectContaining({
      id: "sofa",
      x_m: 3,
      y_m: 5,
      width_m: 2.5,
      depth_m: 1.5,
      rotation_deg: 45,
      l_shape: { main_depth_m: 1, return_width_m: 1.2 },
    }));
  });

  it("can stagger matching furniture object movement after the structural phase", () => {
    const from = layoutWithObjects([
      object({ id: "sofa", x_m: 1 }),
      object({ id: "chair", catalog_id: "chair", type: "chair", x_m: 2 }),
    ]);
    const to = {
      ...layoutWithObjects([
        object({ id: "sofa", x_m: 5 }),
        object({ id: "chair", catalog_id: "chair", type: "chair", x_m: 8 }),
      ]),
      scenario_id: "back-side-living-sunroom-bedroom",
    };

    const early = interpolateFurnitureLayouts(from, to, 0.35, { stagger: true });
    const mid = interpolateFurnitureLayouts(from, to, 0.65, { stagger: true });

    expect(early.objects[0].x_m).toBe(1);
    expect(early.objects[1].x_m).toBe(2);
    expect(mid.objects[0].x_m).toBeGreaterThan(1);
    expect(mid.objects[1].x_m).toBeGreaterThanOrEqual(2);
    expect(interpolateFurnitureLayouts(from, to, 1, { stagger: true }).objects[1].x_m).toBe(8);
  });

  it("clamps interpolation progress and leaves target-only objects in the target position", () => {
    const from = layoutWithObjects([object({ id: "sofa", x_m: 1 })]);
    const to = {
      ...layoutWithObjects([
        object({ id: "sofa", x_m: 5 }),
        object({ id: "new-chair", catalog_id: "chair", type: "chair", x_m: 9 }),
      ]),
      scenario_id: "back-side-living-sunroom-bedroom",
    };

    expect(interpolateFurnitureLayouts(from, to, -1).objects[0].x_m).toBe(1);
    expect(interpolateFurnitureLayouts(from, to, 2).objects[0].x_m).toBe(5);
    expect(interpolateFurnitureLayouts(from, to, 0.25).objects[1].x_m).toBe(9);
  });
});
