import { describe, expect, it } from "vitest";
import catalogSource from "./FurnitureCatalogPanel.svelte?raw";
import editorSource from "./FurnitureEditorView.svelte?raw";
import inspectorSource from "./FurnitureObjectInspector.svelte?raw";
import layerControlsSource from "./FurnitureLayerControls.svelte?raw";
import planCanvasSource from "./PlanCanvas.svelte?raw";
import furnitureBackgroundSource from "../public/views/reference_plan.svg?raw";

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

  it("hides reference room labels by default behind a separate toggle", () => {
    expect(editorSource).toContain("let roomLabelsVisible = $state(false);");
    expect(editorSource).toContain("roomLabelsVisible={roomLabelsVisible}");
    expect(editorSource).toContain("showRoomLabels={roomLabelsVisible}");
    expect(layerControlsSource).toContain("roomLabelsVisible: boolean;");
    expect(layerControlsSource).toContain("onToggleRoomLabels: () => void;");
    expect(layerControlsSource).toContain("checked={roomLabelsVisible}");
    expect(layerControlsSource).toContain("Room Labels");
    expect(planCanvasSource).toContain("showRoomLabels: boolean;");
    expect(planCanvasSource).toContain("class=\"room-label-layer\"");
    expect(planCanvasSource).toContain("{#if showRoomLabels}");
  });

  it("uses a label-free packaged reference background for furniture editing", () => {
    expect(furnitureBackgroundSource).not.toContain('class="ref-room-label"');
    expect(furnitureBackgroundSource).toContain('class="ref-site-label"');
  });

  it("renders side and corner handles for anchored furniture resizing", () => {
    expect(planCanvasSource).toContain("const RESIZE_HANDLES");
    expect(planCanvasSource).toContain('name: "n"');
    expect(planCanvasSource).toContain('name: "e"');
    expect(planCanvasSource).toContain('name: "s"');
    expect(planCanvasSource).toContain('name: "w"');
    expect(planCanvasSource).toContain('name: "nw"');
    expect(planCanvasSource).toContain('name: "se"');
    expect(planCanvasSource).toContain("data-resize-handle={handle.name}");
    expect(planCanvasSource).toContain("startResize(event, object, handle.name)");
  });

  it("sizes edit handles from screen pixels instead of fixed SVG units", () => {
    expect(planCanvasSource).toContain("screenPixelsToSvgUnits");
    expect(planCanvasSource).toContain("resizeHandleSize");
    expect(planCanvasSource).toContain("rotateHandleRadius");
    expect(planCanvasSource).toContain("width={resizeHandleSize}");
    expect(planCanvasSource).toContain("height={resizeHandleSize}");
    expect(planCanvasSource).toContain("r={rotateHandleRadius}");
    expect(planCanvasSource).not.toContain('width="10"');
    expect(planCanvasSource).not.toContain('r="7"');
  });

  it("keeps collapsed catalog groups stacked at the top of the scroll panel", () => {
    expect(catalogSource).toMatch(/\.catalog-groups\s*{[\s\S]*align-content:\s*start;/);
  });

  it("lets the selected object switch between fixed and moveable layers", () => {
    expect(editorSource).toContain("changeObjectLayer");
    expect(editorSource).toContain("onChangeLayer={handleChangeLayer}");
    expect(inspectorSource).toContain("onChangeLayer: (objectId: string, layer: FurnitureLayerKind) => void;");
    expect(inspectorSource).toContain("<select");
    expect(inspectorSource).toContain('<option value="fixed">Fixed</option>');
    expect(inspectorSource).toContain('<option value="moveable">Moveable</option>');
  });
});
