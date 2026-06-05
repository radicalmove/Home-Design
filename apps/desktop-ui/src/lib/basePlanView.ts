import type { ProjectManifest } from "../types";

export function basePlanBackgroundAssetPath(project: ProjectManifest): string {
  return project.views.find((view) => view.mode === "furniture_editor")?.asset_path
    ?? project.views.find((view) => view.mode === "base_plan")?.asset_path
    ?? "/views/reference_plan.svg";
}
