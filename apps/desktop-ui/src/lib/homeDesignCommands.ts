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

export function getAppStatus(): Promise<AppStatus> {
  return invoke<AppStatus>("get_app_status");
}

export function loadBuiltinProject(): Promise<ProjectManifest> {
  return invoke<ProjectManifest>("load_builtin_project");
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
