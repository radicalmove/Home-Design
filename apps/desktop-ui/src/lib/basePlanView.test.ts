import { describe, expect, it } from "vitest";
import { basePlanBackgroundAssetPath } from "./basePlanView";
import type { ProjectManifest } from "../types";

function projectWithViews(views: ProjectManifest["views"]): ProjectManifest {
  return {
    id: "current-house",
    name: "Current House",
    model_version: "1",
    model_source: "DATA/house_model.json",
    views,
    scenarios: [],
    layers: [],
    object_catalogs: [],
    analysis_outputs: [],
  };
}

describe("base plan view assets", () => {
  it("uses the SVG floor plan asset for the native 2D canvas", () => {
    const project = projectWithViews([
      {
        id: "base-view",
        label: "2D Plan",
        mode: "base_plan",
        asset_path: "/views/reference_plan.html",
        available: true,
      },
      {
        id: "furniture-editor",
        label: "Furniture Editor",
        mode: "furniture_editor",
        asset_path: "/views/reference_plan.svg",
        available: true,
      },
    ]);

    expect(basePlanBackgroundAssetPath(project)).toBe("/views/reference_plan.svg");
  });
});
