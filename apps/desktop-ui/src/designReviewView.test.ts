import { describe, expect, it } from "vitest";
import appSource from "./App.svelte?raw";
import designReviewSource from "./DesignReviewView.svelte?raw";
import designReviewAnalysisSource from "./lib/designReview?raw";

describe("design review view wiring", () => {
  it("routes the design review manifest mode into the Svelte report view", () => {
    expect(appSource).toContain('import DesignReviewView from "./DesignReviewView.svelte";');
    expect(appSource).toContain('selectedView.mode === "design_review"');
    expect(appSource).toContain("<DesignReviewView projectId={project.id} scenarioId={selectedScenario.id} />");
  });

  it("renders the core report headings and live evidence controls", () => {
    expect(designReviewSource).toContain("scenarioId: string;");
    expect(designReviewSource).toContain("loadDesignReviewData(projectId, scenarioId)");
    expect(designReviewSource).toContain("analysis.overallAssessment");
    expect(designReviewSource).toContain("analysis.summarySections");
    expect(designReviewSource).toContain("analysis.practicalFindings");
    expect(designReviewSource).toContain("analysis.reportSections");
    expect(designReviewSource).toContain("analysis.roomAnalyses");
    expect(designReviewSource).toContain("analysis.movementScenarios");
    expect(designReviewSource).toContain("analysis.movementMapViewBox");
    expect(designReviewSource).toContain("analysis.expertReview");
    expect(designReviewAnalysisSource).toContain("Strengths");
    expect(designReviewAnalysisSource).toContain("Weaknesses");
    expect(designReviewAnalysisSource).toContain("Moveable Furniture Opportunities");
    expect(designReviewAnalysisSource).toContain("Good daylight is partly landing in low-use service spaces");
    expect(designReviewAnalysisSource).toContain("The lounge is a sitting room and a movement junction");
    expect(designReviewAnalysisSource).toContain("Sunroom comfort is seasonal");
    expect(designReviewAnalysisSource).toContain("Overall Assessment");
    expect(designReviewAnalysisSource).not.toContain("Three Weaknesses In The Previous Pass");
    expect(designReviewAnalysisSource).not.toContain("Final Overall Review");
    expect(designReviewSource).not.toContain("analysis.selfCritique");
    expect(designReviewAnalysisSource).toContain("front door");
    expect(designReviewAnalysisSource).toContain("deck");
    expect(designReviewAnalysisSource).toContain("second toilet");
    expect(designReviewAnalysisSource).toContain("redoing the bathroom");
    expect(designReviewAnalysisSource).toContain("Useful Light And Daily Rhythm");
    expect(designReviewSource).toContain("Refresh Review");
    expect(designReviewSource).toContain("Plan Snippets");
    expect(designReviewSource).toContain("Theoretical Movement Map");
    expect(designReviewSource).toContain("Room-By-Room Analysis");
    expect(designReviewSource).toContain("Expert Review Lens");
    expect(designReviewSource).toContain("Data Snapshot");
    expect(designReviewSource).toContain("summary-list");
    expect(designReviewSource).not.toContain(".summary-grid {\n    display: grid;\n    grid-template-columns: repeat(3");
  });
});
