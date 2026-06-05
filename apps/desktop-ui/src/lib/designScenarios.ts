import type { DesignScenarioDescriptor, ProjectManifest } from "../types";

export const CURRENT_SCENARIO_ID = "current";

export function isCurrentScenario(scenarioId: string | null): boolean {
  return scenarioId === CURRENT_SCENARIO_ID;
}

export function sortedScenarios(project: ProjectManifest): DesignScenarioDescriptor[] {
  return [...project.scenarios].sort((a, b) => a.rank - b.rank);
}

