import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import catalogSource from "./FurnitureCatalogPanel.svelte?raw";
import editorSource from "./FurnitureEditorView.svelte?raw";
import inspectorSource from "./FurnitureObjectInspector.svelte?raw";
import layerControlsSource from "./FurnitureLayerControls.svelte?raw";
import planCanvasSource from "./PlanCanvas.svelte?raw";
import furnitureBackgroundSource from "../public/views/reference_plan.svg?raw";

const appStylesSource = readFileSync(new URL("./styles.css", import.meta.url), "utf8");

function cssBlock(source: string, selector: string): string {
  const escapedSelector = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return source.match(new RegExp(`${escapedSelector}\\s*{(?<body>[\\s\\S]*?)}`))?.groups?.body ?? "";
}

function setLiteralBlock(source: string, name: string): string {
  return source.match(new RegExp(`const ${name} = new Set\\(\\[(?<body>[\\s\\S]*?)\\]\\);`))?.groups?.body ?? "";
}

function sourceBetween(source: string, start: string, end: string): string {
  const startIndex = source.indexOf(start);
  if (startIndex === -1) {
    return "";
  }

  const endIndex = source.indexOf(end, startIndex + start.length);
  return endIndex === -1 ? source.slice(startIndex) : source.slice(startIndex, endIndex);
}

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

  it("renders L-shaped furniture footprints and exposes arm dimension fields", () => {
    expect(planCanvasSource).toContain("lShapePath");
    expect(planCanvasSource).toContain('symbol.shape === "l-shape"');
    expect(planCanvasSource).toContain("object.l_shape");
    expect(inspectorSource).toContain("updateLShapeMainDepth");
    expect(inspectorSource).toContain("updateLShapeReturnWidth");
    expect(inspectorSource).toContain("Main arm D m");
    expect(inspectorSource).toContain("Return W m");
  });

  it("renders bedroom storage, thin partition wall, and wardrobe-door furniture symbols", () => {
    expect(planCanvasSource).toContain('symbol.shape === "bedside-table"');
    expect(planCanvasSource).toContain('symbol.shape === "drawers"');
    expect(planCanvasSource).toContain('symbol.shape === "partition-wall"');
    expect(planCanvasSource).toContain("rx={symbolCornerRadius(symbol.shape)}");
    expect(planCanvasSource).toContain('symbol.shape === "sliding-door"');
  });

  it("locks thin linear object thickness in canvas and inspector resizing controls", () => {
    expect(planCanvasSource).toContain("fixedDepthForObject");
    expect(planCanvasSource).toContain("resizeHandlesForObject(object)");
    expect(planCanvasSource).toContain("deltaDepthM: 0");
    expect(inspectorSource).toContain("fixedDepthForObject");
    expect(inspectorSource).toContain("readonly={hasFixedDepth}");
  });

  it("draws wardrobe doors as white sliding panels like the reference wardrobe doors", () => {
    const outlineOnlySymbols = setLiteralBlock(planCanvasSource, "OUTLINE_ONLY_SYMBOLS");

    expect(outlineOnlySymbols).toContain('"sliding-door"');
    expect(planCanvasSource).toContain('class="symbol-hit-target"');
    expect(planCanvasSource).toContain('class="wardrobe-door-panel fixed"');
    expect(planCanvasSource).toContain('class="wardrobe-door-panel sliding"');
    expect(planCanvasSource).toContain("rx={symbolCornerRadius(symbol.shape)}");
    expect(planCanvasSource).toContain("x={bounds.x}");
    expect(planCanvasSource).toContain("width={bounds.width * 0.58}");
    expect(planCanvasSource).toContain(":not(.symbol-hit-target)");
    expect(planCanvasSource).toMatch(/\.symbol-hit-target\s*{[\s\S]*stroke:\s*none;/);
    expect(planCanvasSource).toMatch(/\.symbol-hit-target\s*{[\s\S]*pointer-events:\s*all;/);
    expect(planCanvasSource).toMatch(/\.wardrobe-door-panel\s*{[\s\S]*fill:\s*#fffdf8;/);
    expect(planCanvasSource).toMatch(/\.wardrobe-door-panel\s*{[\s\S]*stroke:\s*#111;/);
    expect(planCanvasSource).toMatch(/\.wardrobe-door-panel\s*{[\s\S]*stroke-width:\s*0\.45;/);
  });

  it("renders live wall-distance guides while furniture is moving", () => {
    expect(planCanvasSource).toContain("nearestWallDistanceGuides");
    expect(planCanvasSource).toContain("wallDistanceGuides");
    expect(planCanvasSource).toContain("wall-distance-guide");
    expect(planCanvasSource).toContain("REFERENCE_WALL_SEGMENTS");
  });

  it("passes reference wall stroke widths into wall-distance guide geometry", () => {
    expect(planCanvasSource).toContain("WALL_THICKNESS_PX");
    expect(planCanvasSource).toContain("withWallThickness");
    expect(planCanvasSource).toContain("thickness_px");
  });

  it("sizes wall-distance labels from screen pixels instead of fixed SVG text", () => {
    expect(planCanvasSource).toContain("wallDistanceLabelFontSize");
    expect(planCanvasSource).toContain("wallDistanceLabelStrokeWidth");
    expect(planCanvasSource).toContain("font-size={wallDistanceLabelFontSize}");
    expect(planCanvasSource).toContain("stroke-width={wallDistanceLabelStrokeWidth}");
    expect(planCanvasSource).not.toContain("font-size: 8px");
  });

  it("renders fireplace, TV, and heat-pump furniture symbols", () => {
    expect(planCanvasSource).toContain('symbol.shape === "fireplace"');
    expect(planCanvasSource).toContain('symbol.shape === "tv"');
    expect(planCanvasSource).toContain('symbol.shape === "heat-pump"');
  });

  it("draws Planner-style bathroom, laundry, and kitchen symbols", () => {
    const toiletBranch = sourceBetween(
      planCanvasSource,
      '{:else if symbol.shape === "toilet"}',
      '{:else if symbol.shape === "shower"}',
    );

    expect(planCanvasSource).toContain('symbolForFurnitureObject(object.type, object.abbreviation, object.catalog_id)');
    expect(planCanvasSource).toContain('symbol.shape === "bath"');
    expect(planCanvasSource).toContain('class="bath-inner"');
    expect(planCanvasSource).toContain('symbol.shape === "basin"');
    expect(planCanvasSource).toContain('class="basin-bowl"');
    expect(planCanvasSource).toContain('symbol.shape === "toilet"');
    expect(planCanvasSource).toContain('class="toilet-tank"');
    expect(planCanvasSource).toContain('class="toilet-bowl"');
    expect(planCanvasSource).toContain('class="toilet-inlay"');
    expect(planCanvasSource).toContain(":not(.toilet-tank)");
    expect(planCanvasSource).toContain(":not(.toilet-bowl):not(.toilet-inlay)");
    expect(toiletBranch).toContain("x={bounds.x}");
    expect(toiletBranch).toContain("y={bounds.y}");
    expect(toiletBranch).toContain("width={bounds.width}");
    expect(planCanvasSource).toContain('symbol.shape === "shower"');
    expect(planCanvasSource).toContain('class="shower-head"');
    expect(planCanvasSource).not.toContain('class="shower-door-swing"');
    expect(planCanvasSource).not.toContain('x={bounds.x + bounds.width * 0.05} y={bounds.y + bounds.height * 0.05} width={bounds.width * 0.9} height={bounds.height * 0.9}');
    expect(planCanvasSource).toContain('symbol.shape === "washer" || symbol.shape === "dryer"');
    expect(planCanvasSource).toContain('symbol.shape === "refrigerator"');
    expect(planCanvasSource).toContain('symbol.shape === "oven"');
    expect(planCanvasSource).toContain('symbol.shape === "island"');
    expect(planCanvasSource).toContain('class="symbol-mark"');
  });

  it("draws Planner-style common furniture silhouettes", () => {
    const stoolBranch = sourceBetween(
      planCanvasSource,
      '{:else if symbol.shape === "stool"}',
      '{:else if symbol.shape === "armchair"}',
    );

    expect(planCanvasSource).toContain('symbol.shape === "table-and-chairs"');
    expect(planCanvasSource).toContain('class="table-chair top"');
    expect(planCanvasSource).toContain('symbol.shape === "stool"');
    expect(planCanvasSource).toMatch(/<rect\s+class="stool-seat symbol-body"[\s\S]*rx=/);
    expect(planCanvasSource).not.toContain('<ellipse class="stool-seat symbol-body"');
    expect(stoolBranch).toContain("x={bounds.x}");
    expect(stoolBranch).toContain("y={bounds.y}");
    expect(stoolBranch).toContain("width={bounds.width}");
    expect(stoolBranch).toContain("height={bounds.height}");
    expect(planCanvasSource).toContain('symbol.shape === "armchair"');
    expect(planCanvasSource).toContain('class="armchair-arm left"');
    expect(planCanvasSource).toContain('symbol.shape === "wardrobe"');
    expect(planCanvasSource).toContain('class="wardrobe-base-line"');
    expect(planCanvasSource).toContain('class="bed-blanket-fold"');
    expect(planCanvasSource).toContain('class="sofa-cushion-divider"');
  });

  it("uses solid outlines for all fixed furniture symbol bodies", () => {
    const fixedSymbolStyle = cssBlock(planCanvasSource, ".furniture-object.fixed .symbol-body");

    expect(fixedSymbolStyle).toContain("stroke-dasharray: none;");
    expect(fixedSymbolStyle).not.toContain("stroke-dasharray: 4 2;");
  });

  it("keeps desk and cabinet-style symbol bodies square-cornered", () => {
    const squareCornerSymbols = setLiteralBlock(planCanvasSource, "SQUARE_CORNER_SYMBOLS");

    expect(planCanvasSource).toContain("const SQUARE_CORNER_SYMBOLS");
    expect(planCanvasSource).toContain('"bedside-table"');
    expect(planCanvasSource).toContain('"desk"');
    expect(planCanvasSource).toContain('"drawers"');
    expect(squareCornerSymbols).toContain('"shower"');
    expect(planCanvasSource).toContain('"storage"');
    expect(planCanvasSource).toContain('"wardrobe"');
    expect(planCanvasSource).toContain("function symbolCornerRadius");
    expect(planCanvasSource).toContain("rx={symbolCornerRadius(symbol.shape)}");
    expect(planCanvasSource).toContain('class="bedside-table-top"');
    expect(planCanvasSource).toContain('rx="0"');
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

  it("keeps rotate handles filled and clickable over circular symbol styling", () => {
    const rotateHandleStyle = cssBlock(planCanvasSource, ".rotate-handle");

    expect(planCanvasSource).toContain("circle:not(.symbol-body):not(.rotate-handle)");
    expect(rotateHandleStyle).toContain("fill: #ffffff;");
    expect(rotateHandleStyle).toContain("pointer-events: all;");
  });

  it("keeps collapsed catalog groups stacked at the top of the scroll panel", () => {
    expect(catalogSource).toMatch(/\.catalog-groups\s*{[\s\S]*align-content:\s*start;/);
  });

  it("keeps catalog wheel scrolling isolated from the main furniture view", () => {
    expect(catalogSource).toContain("stopCatalogWheelPropagation");
    expect(catalogSource).toContain("onwheel={stopCatalogWheelPropagation}");
    expect(catalogSource).toMatch(/\.catalog-groups\s*{[\s\S]*overscroll-behavior:\s*contain;/);
    expect(appStylesSource).toMatch(/body\s*{[^}]*overflow:\s*hidden;/);
    expect(appStylesSource).toMatch(/\.workspace\s*{[^}]*height:\s*100vh;/);
    expect(appStylesSource).toMatch(/\.workspace\s*{[^}]*overflow:\s*hidden;/);
    expect(editorSource).toMatch(/\.furniture-editor\s*{[\s\S]*height:\s*100%;/);
    expect(editorSource).toMatch(/\.furniture-editor\s*{[\s\S]*overflow:\s*hidden;/);
  });

  it("filters catalog objects as search text is entered", () => {
    expect(catalogSource).toContain("let searchQuery = $state(\"\");");
    expect(catalogSource).toContain("filteredGroups");
    expect(catalogSource).toContain("catalogSearchText");
    expect(catalogSource).toContain('type="search"');
    expect(catalogSource).toContain('aria-label="Search catalog objects"');
    expect(catalogSource).toContain("bind:value={searchQuery}");
    expect(catalogSource).toContain("{#each filteredGroups as group}");
  });

  it("lets the selected object switch between fixed and moveable layers", () => {
    expect(editorSource).toContain("changeObjectLayer");
    expect(editorSource).toContain("onChangeLayer={handleChangeLayer}");
    expect(inspectorSource).toContain("onChangeLayer: (objectId: string, layer: FurnitureLayerKind) => void;");
    expect(inspectorSource).toContain("<select");
    expect(inspectorSource).toContain('<option value="fixed">Fixed</option>');
    expect(inspectorSource).toContain('<option value="moveable">Moveable</option>');
  });

  it("renders furniture in sorted global z-index order", () => {
    expect(planCanvasSource).toContain("sortedFurnitureObjects");
    expect(planCanvasSource).toContain("sortedFurnitureObjects(layout.objects)");
    expect(planCanvasSource).toContain("let visibleObjects = $derived(");
  });

  it("wires selected furniture order controls through the editor commit path", () => {
    expect(editorSource).toContain("reorderObject");
    expect(editorSource).toContain("handleReorderObject");
    expect(editorSource).toContain("const nextLayout = reorderObject(layout, objectId, action);");
    expect(editorSource).toContain("if (nextLayout !== layout) {");
    expect(editorSource).toContain("commitLayout(nextLayout)");
    expect(editorSource).toContain("onReorder={handleReorderObject}");
  });

  it("batches canvas drag edits into one undo history entry on pointer release", () => {
    expect(editorSource).toContain("finishFurnitureGestureHistory");
    expect(editorSource).toContain("let activeObjectEditSnapshot = $state<FurnitureHistorySnapshot | null>(null);");
    expect(editorSource).toContain("function handleBeginObjectEdit(objectId: string)");
    expect(editorSource).toContain("function handleFinishObjectEdit()");
    expect(editorSource).toContain("previewLayout");
    expect(editorSource).toContain("onBeginObjectEdit={handleBeginObjectEdit}");
    expect(editorSource).toContain("onFinishObjectEdit={handleFinishObjectEdit}");
    expect(planCanvasSource).toContain("onBeginObjectEdit: (objectId: string) => void;");
    expect(planCanvasSource).toContain("onFinishObjectEdit: () => void;");
    expect(planCanvasSource).toContain("onBeginObjectEdit(object.id)");
    expect(planCanvasSource).toContain("onFinishObjectEdit();");
  });

  it("exposes global furniture order controls in the selected object inspector", () => {
    expect(inspectorSource).toContain('onReorder: (objectId: string, action: FurnitureOrderAction) => void;');
    expect(inspectorSource).toContain('aria-label="Furniture order controls"');
    expect(inspectorSource).toContain("Send to Back");
    expect(inspectorSource).toContain("Send Backward");
    expect(inspectorSource).toContain("Bring Forward");
    expect(inspectorSource).toContain("Bring to Front");
  });

  it("adds catalog furniture at the centre of the current canvas viewport", () => {
    expect(planCanvasSource).toContain("onViewportCenterChange");
    expect(planCanvasSource).toContain("svgToMetres");
    expect(planCanvasSource).toContain("visibleCanvasCenterOffset");
    expect(planCanvasSource).toContain("svgPointInViewBox");
    expect(planCanvasSource).toContain("window.innerWidth");
    expect(planCanvasSource).toContain("window.innerHeight");
    expect(editorSource).toContain("currentViewportCenter");
    expect(editorSource).toContain("onViewportCenterChange={(point) => (currentViewportCenter = point)}");
    expect(editorSource).toContain("addCatalogItem(layout, item, currentViewportCenter ??");
    expect(editorSource).not.toContain("selectedObject.x_m + 0.35");
    expect(editorSource).not.toContain("catalogItemTopLeftForViewportCenter");
  });

  it("provides bounded undo and redo controls plus keyboard shortcuts", () => {
    expect(editorSource).toContain("FURNITURE_HISTORY_LIMIT");
    expect(editorSource).toContain("pushFurnitureHistory");
    expect(editorSource).toContain("undoFurnitureHistory");
    expect(editorSource).toContain("redoFurnitureHistory");
    expect(editorSource).toContain("undoStack");
    expect(editorSource).toContain("redoStack");
    expect(editorSource).toContain("aria-label=\"Undo\"");
    expect(editorSource).toContain("aria-label=\"Redo\"");
    expect(editorSource).toContain("isUndoKeyboardShortcut");
    expect(editorSource).toContain("isRedoKeyboardShortcut");
    expect(editorSource).toContain("event.ctrlKey || event.metaKey");
  });

  it("deletes the selected object from the keyboard when focus is not in an editable field", () => {
    expect(editorSource).toContain("<svelte:window onkeydown={handleEditorKeyDown}");
    expect(editorSource).toContain("isEditableKeyboardTarget");
    expect(editorSource).toContain('event.key !== "Delete"');
    expect(editorSource).toContain('event.key !== "Backspace"');
    expect(editorSource).toContain("handleDeleteObject(selectedObjectId)");
  });
});
