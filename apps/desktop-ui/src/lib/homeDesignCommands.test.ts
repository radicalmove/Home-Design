import { beforeEach, describe, expect, it, vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import {
  getAppStatus,
  loadBuiltinModelStatus,
  loadBuiltinProject,
} from "./homeDesignCommands";

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
      views: [],
      scenarios: [],
      layers: [],
      object_catalogs: [],
      analysis_outputs: [],
    });

    const project = await loadBuiltinProject();

    expect(invokeMock).toHaveBeenCalledWith("load_builtin_project");
    expect(project.id).toBe("current-house");
  });

  it("loads the built-in model status from the Rust command", async () => {
    invokeMock.mockResolvedValueOnce({
      source_path: "DATA/house_model.json",
      summary: {
        units: "metres",
        room_count: 11,
        current_space_count: 11,
        current_built_in_count: 1,
        current_feature_count: 30,
        site_element_count: 11,
        shadow_source_count: 3,
      },
      valid: true,
      validation_error_count: 0,
      validation_warning_count: 0,
    });

    const status = await loadBuiltinModelStatus();

    expect(invokeMock).toHaveBeenCalledWith("load_builtin_model_status");
    expect(status.summary.room_count).toBe(11);
    expect(status.validation_error_count).toBe(0);
  });
});
