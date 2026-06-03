import { describe, expect, it, vi } from "vitest";
import type { ProjectManifest } from "../types";
import { withCheckedViewAvailability } from "./assetAvailability";

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

describe("asset availability", () => {
  it("checks packaged view URLs through the browser runtime", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce({ ok: true })
      .mockResolvedValueOnce({ ok: false })
      .mockResolvedValueOnce({ ok: true });

    const checked = await withCheckedViewAvailability(project, fetcher);

    expect(fetcher).toHaveBeenCalledWith("/views/reference_plan.html", {
      cache: "no-store",
      method: "GET",
    });
    expect(fetcher).toHaveBeenCalledWith("/views/calibration_report.html", {
      cache: "no-store",
      method: "GET",
    });
    expect(checked.views[0].available).toBe(true);
    expect(checked.views[1].available).toBe(false);
    expect(checked.views[2].available).toBe(true);
  });

  it("marks a view unavailable when fetch fails", async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error("missing"));

    const checked = await withCheckedViewAvailability(project, fetcher);

    expect(checked.views.every((view) => !view.available)).toBe(true);
  });
});
