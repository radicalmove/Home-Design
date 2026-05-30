import { invoke } from "@tauri-apps/api/core";
import type { AppStatus, ProjectManifest } from "../types";

export function getAppStatus(): Promise<AppStatus> {
  return invoke<AppStatus>("get_app_status");
}

export function loadBuiltinProject(): Promise<ProjectManifest> {
  return invoke<ProjectManifest>("load_builtin_project");
}
