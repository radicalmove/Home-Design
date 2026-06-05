import { describe, expect, it } from "vitest";
import type { ProjectManifest } from "../types";
import {
  activeScenario,
  activeView,
  firstAvailableViewId,
  firstScenarioId,
  selectAvailableScenario,
  selectAvailableScenarioView,
  selectAvailableView,
  viewsForScenario,
} from "./viewState";

const project: ProjectManifest = {
  id: "current-house",
  name: "Current House",
  model_version: "current-generated-views",
  model_source: "DATA/house_model.json",
  views: [
    {
      id: "base-view",
      label: "2D Plan",
      mode: "base_plan",
      asset_path: "/views/reference_plan.html",
      available: true,
    },
    {
      id: "three-d-navigation",
      label: "3D Navigation",
      mode: "three_d_navigation",
      asset_path: "/views/house_3d.html",
      available: true,
    },
    {
      id: "furniture-editor",
      label: "Furniture Editor",
      mode: "furniture_editor",
      asset_path: "/views/reference_plan.svg",
      available: true,
    },
    {
      id: "estimated-cost",
      label: "Estimated Cost",
      mode: "estimated_cost",
      asset_path: "",
      available: true,
    },
  ],
  scenarios: [
    {
      id: "current",
      label: "Design 1 - Current House",
      short_label: "Design 1",
      summary: "Current house",
      source_design: null,
      rank: 1,
      complete: true,
    },
    {
      id: "back-side-living-sunroom-bedroom",
      label: "Design 2 - Back-Side Living Rebuild + Sunroom Bedroom Replacement",
      short_label: "Design 2",
      summary: "Bedroom 2 becomes the living/dining/day room.",
      source_design: "current",
      rank: 2,
      complete: false,
    },
  ],
  layers: [],
  object_catalogs: [],
  analysis_outputs: [],
};

describe("view state helpers", () => {
  it("defaults to the first available view", () => {
    expect(firstAvailableViewId(project)).toBe("base-view");
  });

  it("selects an available requested view", () => {
    expect(selectAvailableView(project, "three-d-navigation")).toBe("three-d-navigation");
  });

  it("falls back to the base view when a requested view is unavailable", () => {
    const unavailableProject = {
      ...project,
      views: project.views.map((view) =>
        view.id === "three-d-navigation" ? { ...view, available: false } : view,
      ),
    };

    expect(selectAvailableView(unavailableProject, "three-d-navigation")).toBe("base-view");
  });

  it("returns the active descriptor for the selected view", () => {
    expect(activeView(project, "three-d-navigation")?.asset_path).toBe("/views/house_3d.html");
  });

  it("selects the furniture editor native view when available", () => {
    expect(selectAvailableView(project, "furniture-editor")).toBe("furniture-editor");
    expect(activeView(project, "furniture-editor")?.mode).toBe("furniture_editor");
  });

  it("defaults to the current scenario", () => {
    expect(firstScenarioId(project)).toBe("current");
    expect(selectAvailableScenario(project, null)).toBe("current");
  });

  it("falls back to the current scenario when a requested scenario is unknown", () => {
    expect(selectAvailableScenario(project, "missing-design")).toBe("current");
    expect(activeScenario(project, "missing-design")?.id).toBe("current");
  });

  it("selects a scenario and view together", () => {
    expect(
      selectAvailableScenarioView(project, "back-side-living-sunroom-bedroom", "three-d-navigation"),
    ).toEqual({
      scenarioId: "back-side-living-sunroom-bedroom",
      viewId: "three-d-navigation",
    });
  });

  it("falls back to an available view while preserving the selected scenario", () => {
    const unavailableProject = {
      ...project,
      views: project.views.map((view) =>
        view.id === "three-d-navigation" ? { ...view, available: false } : view,
      ),
    };

    expect(
      selectAvailableScenarioView(
        unavailableProject,
        "back-side-living-sunroom-bedroom",
        "three-d-navigation",
      ),
    ).toEqual({
      scenarioId: "back-side-living-sunroom-bedroom",
      viewId: "base-view",
    });
  });

  it("only exposes the estimated cost view for Design 2", () => {
    expect(viewsForScenario(project, "current").map((view) => view.id)).not.toContain("estimated-cost");
    expect(viewsForScenario(project, "back-side-living-sunroom-bedroom").map((view) => view.id)).toContain(
      "estimated-cost",
    );
    expect(selectAvailableScenarioView(project, "current", "estimated-cost")).toEqual({
      scenarioId: "current",
      viewId: "base-view",
    });
    expect(selectAvailableScenarioView(project, "back-side-living-sunroom-bedroom", "estimated-cost")).toEqual({
      scenarioId: "back-side-living-sunroom-bedroom",
      viewId: "estimated-cost",
    });
  });
});
