import { describe, expect, it } from "vitest";
import planCanvasSource from "./PlanCanvas.svelte?raw";

describe("furniture canvas interaction layout", () => {
  it("uses a crisp SVG viewBox canvas with a tall editing viewport", () => {
    expect(planCanvasSource).toContain("viewBox={viewBoxValue}");
    expect(planCanvasSource).not.toContain("scale(${zoom})");
    expect(planCanvasSource).toMatch(/\.plan-canvas\s*{[\s\S]*overflow:\s*hidden;/);
    expect(planCanvasSource).toMatch(/\.plan-canvas\s*{[\s\S]*aspect-ratio:\s*1\s*\/\s*2;/);
    expect(planCanvasSource).toMatch(/svg\s*{[\s\S]*height:\s*100%;/);
  });
});
