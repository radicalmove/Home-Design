import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import appSource from "./App.svelte?raw";
import planCanvasSource from "./PlanCanvas.svelte?raw";

const baseViewPath = new URL("./BaseView.svelte", import.meta.url);
let baseViewSource = "";
try {
  baseViewSource = readFileSync(baseViewPath, "utf8");
} catch {
  baseViewSource = "";
}

describe("base view furniture overlays", () => {
  it("routes the packaged base plan through the native base view overlay", () => {
    expect(appSource).toContain('import BaseView from "./BaseView.svelte";');
    expect(appSource).toContain('import { basePlanBackgroundAssetPath } from "./lib/basePlanView";');
    expect(appSource).toContain('selectedView.mode === "base_plan"');
    expect(appSource).toContain("<BaseView");
    expect(appSource).toContain("scenarioId={selectedScenario.id}");
    expect(appSource).toContain("resetKey={viewActivationKey}");
    expect(appSource).toContain("backgroundAssetPath={basePlanBackgroundAssetPath(project)}");
  });

  it("loads the current saved furniture layout and keeps all 2D overlay layers off by default", () => {
    expect(baseViewSource).toContain("scenarioId: string;");
    expect(baseViewSource).toContain("resetKey: number;");
    expect(baseViewSource).toContain("loadFurnitureLayout(projectId, scenarioId)");
    expect(baseViewSource).toContain("normaliseFurnitureLayout");
    expect(baseViewSource).toContain("let fixedVisible = $state(false);");
    expect(baseViewSource).toContain("let moveableVisible = $state(false);");
    expect(baseViewSource).toContain("let labelsVisible = $state(false);");
    expect(baseViewSource).toContain("let roomLabelsVisible = $state(false);");
    expect(baseViewSource).toContain('import FurnitureLayerControls from "./FurnitureLayerControls.svelte";');
    expect(baseViewSource).toContain("<FurnitureLayerControls");
    expect(baseViewSource).toContain("labelsVisible={labelsVisible}");
    expect(baseViewSource).toContain("roomLabelsVisible={roomLabelsVisible}");
    expect(baseViewSource).toContain("onToggleLabels={() => (labelsVisible = !labelsVisible)}");
    expect(baseViewSource).toContain("onToggleRoomLabels={() => (roomLabelsVisible = !roomLabelsVisible)}");
    expect(baseViewSource).not.toContain("Fixed Furniture");
    expect(baseViewSource).not.toContain("Moveable Furniture");
  });

  it("keeps the 2D layer toggles as literal visibility switches", () => {
    expect(baseViewSource).toContain("fixedVisible={fixedVisible}");
    expect(baseViewSource).toContain("moveableVisible={moveableVisible}");
    expect(baseViewSource).toContain("showLabels={labelsVisible}");
    expect(baseViewSource).toContain("showRoomLabels={roomLabelsVisible}");
    expect(baseViewSource).not.toContain("fixedVisible={fixedVisible || activeTransitionProgress > 0}");
    expect(baseViewSource).not.toContain("moveableVisible={moveableVisible || activeTransitionProgress > 0}");
    expect(baseViewSource).not.toContain("showLabels={false}");
    expect(baseViewSource).not.toContain("showRoomLabels={false}");
  });

  it("reuses the furniture editor zoom contract up to 2000 percent", () => {
    expect(baseViewSource).toContain("clampPlanZoom");
    expect(baseViewSource).toContain("resetKey;");
    expect(baseViewSource).toContain("planZoom = 1;");
    expect(baseViewSource).toContain("planZoomLabel(planZoom)");
    expect(baseViewSource).toContain("onZoomChange={handlePlanZoom}");
    expect(baseViewSource).toContain('initialCenterMode="visible"');
    expect(baseViewSource).toContain("resetKey={resetKey}");
    expect(baseViewSource).toContain("readOnly={true}");
  });

  it("restores the 2D Plan sunlight controls and routes them into the shared canvas", () => {
    expect(baseViewSource).toContain("SUNLIGHT_TIME_SLIDER");
    expect(baseViewSource).toContain("SUNLIGHT_YEAR_POINTS");
    expect(baseViewSource).toContain("formatSunlightMinutes");
    expect(baseViewSource).toContain("sunlightYearPointAt");
    expect(baseViewSource).toContain("let sunlightVisible = $state(false);");
    expect(baseViewSource).toContain("let sunlightYearIndex = $state(0);");
    expect(baseViewSource).toContain("let sunlightTimeMinutes = $state(720);");
    expect(baseViewSource).toContain('aria-label="2D Plan sunlight controls"');
    expect(baseViewSource).toContain("Sunlight");
    expect(baseViewSource).toContain('type="range"');
    expect(baseViewSource).toContain("min={SUNLIGHT_TIME_SLIDER.startMinutes}");
    expect(baseViewSource).toContain("max={SUNLIGHT_TIME_SLIDER.endMinutes}");
    expect(baseViewSource).toContain("showSunlight={sunlightVisible}");
    expect(baseViewSource).toContain("sunlightYearIndex={sunlightYearIndex}");
    expect(baseViewSource).toContain("sunlightTimeMinutes={sunlightTimeMinutes}");

    expect(planCanvasSource).toContain("sunlightOverlayForPlan");
    expect(planCanvasSource).toContain("showSunlight?: boolean;");
    expect(planCanvasSource).toContain("sunlightYearIndex?: number;");
    expect(planCanvasSource).toContain("sunlightTimeMinutes?: number;");
    expect(planCanvasSource).toContain("sunlight-overlay-layer");
    expect(planCanvasSource).toContain("sunlight-ray-layer");
    expect(planCanvasSource).toContain("sunlight-sun-marker");
  });

  it("keeps sunlight controls on their own longer slider row", () => {
    expect(baseViewSource).toContain('class="base-view-toolbar-row"');
    expect(baseViewSource).toContain('class="base-sunlight-controls"');
    expect(baseViewSource.indexOf('class="base-view-toolbar-row"')).toBeLessThan(
      baseViewSource.indexOf('class="base-sunlight-controls"'),
    );
    expect(baseViewSource).toContain(
      "grid-template-columns: auto minmax(220px, 360px) minmax(220px, 360px);",
    );
    expect(baseViewSource).toContain("grid-template-columns: auto minmax(220px, 360px) minmax(86px, auto);");
    expect(baseViewSource).toContain("min-width: 220px;");
  });

  it("shows a 10 second transition control only for future designs", () => {
    expect(baseViewSource).toContain("CURRENT_SCENARIO_ID");
    expect(baseViewSource).toContain("DESIGN_TRANSITION_DURATION_MS");
    expect(baseViewSource).toContain("interpolateFurnitureLayouts");
    expect(baseViewSource).toContain("transitionProgressAt");
    expect(baseViewSource).toContain("transitionPercentLabel");
    expect(baseViewSource).toContain('scenarioId !== CURRENT_SCENARIO_ID');
    expect(baseViewSource).toContain("requestAnimationFrame");
    expect(baseViewSource).toContain("transitionBaseLayout");
    expect(baseViewSource).toContain('loadFurnitureLayout(projectId, CURRENT_SCENARIO_ID)');
    expect(baseViewSource).toContain("displayedLayout");
    expect(baseViewSource).toContain("scenarioStructuralProgress");
    expect(baseViewSource).toContain("transitionStartedAt === null ? 1 : transitionProgress");
    expect(baseViewSource).toContain("structuralTransitionProgress={scenarioStructuralProgress}");
    expect(baseViewSource).toContain("structuralTransitionScenarioId={scenarioId}");
    expect(baseViewSource).toContain("Show transition from Design 1");
    expect(baseViewSource).toContain("Transition {transitionPercentLabel(transitionProgress)}");
  });

  it("shows scenario furniture reuse guidance in future 2D plans", () => {
    expect(baseViewSource).toContain("designScenarioConceptById");
    expect(baseViewSource).toContain("scenarioConcept?.furniture_reuse");
    expect(baseViewSource).toContain("let reusePanelExpanded = $state(false);");
    expect(baseViewSource).toContain("aria-expanded={reusePanelExpanded}");
    expect(baseViewSource).toContain("onclick={() => (reusePanelExpanded = !reusePanelExpanded)}");
    expect(baseViewSource).toContain("{#if reusePanelExpanded}");
    expect(baseViewSource).toContain('class="scenario-plan-controls" aria-label="Future design review controls"');
    expect(baseViewSource).toContain("scenario-reuse-overlay");
    expect(baseViewSource).toContain("Furniture reuse plan");
    expect(baseViewSource).toContain("reuse_relocated");
    expect(baseViewSource).toContain("new_required");

    const scenarioControlsIndex = baseViewSource.indexOf("scenario-plan-controls");
    const planShellIndex = baseViewSource.indexOf("base-plan-shell");
    expect(scenarioControlsIndex).toBeGreaterThan(-1);
    expect(planShellIndex).toBeGreaterThan(-1);
    expect(scenarioControlsIndex).toBeLessThan(planShellIndex);
  });

  it("shows collapsed design sanity checks in future 2D plans", () => {
    expect(baseViewSource).toContain("buildDesignSanityChecks");
    expect(baseViewSource).toContain("let checksPanelExpanded = $state(false);");
    expect(baseViewSource).toContain("scenarioDesignChecks");
    expect(baseViewSource).toContain("Design checks");
    expect(baseViewSource).toContain("aria-expanded={checksPanelExpanded}");
    expect(baseViewSource).toContain("onclick={() => (checksPanelExpanded = !checksPanelExpanded)}");
    expect(baseViewSource).toContain("{#if checksPanelExpanded}");
    expect(baseViewSource).toContain("scenario-checks-overlay");
    expect(baseViewSource).toContain("No checks flagged");
  });

  it("lets the shared plan canvas render furniture in read-only mode", () => {
    expect(planCanvasSource).toContain("readOnly?: boolean;");
    expect(planCanvasSource).toContain('initialCenterMode?: "canvas" | "visible";');
    expect(planCanvasSource).toContain("resetKey?: number;");
    expect(planCanvasSource).toContain("centeredViewOriginAtCanvasPoint");
    expect(planCanvasSource).toContain("visibleCanvasCenterOffset");
    expect(planCanvasSource).toContain("readOnly = false");
    expect(planCanvasSource).toContain("if (readOnly) {");
    expect(planCanvasSource).toContain("{#if !readOnly && selectedObjectId === object.id}");
  });

  it("renders structural design transitions inside the shared plan canvas", () => {
    expect(planCanvasSource).toContain("structuralTransitionForScenario");
    expect(planCanvasSource).toContain("structuralTransitionProgress?: number;");
    expect(planCanvasSource).toContain("structural-transition-layer");
    expect(planCanvasSource).toContain("proposed-plan-layer");
    expect(planCanvasSource).toContain("proposed-plan-room");
    expect(planCanvasSource).toContain("proposed-plan-floor-area");
    expect(planCanvasSource).toContain("proposed-plan-opening");
    expect(planCanvasSource).toContain("proposed-plan-window");
    expect(planCanvasSource).toContain("roomLabelsForScenario");
    expect(planCanvasSource).toContain("roomLabels = $derived(roomLabelsForScenario(structuralTransitionScenarioId))");
    expect(planCanvasSource).toContain("proposedFloorFill");
    expect(planCanvasSource).toContain("plan-overlay-vinyl-planks");
    expect(planCanvasSource).toContain("plan-overlay-carpet");
    expect(planCanvasSource).toContain('stroke="#c4b49a"');
    expect(planCanvasSource).toContain('opacity="0.68"');
    expect(planCanvasSource).toContain("plan-overlay-tile");
    expect(planCanvasSource).toContain("type StructuralTransitionOpening");
    expect(planCanvasSource).toContain("function openingCutoutStroke(opening: StructuralTransitionOpening)");
    expect(planCanvasSource).toContain('opening.id === "design-2-main-lounge-deck-doors"');
    expect(planCanvasSource).toContain("stroke={openingCutoutStroke(opening)}");
    expect(planCanvasSource).toContain("stroke: none;");
    expect(planCanvasSource).toContain("stroke-dasharray: 4 4;");
    expect(planCanvasSource).toContain("stroke: transparent;");
    expect(planCanvasSource).toContain("wall-removal-mask");
    expect(planCanvasSource).toContain("future-wall");
    expect(planCanvasSource).toContain("door-marker");
    expect(planCanvasSource).toContain("retainedDoorTraces");
    expect(planCanvasSource).toContain("retained-door-trace-leaf");
    expect(planCanvasSource).toContain("retained-door-trace-arc");
    expect(planCanvasSource).toContain("openingCutoutStrokeWidth(opening)");
    expect(planCanvasSource).toContain("MAIN_ENTRY_CUTOUT_COLOUR = \"#9a6438\"");
    expect(planCanvasSource).toContain("return MAIN_ENTRY_CUTOUT_COLOUR;");
    expect(planCanvasSource).toContain("WINDOW_GUIDE_OFFSET_PX = 2");
    expect(planCanvasSource).toContain("WINDOW_GUIDE_STROKE_WIDTH_PX = 0.9");
    expect(planCanvasSource).toContain("WINDOW_CUTOUT_COLOUR = \"#fffdf8\"");
    expect(planCanvasSource).toContain("WINDOW_GUIDE_COLOUR = \"#777b80\"");
    expect(planCanvasSource).toContain(".future-wall {\n    fill: none;\n    stroke: #585b63;");
    expect(planCanvasSource).toContain(".proposed-plan-door-gap {\n    stroke: transparent;");
    expect(planCanvasSource).toContain(".retained-door-trace-leaf,\n  .retained-door-trace-arc {\n    vector-effect: none;");
    expect(planCanvasSource).not.toContain(".proposed-plan-opening-cutout {\n    stroke: #fffaf1;");
    expect(planCanvasSource).not.toContain("windowGuideOffset(opening)");
    expect(planCanvasSource).not.toContain("opening.strokeWidth / 2");
    expect(planCanvasSource).not.toContain("windowGlassStrokeWidth");
    expect(planCanvasSource).not.toContain("proposed-plan-window-glass");
    expect(planCanvasSource).not.toContain("plan-overlay-deck-boards");
    expect(planCanvasSource).not.toContain('opening.id === "design-2-day-room-east-double-glass-door"');
    expect(planCanvasSource).not.toContain("structuralTransition.planLabels");
    expect(planCanvasSource).not.toContain("proposed-plan-label-layer");
    expect(planCanvasSource).not.toContain("proposed-plan-label");
    expect(planCanvasSource).not.toContain("labelOpacity");
    expect(planCanvasSource).not.toContain(".future-wall {\n    fill: none;\n    stroke: #455057;\n    stroke-linecap: square;");
    expect(planCanvasSource).not.toContain(".proposed-plan-opening {\n    fill: none;\n    stroke-linecap: butt;\n    vector-effect: non-scaling-stroke;");
    expect(planCanvasSource).not.toContain(".wall-removal-mask {\n    stroke: #f8f1e5;\n    stroke-linecap: square;\n    vector-effect: non-scaling-stroke;");

    const floorAreaIndex = planCanvasSource.indexOf("structuralTransition.floorAreas");
    const proposedRoomIndex = planCanvasSource.indexOf("structuralTransition.proposedRooms");
    const wallMaskIndex = planCanvasSource.indexOf("structuralTransition.wallMasks");
    const futureWallIndex = planCanvasSource.indexOf("structuralTransition.futureWalls");
    const openingIndex = planCanvasSource.indexOf("structuralTransition.openings");
    const retainedDoorIndex = planCanvasSource.indexOf("retainedDoorTraces");

    expect(floorAreaIndex).toBeGreaterThan(-1);
    expect(proposedRoomIndex).toBeGreaterThan(-1);
    expect(wallMaskIndex).toBeGreaterThan(-1);
    expect(futureWallIndex).toBeGreaterThan(-1);
    expect(openingIndex).toBeGreaterThan(-1);
    expect(wallMaskIndex).toBeLessThan(floorAreaIndex);
    expect(proposedRoomIndex).toBeLessThan(floorAreaIndex);
    expect(floorAreaIndex).toBeLessThan(futureWallIndex);
    expect(futureWallIndex).toBeLessThan(openingIndex);
    expect(openingIndex).toBeLessThan(retainedDoorIndex);
  });

  it("keeps the tuned SVG reference plan as the primary 2D rendering", () => {
    expect(planCanvasSource).toContain("plan-reference-underlay");
    expect(planCanvasSource).toContain('href={backgroundAssetPath}');
    expect(planCanvasSource).toContain('width="1600"');
    expect(planCanvasSource).toContain('height="900"');
    expect(planCanvasSource).not.toContain("planVectorLayers");
    expect(planCanvasSource).not.toContain("currentPlanVectorModel");
    expect(planCanvasSource).not.toContain("planVectorModelForScenario");
  });
});
