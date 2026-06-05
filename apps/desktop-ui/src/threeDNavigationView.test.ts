import { describe, expect, it } from "vitest";
import appSource from "./App.svelte?raw";
import viewSource from "./ThreeDNavigationView.svelte?raw";

describe("native 3D navigation view wiring", () => {
  it("routes three_d_navigation to the native Svelte view", () => {
    expect(appSource).toContain('import ThreeDNavigationView from "./ThreeDNavigationView.svelte";');
    expect(appSource).toContain('selectedView.mode === "three_d_navigation"');
    expect(appSource).toContain("<ThreeDNavigationView projectId={project.id} scenarioId={selectedScenario.id} />");
    expect(appSource).toContain("selectedViewDisplayPath");
    expect(appSource).toContain("Native renderer");
  });

  it("loads design review data for model and saved furniture", () => {
    expect(viewSource).toContain("loadDesignReviewData");
    expect(viewSource).toContain("scenarioId: string;");
    expect(viewSource).toContain("loadDesignReviewData(projectId, scenarioId)");
    expect(viewSource).toContain("buildThreeDSceneConfig");
    expect(viewSource).toContain("Furniture layout");
  });

  it("owns the Three.js renderer lifecycle and native navigation state", () => {
    expect(viewSource).toContain('import * as THREE from "three";');
    expect(viewSource).toContain("new THREE.WebGLRenderer");
    expect(viewSource).toContain("requestAnimationFrame");
    expect(viewSource).toContain("cleanupThreeDScene");
    expect(viewSource).toContain("keysPressed");
    expect(viewSource).toContain("resetCamera");
  });

  it("uses double-sided materials so floor and site planes are visible from overview cameras", () => {
    expect(viewSource).toContain("side: THREE.DoubleSide");
    expect(viewSource).not.toContain("THREE.FrontSide");
  });

  it("renders the raised house base as masonry skirting instead of exposed pile cylinders", () => {
    expect(viewSource).toContain("foundation.skirtSegments");
    expect(viewSource).toContain('materialFor("foundationMasonry"');
    expect(viewSource).not.toContain("config.foundation.piles.forEach");
    expect(viewSource).not.toContain("foundation:pile");
    expect(viewSource).not.toContain("CylinderGeometry(0.045");
  });

  it("renders explicit timber step treads for the sunroom and deck edges", () => {
    expect(viewSource).toContain("config.steps.forEach");
    expect(viewSource).toContain("addDeckStep");
    expect(viewSource).toContain("step:");
  });

  it("renders deck side fascia and exterior-facing foundation skirting", () => {
    expect(viewSource).toContain("config.deckEdges.forEach");
    expect(viewSource).toContain("addDeckEdge");
    expect(viewSource).toContain("exteriorFaceOffsetM");
    expect(viewSource).toContain("offsetSegmentForExteriorFace");
  });

  it("turns material pattern metadata into procedural Three.js textures", () => {
    expect(viewSource).toContain("textureForPattern");
    expect(viewSource).toContain("new THREE.CanvasTexture");
    expect(viewSource).toContain("deck_boards");
    expect(viewSource).toContain("masonry_blocks");
    expect(viewSource).toContain("reusableTextures");
  });

  it("does not apply repeating procedural textures to large lawn and concrete site surfaces", () => {
    expect(viewSource).toContain("shouldTextureSiteElement");
    expect(viewSource).toContain('siteElement.material === "deckTimber"');
    expect(viewSource).toContain("usePattern");
  });

  it("renders one stable base ground plane below site features to avoid low-angle z-fighting", () => {
    expect(viewSource).toContain("addStableGroundPlane");
    expect(viewSource).toContain("config.groundPlane");
    expect(viewSource).toContain("renderOrder = -10");
  });

  it("keeps arrow keys mirrored to WASD movement but raises the walking speed", () => {
    expect(viewSource).toContain('keysPressed.has("arrowup") || keysPressed.has("w")');
    expect(viewSource).toContain('keysPressed.has("arrowdown") || keysPressed.has("s")');
    expect(viewSource).toContain('keysPressed.has("arrowright") || keysPressed.has("d")');
    expect(viewSource).toContain('keysPressed.has("arrowleft") || keysPressed.has("a")');
    expect(viewSource).toContain("keysPressed.has(\"shift\") ? 7.0 : 3.6");
  });

  it("uses natural mouse-look yaw where moving the mouse left looks left", () => {
    expect(viewSource).toContain("cameraYaw += dx * 0.004");
    expect(viewSource).toContain("cameraPitch = THREE.MathUtils.clamp(cameraPitch - dy * 0.003");
    expect(viewSource).toContain('keysPressed.has("j")');
    expect(viewSource).toContain('keysPressed.has("l")');
  });

  it("adds white frames, mullions, and handles so openings read as windows and doors", () => {
    expect(viewSource).toContain("addOpeningFrame");
    expect(viewSource).toContain("addOpeningHandle");
    expect(viewSource).toContain("addOpeningWallInfill");
    expect(viewSource).toContain("openingDimensionsForType");
    expect(viewSource).toContain('materialFor("frameWhite"');
    expect(viewSource).toContain('materialFor("doorHandle"');
  });

  it("renders openings from measured wall anchors and caps exterior wall endpoints square", () => {
    expect(viewSource).toContain("for (const [index, anchor] of opening.anchors.entries())");
    expect(viewSource).toContain("openingPanelSpecFromAnchor");
    expect(viewSource).toContain("addExteriorWallEndpointCaps");
    expect(viewSource).toContain("wall.class.includes(\"exterior\")");
  });

  it("keeps opening infill at wall thickness and renders doors open", () => {
    expect(viewSource).toContain("depthM: Math.max(anchor.wallThicknessM, panelThicknessM)");
    expect(viewSource).toContain("const infillDepth = panel.depthM;");
    expect(viewSource).toContain("const frameDepth = panel.depthM;");
    expect(viewSource).toContain("addOpenDoorLeaf");
    expect(viewSource).toContain("isDoorLikeOpening");
  });

  it("keeps glazing visibly transparent in the 3D renderer", () => {
    expect(viewSource).toContain("transparent: preset?.transparent ?? false");
    expect(viewSource).toContain("opacity: preset?.opacity ?? 1");
    expect(viewSource).toContain("depthWrite: !(preset?.transparent ?? false)");
    expect(viewSource).toContain("renderWallSegmentsWithOpeningCuts");
    expect(viewSource).toContain("wallOpeningAnchorsForWall");
    expect(viewSource).toContain("addWindowGlass");
    expect(viewSource).toContain("!isPlainOpening(opening.type)");
  });

  it("distinguishes plain openings, hinged doors, double doors, and sliding glazed doors", () => {
    expect(viewSource).toContain("isSlidingDoorOpening");
    expect(viewSource).toContain("isGlazedSlidingDoorOpening");
    expect(viewSource).toContain("isDoubleDoorOpening");
    expect(viewSource).toContain("isPlainOpening");
    expect(viewSource).toContain("addSlidingDoorPanels");
    expect(viewSource).toContain("addSolidSlidingDoorPanel");
    expect(viewSource).toContain("addDoubleDoorLeaves");
    expect(viewSource).toContain("addOpeningWallInfill(targetScene, panel, floorElevationM");
  });

  it("renders interior sliding doors as solid panels instead of transparent glass", () => {
    expect(viewSource).toContain('opening.type === "slider"');
    expect(viewSource).toContain("addSolidSlidingDoorPanel(targetScene, visiblePanel");
    expect(viewSource).toContain('materialFor("paintedWall"');
  });

  it("keeps window cuts tight and fills side reveals beside frames", () => {
    expect(viewSource).toContain("return [start, end];");
    expect(viewSource).toContain("addWindowSideWallReturns");
    expect(viewSource).toContain("const returnWidth = 0.055;");
  });

  it("renders exterior double-door groups as glazed side-hinged leaves without a fixed centre column", () => {
    expect(viewSource).toContain("addGlazedDoubleDoorLeaves");
    expect(viewSource).toContain('const doorGlassMaterial = materialFor("glazing");');
    expect(viewSource).toContain("includeCentreMullion = true");
    expect(viewSource).toContain("addOpeningFrame(targetScene, visiblePanel, `opening:${opening.id}:${index}:frame`, false)");
    expect(viewSource).toContain("const hingeOffset = index === 0 ? -panel.widthM / 2 : panel.widthM / 2;");
    expect(viewSource).toContain("const leafGroup = new THREE.Group();");
    expect(viewSource).toContain("leafGroup.position.set(hinge.x, panel.position.y, hinge.z);");
    expect(viewSource).toContain("leafGroup.rotation.y = panel.rotationY + swingDirection * (index === 0 ? openAngleRad : -openAngleRad);");
    expect(viewSource).toContain("targetScene.add(leafGroup);");
    expect(viewSource).not.toContain("openingPositionFromLeafRotation");
  });

  it("flips double-door leaf swing when the model marks doors as outward to the front path", () => {
    expect(viewSource).toContain("opening.swing");
    expect(viewSource).toContain("swingDirectionForOpening");
    expect(viewSource).toContain('opening.swing === "outward_to_front_path" ? -1 : 1');
    expect(viewSource).toContain("leafGroup.rotation.y = panel.rotationY + swingDirection * (index === 0 ? openAngleRad : -openAngleRad);");
  });

  it("renders sunroom wraparound glazing as floor-to-ceiling panels offset to the exterior face", () => {
    expect(viewSource).toContain("openingDimensionsForOpening");
    expect(viewSource).toContain('opening.id === "sunroom_wraparound_glazing"');
    expect(viewSource).toContain("return { heightM: 2.18, sillHeightM: 0.02 };");
    expect(viewSource).toContain("offsetSunroomGlazingPanelToExterior");
    expect(viewSource).toContain("const exteriorOffsetM = 0.09;");
  });

  it("renders sunroom glazing with slim curtain-wall frames instead of generic wall returns", () => {
    expect(viewSource).toContain("isSunroomWraparoundGlazing");
    expect(viewSource).toContain("addSunroomGlazingAssembly");
    expect(viewSource).toContain("const frameWidth = 0.04;");
    expect(viewSource).toContain("if (isSunroomWraparoundGlazing(opening))");
    expect(viewSource).toContain("continue;");
  });

  it("keeps the master-to-sunroom former-external window as a normal window profile", () => {
    expect(viewSource).toContain("opening.windowContext");
    expect(viewSource).toContain('opening.windowContext === "former_external"');
    expect(viewSource).toContain("return { heightM: 1.18, sillHeightM: 0.78 };");
    expect(viewSource).toContain("addFormerExternalWindowAssembly");
    expect(viewSource).toContain("offsetFormerExternalWindowPanelToRoom(panel, opening.room)");
    expect(viewSource).toContain("offsetFormerExternalWindowPanelToSunroom");
    expect(viewSource).toContain('const sunroom = sceneConfig?.rooms.find((item) => item.id === "sunroom");');
    expect(viewSource).toContain('if (opening.windowContext === "former_external" && !isDoorLikeOpening(opening.type) && !isPlainOpening(opening.type))');
  });

  it("renders sliding doors on the built-in master bedroom wardrobe bay", () => {
    expect(viewSource).toContain("addBuiltInWardrobeDoors");
    expect(viewSource).toContain('room.id === "master_bedroom_wardrobe"');
    expect(viewSource).toContain("const doorSets = 2;");
    expect(viewSource).toContain('`wardrobe-door:${room.id}:${index}`');
  });

  it("renders high-impact furniture as grouped assemblies instead of single blocks", () => {
    expect(viewSource).toContain("createFurnitureGroup");
    expect(viewSource).toContain("addFurniturePart");
    expect(viewSource).toContain("addBedFurniture");
    expect(viewSource).toContain("addLShapedSofaFurniture");
    expect(viewSource).toContain("addChairFurniture");
    expect(viewSource).toContain("addTableFurniture");
    expect(viewSource).toContain("addDeskFurniture");
    expect(viewSource).toContain("addTvFurniture");
    expect(viewSource).toContain("addPianoFurniture");
    expect(viewSource).toContain("addFireplaceFurniture");
    expect(viewSource).toContain("if (addDetailedFurnitureObject(targetScene, object, floorElevationM))");
  });

  it("renders storage, appliance, bathroom, stool, and wardrobe objects with type-specific detail", () => {
    expect(viewSource).toContain("addStorageFurniture");
    expect(viewSource).toContain("addBookcaseFurniture");
    expect(viewSource).toContain('["front", -object.depthM * 0.32]');
    expect(viewSource).toContain('["back", object.depthM * 0.32]');
    expect(viewSource).toContain("book-spine-${face}");
    expect(viewSource).toContain("vertical-divider");
    expect(viewSource).toContain("addApplianceFurniture");
    expect(viewSource).toContain("addSinkFurniture");
    expect(viewSource).toContain("addBathFurniture");
    expect(viewSource).toContain("addShowerFurniture");
    expect(viewSource).toContain("addToiletFurniture");
    expect(viewSource).toContain("addStoolFurniture");
    expect(viewSource).toContain("addWardrobeDoorFurniture");
    expect(viewSource).toContain("addPartitionWallFurniture");
    expect(viewSource).toContain("cabinetVisualHeight");
    expect(viewSource).toContain("addFurnitureCylinder");
  });

  it("keeps large structural openings clear and wall-mounts TVs placed over fireplaces", () => {
    expect(viewSource).toContain('openingType === "large_opening"');
    expect(viewSource).toContain("if (isPlainOpening(opening.type)) {");
    expect(viewSource).toContain("continue;");
    expect(viewSource).toContain("isTvAboveFireplace");
    expect(viewSource).toContain("addWallMountedTvFurniture");
    expect(viewSource).toContain("return addWallMountedTvFurniture(targetScene, object, floorElevationM);");
  });

  it("lifts TVs onto configured support surfaces and refreshes the saved layout when 3D mounts", () => {
    expect(viewSource).toContain("supportSurfaceHeightM");
    expect(viewSource).toContain("group.position.y += object.supportSurfaceHeightM");
    expect(viewSource).toContain("$effect(() => {");
    expect(viewSource).toContain("void refreshThreeDData();");
  });

  it("only cuts a wall segment when an opening anchor overlaps that same segment", () => {
    expect(viewSource).toContain("anchorOverlapsWallSegment");
    expect(viewSource).toContain("const anchors = wallOpeningAnchorsForWall(config, wall).filter((anchor) => anchorOverlapsWallSegment(anchor, segment));");
  });
});
