import { invoke } from "@tauri-apps/api/core";
import type {
  AppStatus,
  BuiltInModelStatus,
  DesignReviewData,
  FurnitureCatalog,
  FurnitureLayout,
  FurnitureLayoutLoadResult,
  ProjectManifest,
} from "../types";

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
      id: "design-review",
      label: "Design Review",
      mode: "design_review",
      asset_path: "",
      available: true,
    },
  ],
  scenarios: [
    {
      id: "current",
      label: "Design 1 - Current House",
      short_label: "Design 1",
      summary: "The current measured house, furniture layout, daylight review, and 3D navigation model.",
      source_design: null,
      rank: 1,
      complete: true,
    },
    {
      id: "back-side-living-sunroom-bedroom",
      label: "Design 2 - Back-Side Living Rebuild + Sunroom Bedroom Replacement",
      short_label: "Design 2",
      summary:
        "Bedroom 2 and the service end become the stronger living/dining/day room, while the current lounge and sunroom footprints become bedrooms.",
      source_design: "current",
      rank: 2,
      complete: false,
    },
  ],
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

export function loadBuiltinModelStatus(): Promise<BuiltInModelStatus> {
  return invoke<BuiltInModelStatus>("load_builtin_model_status");
}

export function loadFurnitureCatalog(): Promise<FurnitureCatalog> {
  return invoke<FurnitureCatalog>("load_furniture_catalog");
}

export function loadFurnitureLayout(
  projectId: string,
  scenarioId: string,
): Promise<FurnitureLayoutLoadResult> {
  return invoke<FurnitureLayoutLoadResult>("load_furniture_layout", { projectId, scenarioId });
}

export function saveFurnitureLayout(layout: FurnitureLayout): Promise<void> {
  return invoke<void>("save_furniture_layout", { layout });
}

export function loadDesignReviewData(
  projectId: string,
  scenarioId = "current",
): Promise<DesignReviewData> {
  return invoke<DesignReviewData>("load_design_review_data", { projectId, scenarioId });
}
