import { invoke } from "@tauri-apps/api/core";
import type { AppStatus, ProjectManifest } from "../types";

const fallbackStatus: AppStatus = {
  app_name: "Home Design",
  runtime: "browser-preview",
  built_in_project_count: 1,
};

const fallbackProject: ProjectManifest = {
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

export function getAppStatus(): Promise<AppStatus> {
  return invokeWithBrowserFallback("get_app_status", fallbackStatus);
}

export function loadBuiltinProject(): Promise<ProjectManifest> {
  return invokeWithBrowserFallback("load_builtin_project", fallbackProject);
}

async function invokeWithBrowserFallback<T>(command: string, fallback: T): Promise<T> {
  try {
    return await invoke<T>(command);
  } catch (reason: unknown) {
    if (isMissingTauriRuntime(reason)) {
      return fallback;
    }
    throw reason;
  }
}

function isMissingTauriRuntime(reason: unknown): boolean {
  if (!(reason instanceof Error)) {
    return false;
  }
  const message = reason.message.toLowerCase();
  return message.includes("invoke") && message.includes("undefined");
}
