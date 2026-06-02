import { describe, expect, it } from "vitest";
import appSource from "./App.svelte?raw";
import designReviewSource from "./DesignReviewView.svelte?raw";
import designReviewAnalysisSource from "./lib/designReview?raw";

describe("design review view wiring", () => {
  it("routes the design review manifest mode into the Svelte report view", () => {
    expect(appSource).toContain('import DesignReviewView from "./DesignReviewView.svelte";');
    expect(appSource).toContain('selectedView.mode === "design_review"');
    expect(appSource).toContain("<DesignReviewView projectId={project.id} />");
  });

  it("renders the core report headings and live evidence controls", () => {
    expect(designReviewSource).toContain("analysis.reportSections");
    expect(designReviewAnalysisSource).toContain("Executive View");
    expect(designReviewAnalysisSource).toContain("Movement Flow");
    expect(designReviewAnalysisSource).toContain("Light And Seasons");
    expect(designReviewAnalysisSource).toContain("Room-By-Room Review");
    expect(designReviewAnalysisSource).toContain("Priority Actions");
    expect(designReviewSource).toContain("Refresh Review");
    expect(designReviewSource).toContain("Plan Snippets");
  });
});
