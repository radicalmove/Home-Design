import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";

const repoRoot = new URL("../../../../", import.meta.url);

function readRepoFile(path: string): string {
  return readFileSync(new URL(path, repoRoot), "utf8");
}

describe("visual QA process guard", () => {
  it("keeps the visual QA gate embedded in project docs and desktop checks", () => {
    const visualQaGuide = readRepoFile("VISUAL_QA.md");
    const agentInstructions = readRepoFile("AGENTS.md");
    const packageJson = JSON.parse(readRepoFile("apps/desktop-ui/package.json")) as {
      scripts?: Record<string, string>;
    };
    const visualQaScript = readRepoFile("apps/desktop-ui/scripts/visual-qa-check.mjs");
    const readme = readRepoFile("README.md");

    expect(visualQaGuide).toContain("# Visual QA Gate");
    expect(visualQaGuide).toContain("Rendered visual inspection is mandatory for visual changes.");
    expect(visualQaGuide).toContain("Compare against Design 1 or the relevant reference view");
    expect(visualQaGuide).toContain("wall continuity");
    expect(visualQaGuide).toContain("window and door style");
    expect(visualQaGuide).toContain("flooring continuity");
    expect(visualQaGuide).toContain("furniture crossing walls");
    expect(visualQaGuide).toContain("Do not claim a visual change is complete from tests alone.");

    expect(agentInstructions).toContain("Follow `VISUAL_QA.md` for any visual app change.");
    expect(agentInstructions).toContain("Do not rely only on coordinate tests, source tests, or successful builds");

    expect(packageJson.scripts?.["visual-qa"]).toBe("node scripts/visual-qa-check.mjs");
    expect(packageJson.scripts?.check).toContain("npm run visual-qa");
    expect(visualQaScript).toContain("VISUAL_QA.md");
    expect(visualQaScript).toContain("Visual QA gate is present");
    expect(readme).toContain("npm run visual-qa --prefix apps/desktop-ui");
  });
});
