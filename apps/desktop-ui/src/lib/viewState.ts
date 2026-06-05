import type { DesignScenarioDescriptor, ProjectManifest, ViewDescriptor } from "../types";
import { CURRENT_SCENARIO_ID, sortedScenarios } from "./designScenarios";

export type ScenarioViewSelection = {
  scenarioId: string;
  viewId: string;
};

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

export function firstScenarioId(project: ProjectManifest): string | null {
  const scenarios = sortedScenarios(project);
  return (
    scenarios.find((scenario) => scenario.id === CURRENT_SCENARIO_ID)?.id ??
    scenarios[0]?.id ??
    null
  );
}

export function selectAvailableScenario(
  project: ProjectManifest,
  requestedScenarioId: string | null,
): string | null {
  if (requestedScenarioId && project.scenarios.some((scenario) => scenario.id === requestedScenarioId)) {
    return requestedScenarioId;
  }
  return firstScenarioId(project);
}

export function activeScenario(
  project: ProjectManifest | null,
  selectedScenarioId: string | null,
): DesignScenarioDescriptor | null {
  if (!project) {
    return null;
  }

  const scenarioId = selectAvailableScenario(project, selectedScenarioId);
  if (!scenarioId) {
    return null;
  }
  return project.scenarios.find((scenario) => scenario.id === scenarioId) ?? null;
}

export function selectAvailableScenarioView(
  project: ProjectManifest,
  requestedScenarioId: string | null,
  requestedViewId: string | null,
): ScenarioViewSelection | null {
  const scenarioId = selectAvailableScenario(project, requestedScenarioId);
  const viewId = selectAvailableView(project, requestedViewId);

  if (!scenarioId || !viewId) {
    return null;
  }

  return { scenarioId, viewId };
}
