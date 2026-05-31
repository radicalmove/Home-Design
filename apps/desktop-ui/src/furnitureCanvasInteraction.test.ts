import { describe, expect, it } from "vitest";
import planCanvasSource from "./PlanCanvas.svelte?raw";

describe("furniture canvas interaction layout", () => {
  it("clips a transformed plan stage so hand panning can move in both axes", () => {
    expect(planCanvasSource).toContain('class="plan-stage"');
    expect(planCanvasSource).toMatch(/\.plan-canvas\s*{[\s\S]*overflow:\s*hidden;/);
    expect(planCanvasSource).toMatch(/\.plan-stage\s*{[\s\S]*transform-origin:\s*0 0;/);
  });
});
