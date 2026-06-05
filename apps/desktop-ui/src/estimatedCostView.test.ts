import { describe, expect, it } from "vitest";
import appSource from "./App.svelte?raw";
import estimatedCostViewSource from "./EstimatedCostView.svelte?raw";

describe("estimated cost view wiring", () => {
  it("routes the estimated cost manifest mode into a Design 2 native cost view", () => {
    expect(appSource).toContain('import EstimatedCostView from "./EstimatedCostView.svelte";');
    expect(appSource).toContain('selectedView.mode === "estimated_cost"');
    expect(appSource).toContain("<EstimatedCostView projectId={project.id} scenarioId={selectedScenario.id} />");
    expect(appSource).toContain("viewsForScenario(project, scenario.id)");
  });

  it("loads design review data and renders cost, roof, assumptions, and exclusions", () => {
    expect(estimatedCostViewSource).toContain("loadDesignReviewData(projectId, scenarioId)");
    expect(estimatedCostViewSource).toContain("buildEstimatedCostAnalysis");
    expect(estimatedCostViewSource).toContain("Planning Range");
    expect(estimatedCostViewSource).toContain("Roof And Envelope");
    expect(estimatedCostViewSource).toContain("Furniture Editor Signals");
    expect(estimatedCostViewSource).toContain("Assumptions");
    expect(estimatedCostViewSource).toContain("Exclusions");
  });

  it("keeps the long cost breakdown scrollable inside the clipped workspace", () => {
    expect(estimatedCostViewSource).toContain("height: 100%;");
    expect(estimatedCostViewSource).toContain("min-height: 0;");
    expect(estimatedCostViewSource).toContain("overflow: auto;");
  });

  it("renders detailed cost items as readable stacked rows instead of a squeezed table", () => {
    expect(estimatedCostViewSource).toContain('class="cost-line-list"');
    expect(estimatedCostViewSource).toContain('class="cost-line"');
    expect(estimatedCostViewSource).toContain('class="cost-line-range"');
    expect(estimatedCostViewSource).not.toContain("<table>");
    expect(estimatedCostViewSource).not.toContain("<th");
  });
});
