import { describe, expect, it } from "vitest";
import type { ProjectManifest } from "../types";
import { activeView, firstAvailableViewId, selectAvailableView } from "./viewState";

const project: ProjectManifest = {
  id: "current-house",
  name: "Current House",
  model_version: "current-generated-views",
  model_source: "DATA/house_model.json",
  views: [
    {
      id: "base-view",
      label: "Base View",
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
      id: "design-report",
      label: "Design Report",
      mode: "design_report",
      asset_path: "/views/calibration_report.html",
      available: true,
    },
  ],
  scenarios: [],
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
    expect(activeView(project, "design-report")?.asset_path).toBe("/views/calibration_report.html");
  });
});
