import { describe, expect, it } from "vitest";
import editorSource from "./FurnitureEditorView.svelte?raw";
import layerControlsSource from "./FurnitureLayerControls.svelte?raw";
import planCanvasSource from "./PlanCanvas.svelte?raw";

describe("furniture canvas interaction layout", () => {
  it("uses a crisp SVG viewBox canvas with a tall editing viewport", () => {
    expect(planCanvasSource).toContain("viewBox={viewBoxValue}");
    expect(planCanvasSource).not.toContain("scale(${zoom})");
    expect(planCanvasSource).toMatch(/\.plan-canvas\s*{[\s\S]*overflow:\s*hidden;/);
    expect(planCanvasSource).toMatch(/\.plan-canvas\s*{[\s\S]*aspect-ratio:\s*1\s*\/\s*2;/);
    expect(planCanvasSource).toMatch(/svg\s*{[\s\S]*height:\s*100%;/);
  });

  it("hides furniture abbreviation labels by default behind a toggle", () => {
    expect(editorSource).toContain("let labelsVisible = $state(false);");
    expect(editorSource).toContain("labelsVisible={labelsVisible}");
    expect(editorSource).toContain("showLabels={labelsVisible}");
    expect(layerControlsSource).toContain("labelsVisible: boolean;");
    expect(layerControlsSource).toContain("onToggleLabels: () => void;");
    expect(layerControlsSource).toContain("checked={labelsVisible}");
    expect(planCanvasSource).toContain("showLabels: boolean;");
    expect(planCanvasSource).toContain("{#if showLabels && symbol.abbreviation}");
  });
});
