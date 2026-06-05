import type { DesignScenarioDescriptor, ProjectManifest, ViewDescriptor } from "../types";
import { CURRENT_SCENARIO_ID, sortedScenarios } from "./designScenarios";

const ESTIMATED_COST_SCENARIO_IDS = new Set(["back-side-living-sunroom-bedroom"]);

export type ScenarioViewSelection = {
  scenarioId: string;
  viewId: string;
};

export function isViewAvailableForScenario(view: ViewDescriptor, scenarioId: string | null): boolean {
  return view.mode !== "estimated_cost" || (scenarioId !== null && ESTIMATED_COST_SCENARIO_IDS.has(scenarioId));
}

export function viewsForScenario(project: ProjectManifest, scenarioId: string | null): ViewDescriptor[] {
  return project.views.filter((view) => isViewAvailableForScenario(view, scenarioId));
}

export function firstAvailableViewId(project: ProjectManifest, scenarioId: string | null = null): string | null {
  return viewsForScenario(project, scenarioId).find((view) => view.available)?.id ?? null;
}

export function selectAvailableView(
  project: ProjectManifest,
  requestedId: string | null,
  scenarioId: string | null = null,
): string | null {
  if (
    requestedId
    && viewsForScenario(project, scenarioId).some((view) => view.id === requestedId && view.available)
  ) {
    return requestedId;
  }
  return firstAvailableViewId(project, scenarioId);
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
  const viewId = selectAvailableView(project, requestedViewId, scenarioId);

  if (!scenarioId || !viewId) {
    return null;
  }

  return { scenarioId, viewId };
}
