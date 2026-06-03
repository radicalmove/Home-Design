import { beforeEach, describe, expect, it, vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { getAppStatus, loadBuiltinProject } from "./homeDesignCommands";

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

const invokeMock = vi.mocked(invoke);

describe("home design Tauri commands", () => {
  beforeEach(() => {
    invokeMock.mockReset();
  });

  it("loads app status from the Rust command", async () => {
    invokeMock.mockResolvedValueOnce({
      app_name: "Home Design",
      runtime: "tauri-desktop",
      built_in_project_count: 1,
    });

    const status = await getAppStatus();

    expect(invokeMock).toHaveBeenCalledWith("get_app_status");
    expect(status.app_name).toBe("Home Design");
  });

  it("loads the built-in project manifest from the Rust command", async () => {
    invokeMock.mockResolvedValueOnce({
      id: "current-house",
      name: "Current House",
      model_version: "current-generated-views",
      model_source: "DATA/house_model.json",
      views: [
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
    });

    const project = await loadBuiltinProject();

    expect(invokeMock).toHaveBeenCalledWith("load_builtin_project");
    expect(project.id).toBe("current-house");
    expect(project.views[0].asset_path).toBe("/views/calibration_report.html");
  });

  it("falls back to the packaged manifest when Tauri invoke is unavailable", async () => {
    invokeMock.mockRejectedValueOnce(new TypeError("Cannot read properties of undefined (reading 'invoke')"));

    const project = await loadBuiltinProject();

    expect(project.id).toBe("current-house");
    expect(project.views.map((view) => view.id)).toContain("design-report");
    expect(project.views.find((view) => view.id === "design-report")?.asset_path).toBe(
      "/views/calibration_report.html",
    );
  });

  it("falls back to packaged status when Tauri invoke is unavailable", async () => {
    invokeMock.mockRejectedValueOnce(new TypeError("Cannot read properties of undefined (reading 'invoke')"));

    const status = await getAppStatus();

    expect(status.app_name).toBe("Home Design");
    expect(status.built_in_project_count).toBe(1);
  });
});
