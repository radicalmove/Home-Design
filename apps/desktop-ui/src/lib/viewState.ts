import type { ProjectManifest, ViewDescriptor } from "../types";

export function firstAvailableViewId(project: ProjectManifest): string | null {
  return project.views.find((view) => view.available)?.id ?? null;
}

export function selectAvailableView(project: ProjectManifest, requestedId: string | null): string | null {
  if (requestedId && project.views.some((view) => view.id === requestedId && view.available)) {
    return requestedId;
  }
  return firstAvailableViewId(project);
}

export function activeView(
  project: ProjectManifest | null,
  selectedViewId: string | null,
): ViewDescriptor | null {
  if (!project || !selectedViewId) {
    return null;
  }
  return project.views.find((view) => view.id === selectedViewId) ?? null;
}
