<script lang="ts">
  import { onDestroy, tick } from "svelte";
  import * as THREE from "three";
  import { buildThreeDSceneConfig } from "./lib/threeD/sceneConfig";
  import { loadDesignReviewData } from "./lib/homeDesignCommands";
  import type { DesignReviewData } from "./types";
  import type {
    ThreeDDeckEdge,
    ThreeDFurnitureItem,
    ThreeDGroundPlane,
    ThreeDMaterialPreset,
    ThreeDSceneConfig,
    ThreeDStepTread,
    ThreeDSiteElement,
  } from "./lib/threeD/sceneConfig";
  import { sceneGeometryBoundsList, type SceneGeometry, type ScenePoint } from "./lib/threeD/geometry";
  import {
    HORIZONTAL_PLANE_ROTATION_X,
  } from "./lib/threeD/renderGeometry";

  type Props = {
    projectId: string;
    scenarioId: string;
  };

  let { projectId, scenarioId }: Props = $props();

  let reviewData = $state<DesignReviewData | null>(null);
  let sceneConfig = $state<ThreeDSceneConfig | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let refreshedAt = $state<string | null>(null);
  let stageElement = $state<HTMLButtonElement | null>(null);
  let selectedPhotoViewpointId = $state("default");

  let renderer: THREE.WebGLRenderer | null = null;
  let scene: THREE.Scene | null = null;
  let camera: THREE.PerspectiveCamera | null = null;
  let clock: THREE.Clock | null = null;
  let resizeObserver: ResizeObserver | null = null;
  let animationFrameId: number | null = null;
  let cameraYaw = -0.9;
  let cameraPitch = -0.1;
  let dragging = false;
  let lastPointer = { x: 0, y: 0 };
  let latestRefreshRequest = 0;

  const keysPressed = new Set<string>();
  const reusableMaterials = new Map<string, THREE.Material>();
  const reusableTextures = new Map<string, THREE.Texture>();
  const NAVIGATION_KEYS = new Set([
    "w",
    "a",
    "s",
    "d",
    "q",
    "e",
    "i",
    "j",
    "k",
    "l",
    "arrowup",
    "arrowdown",
    "arrowleft",
    "arrowright",
  ]);
  type MaterialOptions = {
    usePattern?: boolean;
  };
  type OpeningPanelRenderSpec = {
    widthM: number;
    heightM: number;
    depthM: number;
    sillHeightM: number;
    position: {
      x: number;
      y: number;
      z: number;
    };
    rotationY: number;
  };
  type FurniturePartOptions = {
    rotationDeg?: number;
  };

  function toErrorMessage(reason: unknown): string {
    return reason instanceof Error ? reason.message : String(reason);
  }

  async function refreshThreeDData() {
    const refreshRequest = latestRefreshRequest + 1;
    latestRefreshRequest = refreshRequest;
    loading = true;
    error = null;
    try {
      const data = await loadDesignReviewData(projectId, scenarioId);
      if (refreshRequest !== latestRefreshRequest) {
        return;
      }
      reviewData = data;
      sceneConfig = buildThreeDSceneConfig(data);
      refreshedAt = new Intl.DateTimeFormat(undefined, {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }).format(new Date());
      await tick();
      initialiseThreeDScene();
    } catch (reason: unknown) {
      if (refreshRequest === latestRefreshRequest) {
        error = toErrorMessage(reason);
      }
    } finally {
      if (refreshRequest === latestRefreshRequest) {
        loading = false;
      }
    }
  }

  function isEditableTarget(target: EventTarget | null): boolean {
    return target instanceof HTMLElement
      && Boolean(target.closest("input, textarea, select, [contenteditable='true']"));
  }

  function isNavigationKey(event: KeyboardEvent): boolean {
    return NAVIGATION_KEYS.has(event.key.toLowerCase());
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (isEditableTarget(event.target) || !isNavigationKey(event)) {
      return;
    }
    event.preventDefault();
    keysPressed.add(event.key.toLowerCase());
  }

  function handleKeyUp(event: KeyboardEvent) {
    keysPressed.delete(event.key.toLowerCase());
  }

  function handlePointerDown(event: PointerEvent) {
    if (!stageElement) {
      return;
    }
    dragging = true;
    lastPointer = { x: event.clientX, y: event.clientY };
    stageElement.setPointerCapture(event.pointerId);
    stageElement.focus();
  }

  function handlePointerMove(event: PointerEvent) {
    if (!dragging) {
      return;
    }
    const dx = event.clientX - lastPointer.x;
    const dy = event.clientY - lastPointer.y;
    lastPointer = { x: event.clientX, y: event.clientY };
    cameraYaw += dx * 0.004;
    cameraPitch = THREE.MathUtils.clamp(cameraPitch - dy * 0.003, -1.1, 0.8);
    updateCameraLook();
  }

  function handlePointerUp(event: PointerEvent) {
    dragging = false;
    stageElement?.releasePointerCapture(event.pointerId);
  }

  function handleWheel(event: WheelEvent) {
    if (!camera) {
      return;
    }
    event.preventDefault();
    camera.position.y = THREE.MathUtils.clamp(camera.position.y + Math.sign(event.deltaY) * 0.16, 0.55, 3.4);
    updateCameraLook();
  }

  function textureForPattern(pattern: string, baseColor: string): THREE.Texture {
    const cacheKey = `${pattern}:${baseColor}`;
    const cached = reusableTextures.get(cacheKey);
    if (cached) {
      return cached;
    }

    const canvas = document.createElement("canvas");
    canvas.width = 128;
    canvas.height = 128;
    const context = canvas.getContext("2d");
    if (context) {
      context.fillStyle = baseColor;
      context.fillRect(0, 0, canvas.width, canvas.height);

      if (pattern === "deck_boards" || pattern === "vinyl_planks") {
        context.strokeStyle = pattern === "deck_boards" ? "rgba(72, 45, 26, 0.42)" : "rgba(72, 55, 42, 0.28)";
        context.lineWidth = pattern === "deck_boards" ? 2 : 1;
        for (let y = 10; y < canvas.height; y += pattern === "deck_boards" ? 14 : 18) {
          context.beginPath();
          context.moveTo(0, y);
          context.lineTo(canvas.width, y + 1);
          context.stroke();
        }
        context.strokeStyle = pattern === "deck_boards" ? "rgba(179, 126, 76, 0.24)" : "rgba(255, 245, 224, 0.18)";
        for (let x = 8; x < canvas.width; x += 24) {
          context.beginPath();
          context.moveTo(x, 0);
          context.lineTo(x + 10, canvas.height);
          context.stroke();
        }
      } else if (pattern === "masonry_blocks" || pattern === "tile_grid") {
        const rowHeight = pattern === "masonry_blocks" ? 24 : 32;
        const columnWidth = pattern === "masonry_blocks" ? 42 : 32;
        context.strokeStyle = pattern === "masonry_blocks" ? "rgba(95, 88, 76, 0.38)" : "rgba(80, 95, 98, 0.32)";
        context.lineWidth = pattern === "masonry_blocks" ? 2 : 1;
        for (let y = rowHeight; y < canvas.height; y += rowHeight) {
          context.beginPath();
          context.moveTo(0, y);
          context.lineTo(canvas.width, y);
          context.stroke();
        }
        for (let y = 0; y < canvas.height; y += rowHeight) {
          const offset = pattern === "masonry_blocks" && Math.floor(y / rowHeight) % 2 === 1 ? columnWidth / 2 : 0;
          for (let x = offset; x < canvas.width; x += columnWidth) {
            context.beginPath();
            context.moveTo(x, y);
            context.lineTo(x, Math.min(canvas.height, y + rowHeight));
            context.stroke();
          }
        }
      } else if (pattern === "grass_noise" || pattern === "carpet_noise" || pattern === "concrete_mottle" || pattern === "fabric_noise") {
        for (let index = 0; index < 180; index += 1) {
          const x = (index * 37) % canvas.width;
          const y = (index * 53) % canvas.height;
          const alpha = pattern === "concrete_mottle" ? 0.14 : 0.18;
          context.fillStyle = index % 2 === 0
            ? `rgba(255, 255, 255, ${alpha})`
            : `rgba(35, 45, 32, ${alpha})`;
          context.fillRect(x, y, pattern === "grass_noise" ? 2 : 3, pattern === "grass_noise" ? 7 : 3);
        }
      }
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(pattern === "masonry_blocks" ? 2 : 3, pattern === "deck_boards" ? 5 : 3);
    texture.anisotropy = 4;
    reusableTextures.set(cacheKey, texture);
    return texture;
  }

  function materialFor(name: string, fallbackColor = "#d8d2c5", options: MaterialOptions = {}): THREE.Material {
    const usePattern = options.usePattern ?? true;
    const cacheKey = `${name}:${fallbackColor}:${usePattern ? "pattern" : "flat"}`;
    const cached = reusableMaterials.get(cacheKey);
    if (cached) {
      return cached;
    }
    const preset: ThreeDMaterialPreset | undefined = sceneConfig?.materials[name];
    const texture = usePattern && preset?.pattern ? textureForPattern(preset.pattern, preset.baseColor) : null;
    const material = new THREE.MeshStandardMaterial({
      color: texture ? "#ffffff" : preset?.baseColor ?? fallbackColor,
      roughness: preset?.roughness ?? 0.72,
      transparent: preset?.transparent ?? false,
      opacity: preset?.opacity ?? 1,
      depthWrite: !(preset?.transparent ?? false),
      map: texture ?? undefined,
      side: THREE.DoubleSide,
    });
    reusableMaterials.set(cacheKey, material);
    return material;
  }

  function shouldTextureSiteElement(siteElement: ThreeDSiteElement): boolean {
    return siteElement.material === "deckTimber";
  }

  function objectMaterial(object: ThreeDFurnitureItem): THREE.Material {
    if (object.colour) {
      return materialFor(`object:${object.id}`, object.colour);
    }
    return materialFor(object.material);
  }

  function shapeFromPoints(points: ScenePoint[]): THREE.Shape | null {
    if (points.length < 3) {
      return null;
    }
    const shape = new THREE.Shape();
    shape.moveTo(points[0].x, points[0].z);
    points.slice(1).forEach((point) => shape.lineTo(point.x, point.z));
    shape.closePath();
    return shape;
  }

  function addPlaneGeometry(
    targetScene: THREE.Scene,
    geometry: SceneGeometry,
    material: THREE.Material,
    elevationM: number,
    namePrefix: string,
  ) {
    if (geometry.type === "rect") {
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(geometry.width, geometry.depth), material);
      mesh.rotation.x = HORIZONTAL_PLANE_ROTATION_X;
      mesh.position.set(geometry.x + geometry.width / 2, elevationM, geometry.z + geometry.depth / 2);
      mesh.receiveShadow = true;
      mesh.name = `${namePrefix}:rect`;
      targetScene.add(mesh);
      return;
    }

    const polygons = geometry.type === "polygon" ? [geometry.points] : geometry.polygons;
    polygons.forEach((points, index) => {
      const shape = shapeFromPoints(points);
      if (!shape) {
        return;
      }
      const mesh = new THREE.Mesh(new THREE.ShapeGeometry(shape), material);
      mesh.rotation.x = HORIZONTAL_PLANE_ROTATION_X;
      mesh.position.y = elevationM;
      mesh.receiveShadow = true;
      mesh.name = `${namePrefix}:polygon:${index}`;
      targetScene.add(mesh);
    });
  }

  function addStableGroundPlane(targetScene: THREE.Scene, groundPlane: ThreeDGroundPlane) {
    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(groundPlane.widthM, groundPlane.depthM),
      materialFor(groundPlane.material, "#78a85f", { usePattern: false }),
    );
    mesh.rotation.x = HORIZONTAL_PLANE_ROTATION_X;
    mesh.position.set(groundPlane.xM, groundPlane.elevationM, groundPlane.zM);
    mesh.receiveShadow = true;
    mesh.renderOrder = -10;
    mesh.name = "site:stable-ground-plane";
    targetScene.add(mesh);
  }

  function addBox(
    targetScene: THREE.Scene,
    widthM: number,
    heightM: number,
    depthM: number,
    position: { x: number; y: number; z: number },
    material: THREE.Material,
    rotationDeg = 0,
    name = "box",
  ): THREE.Mesh {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(widthM, heightM, depthM), material);
    mesh.position.set(position.x, position.y, position.z);
    mesh.rotation.y = THREE.MathUtils.degToRad(-rotationDeg);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.name = name;
    targetScene.add(mesh);
    return mesh;
  }

  function addWallSegment(
    targetScene: THREE.Scene,
    segment: { x1: number; z1: number; x2: number; z2: number },
    heightM: number,
    thicknessM: number,
    material: THREE.Material,
    floorElevationM: number,
    name: string,
  ) {
    const dx = segment.x2 - segment.x1;
    const dz = segment.z2 - segment.z1;
    const length = Math.hypot(dx, dz);
    if (length <= 0.01) {
      return;
    }
    const mesh = addBox(
      targetScene,
      length,
      heightM,
      thicknessM,
      {
        x: (segment.x1 + segment.x2) / 2,
        y: floorElevationM + heightM / 2,
        z: (segment.z1 + segment.z2) / 2,
      },
      material,
      0,
      name,
    );
    mesh.rotation.y = -Math.atan2(dz, dx);
  }

  function subtractOpeningCuts(cuts: Array<[number, number]>): Array<[number, number]> {
    let intervals: Array<[number, number]> = [[0, 1]];
    cuts
      .map(([start, end]): [number, number] => [Math.max(0, Math.min(start, end)), Math.min(1, Math.max(start, end))])
      .sort((left, right) => left[0] - right[0])
      .forEach(([cutStart, cutEnd]) => {
        intervals = intervals.flatMap(([start, end]) => {
          if (cutEnd <= start || cutStart >= end) {
            return [[start, end]];
          }
          return [
            [start, Math.max(start, cutStart)] as [number, number],
            [Math.min(end, cutEnd), end] as [number, number],
          ].filter(([pieceStart, pieceEnd]) => pieceEnd - pieceStart > 0.015);
        });
      });
    return intervals;
  }

  function pointParameterOnSegment(
    point: { x: number; z: number },
    segment: { x1: number; z1: number; x2: number; z2: number },
  ): number {
    const dx = segment.x2 - segment.x1;
    const dz = segment.z2 - segment.z1;
    const lengthSquared = dx * dx + dz * dz;
    if (lengthSquared <= 0.000001) {
      return 0;
    }
    return ((point.x - segment.x1) * dx + (point.z - segment.z1) * dz) / lengthSquared;
  }

  function segmentAtInterval(
    segment: { x1: number; z1: number; x2: number; z2: number },
    start: number,
    end: number,
  ) {
    return {
      x1: segment.x1 + (segment.x2 - segment.x1) * start,
      z1: segment.z1 + (segment.z2 - segment.z1) * start,
      x2: segment.x1 + (segment.x2 - segment.x1) * end,
      z2: segment.z1 + (segment.z2 - segment.z1) * end,
    };
  }

  function wallOpeningAnchorsForWall(
    config: ThreeDSceneConfig,
    wall: ThreeDSceneConfig["walls"][number],
  ) {
    return config.openings.flatMap((opening) => opening.anchors.filter((anchor) => anchor.sourceWallId === wall.id));
  }

  function distancePointToSegment(
    point: { x: number; z: number },
    segment: { x1: number; z1: number; x2: number; z2: number },
  ): number {
    const parameter = THREE.MathUtils.clamp(pointParameterOnSegment(point, segment), 0, 1);
    const closest = {
      x: segment.x1 + (segment.x2 - segment.x1) * parameter,
      z: segment.z1 + (segment.z2 - segment.z1) * parameter,
    };
    return Math.hypot(point.x - closest.x, point.z - closest.z);
  }

  function anchorOverlapsWallSegment(
    anchor: ThreeDSceneConfig["openings"][number]["anchors"][number],
    segment: { x1: number; z1: number; x2: number; z2: number },
  ): boolean {
    const start = pointParameterOnSegment({ x: anchor.segment.x1, z: anchor.segment.z1 }, segment);
    const end = pointParameterOnSegment({ x: anchor.segment.x2, z: anchor.segment.z2 }, segment);
    const overlapStart = Math.max(0, Math.min(start, end));
    const overlapEnd = Math.min(1, Math.max(start, end));
    return overlapEnd > overlapStart
      && distancePointToSegment(anchor.centre, segment) <= Math.max(anchor.wallThicknessM, 0.12);
  }

  function renderWallSegmentsWithOpeningCuts(
    targetScene: THREE.Scene,
    wall: ThreeDSceneConfig["walls"][number],
    material: THREE.Material,
    floorElevationM: number,
    config: ThreeDSceneConfig,
  ) {
    wall.segments.forEach((segment, index) => {
      const anchors = wallOpeningAnchorsForWall(config, wall).filter((anchor) => anchorOverlapsWallSegment(anchor, segment));
      const cuts = anchors.map((anchor): [number, number] => {
        const start = pointParameterOnSegment({ x: anchor.segment.x1, z: anchor.segment.z1 }, segment);
        const end = pointParameterOnSegment({ x: anchor.segment.x2, z: anchor.segment.z2 }, segment);
        return [start, end];
      });
      subtractOpeningCuts(cuts).forEach(([start, end], pieceIndex) => {
        addWallSegment(
          targetScene,
          segmentAtInterval(segment, start, end),
          wall.heightM,
          wall.thicknessM,
          material,
          floorElevationM,
          `wall:${wall.id}:${index}:${pieceIndex}`,
        );
      });
    });
  }

  function addExteriorWallEndpointCaps(
    targetScene: THREE.Scene,
    wall: ThreeDSceneConfig["walls"][number],
    material: THREE.Material,
    floorElevationM: number,
  ) {
    if (!wall.class.includes("exterior")) {
      return;
    }
    wall.segments.forEach((segment, index) => {
      [
        { x: segment.x1, z: segment.z1, name: "start" },
        { x: segment.x2, z: segment.z2, name: "end" },
      ].forEach((point) => {
        addBox(
          targetScene,
          wall.thicknessM,
          wall.heightM,
          wall.thicknessM,
          {
            x: point.x,
            y: floorElevationM + wall.heightM / 2,
            z: point.z,
          },
          material,
          0,
          `wall-cap:${wall.id}:${index}:${point.name}`,
        );
      });
    });
  }

  function addSegmentBox(
    targetScene: THREE.Scene,
    segment: { x1: number; z1: number; x2: number; z2: number },
    heightM: number,
    thicknessM: number,
    centreY: number,
    material: THREE.Material,
    name: string,
  ) {
    const dx = segment.x2 - segment.x1;
    const dz = segment.z2 - segment.z1;
    const length = Math.hypot(dx, dz);
    if (length <= 0.01) {
      return;
    }
    const mesh = addBox(
      targetScene,
      length,
      heightM,
      thicknessM,
      {
        x: (segment.x1 + segment.x2) / 2,
        y: centreY,
        z: (segment.z1 + segment.z2) / 2,
      },
      material,
      0,
      name,
    );
    mesh.rotation.y = -Math.atan2(dz, dx);
  }

  function addDeckEdge(targetScene: THREE.Scene, edge: ThreeDDeckEdge) {
    addSegmentBox(
      targetScene,
      edge,
      edge.heightM,
      edge.thicknessM,
      edge.topElevationM - edge.heightM / 2,
      materialFor(edge.material),
      `deck-edge:${edge.id}`,
    );
  }

  function addSiteElement(targetScene: THREE.Scene, siteElement: ThreeDSiteElement) {
    addPlaneGeometry(
      targetScene,
      siteElement.geometry,
      materialFor(siteElement.material, "#d8d2c5", { usePattern: shouldTextureSiteElement(siteElement) }),
      siteElement.elevationM,
      `site:${siteElement.id}`,
    );
  }

  function addDeckStep(targetScene: THREE.Scene, step: ThreeDStepTread) {
    addBox(
      targetScene,
      step.widthM,
      step.heightM,
      step.depthM,
      {
        x: step.xM,
        y: step.elevationM + step.heightM / 2,
        z: step.zM,
      },
      materialFor(step.material),
      step.rotationDeg,
      `step:${step.id}`,
    );
  }

  function addOpeningObject(
    targetScene: THREE.Scene,
    opening: ThreeDSceneConfig["openings"][number],
    floorElevationM: number,
  ) {
    const material = materialFor(opening.material);
    const dimensions = openingDimensionsForOpening(opening);
    for (const [index, anchor] of opening.anchors.entries()) {
      let panel = openingPanelSpecFromAnchor(
        anchor,
        floorElevationM,
        dimensions.heightM,
        0.035,
        dimensions.sillHeightM,
      );
      if (isSunroomWraparoundGlazing(opening)) {
        panel = offsetSunroomGlazingPanelToExterior(panel, opening);
        addSunroomGlazingAssembly(targetScene, panel, `opening:${opening.id}:${index}:sunroom-glazing`);
        continue;
      }
      if (isPlainOpening(opening.type)) {
        continue;
      }
      addOpeningWallInfill(targetScene, panel, floorElevationM, `opening:${opening.id}:${index}:infill`);
      if (opening.windowContext === "former_external" && !isDoorLikeOpening(opening.type) && !isPlainOpening(opening.type)) {
        addFormerExternalWindowAssembly(targetScene, opening, panel, material, floorElevationM, `opening:${opening.id}:${index}:former-external`);
        continue;
      }
      const visiblePanel = panel;
      if (isSlidingDoorOpening(opening.type)) {
        if (isGlazedSlidingDoorOpening(opening)) {
          addSlidingDoorPanels(targetScene, visiblePanel, `opening:${opening.id}:${index}:sliding`);
        } else {
          addSolidSlidingDoorPanel(targetScene, visiblePanel, `opening:${opening.id}:${index}:solid-sliding`);
        }
      } else if (isClosedGlazedEntryDoor(opening)) {
        addClosedGlazedEntryDoor(targetScene, visiblePanel, `opening:${opening.id}:${index}:entry-door`);
      } else if (isDoubleDoorOpening(opening.type)) {
        addDoubleDoorLeaves(targetScene, visiblePanel, opening, `opening:${opening.id}:${index}:double-door`);
      } else if (!isDoorLikeOpening(opening.type) && !isPlainOpening(opening.type)) {
        addWindowGlass(targetScene, visiblePanel, material, `opening:${opening.id}:${index}`);
      }
      if (shouldRenderOpeningFrame(opening)) {
        if (isDoubleDoorOpening(opening.type)) {
          addOpeningFrame(targetScene, visiblePanel, `opening:${opening.id}:${index}:frame`, false, "door");
        } else if (isDoorLikeOpening(opening.type)) {
          addOpeningFrame(targetScene, visiblePanel, `opening:${opening.id}:${index}:frame`, false, "door");
        } else {
          addOpeningFrame(targetScene, visiblePanel, `opening:${opening.id}:${index}:frame`);
        }
      }
      if (isDoorLikeOpening(opening.type) && !isSlidingDoorOpening(opening.type) && !isDoubleDoorOpening(opening.type) && !isClosedGlazedEntryDoor(opening)) {
        addOpenDoorLeaf(targetScene, visiblePanel, opening.type, `opening:${opening.id}:${index}:open-leaf`);
      }
    }
  }

  function addWindowGlass(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    material: THREE.Material,
    name: string,
  ) {
    const mesh = addBox(
      targetScene,
      panel.widthM,
      panel.heightM,
      0.018,
      panel.position,
      material,
      0,
      name,
    );
    mesh.rotation.y = panel.rotationY;
    mesh.renderOrder = 20;
  }

  function addSunroomGlazingAssembly(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    namePrefix: string,
  ) {
    const glassMaterial = materialFor("glazing");
    const frameMaterial = materialFor("frameWhite", "#f4f5ef");
    const frameWidth = 0.04;
    const frameDepth = 0.032;
    const rotationDeg = -THREE.MathUtils.radToDeg(panel.rotationY);
    const sideOffset = Math.max(panel.widthM / 2 - frameWidth / 2, frameWidth);
    const railOffset = Math.max(panel.heightM / 2 - frameWidth / 2, frameWidth);

    addWindowGlass(targetScene, { ...panel, depthM: frameDepth }, glassMaterial, `${namePrefix}:glass`);
    addBox(targetScene, frameWidth, panel.heightM, frameDepth, offsetOpeningPosition(panel, -sideOffset, 0), frameMaterial, rotationDeg, `${namePrefix}:left-stile`);
    addBox(targetScene, frameWidth, panel.heightM, frameDepth, offsetOpeningPosition(panel, sideOffset, 0), frameMaterial, rotationDeg, `${namePrefix}:right-stile`);
    addBox(targetScene, panel.widthM, frameWidth, frameDepth, offsetOpeningPosition(panel, 0, railOffset), frameMaterial, rotationDeg, `${namePrefix}:top-rail`);
    addBox(targetScene, panel.widthM, frameWidth, frameDepth, offsetOpeningPosition(panel, 0, -railOffset), frameMaterial, rotationDeg, `${namePrefix}:bottom-rail`);
    if (panel.widthM > 1.2) {
      addBox(targetScene, frameWidth * 0.72, panel.heightM, frameDepth, panel.position, frameMaterial, rotationDeg, `${namePrefix}:centre-mullion`);
    }
  }

  function addWindowSideWallReturns(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    floorElevationM: number,
    namePrefix: string,
  ) {
    const wallHeightM = 2.35;
    const wallMaterial = materialFor("paintedWall", "#d8d2c5");
    const returnWidth = 0.055;
    const rotationDeg = -THREE.MathUtils.radToDeg(panel.rotationY);
    const sideOffset = panel.widthM / 2 + returnWidth / 2;
    [-sideOffset, sideOffset].forEach((acrossM, index) => {
      const position = offsetOpeningPosition(panel, acrossM, 0);
      addBox(
        targetScene,
        returnWidth,
        wallHeightM,
        panel.depthM,
        {
          x: position.x,
          y: floorElevationM + wallHeightM / 2,
          z: position.z,
        },
        wallMaterial,
        rotationDeg,
        `${namePrefix}:${index}`,
      );
    });
  }

  function openingPanelSpecFromAnchor(
    anchor: ThreeDSceneConfig["openings"][number]["anchors"][number],
    floorElevationM: number,
    panelHeightM: number,
    panelThicknessM: number,
    sillHeightM: number,
  ): OpeningPanelRenderSpec {
    return {
      widthM: Math.max(anchor.widthM, panelThicknessM),
      heightM: panelHeightM,
      depthM: Math.max(anchor.wallThicknessM, panelThicknessM),
      sillHeightM,
      position: {
        x: anchor.centre.x,
        y: floorElevationM + sillHeightM + panelHeightM / 2,
        z: anchor.centre.z,
      },
      rotationY: -Math.atan2(anchor.segment.z2 - anchor.segment.z1, anchor.segment.x2 - anchor.segment.x1),
    };
  }

  function openingDimensionsForType(openingType: string): { heightM: number; sillHeightM: number } {
    if (openingType.includes("window")) {
      return { heightM: 1.08, sillHeightM: 0.85 };
    }
    return { heightM: 2.05, sillHeightM: 0 };
  }

  function isSunroomWraparoundGlazing(opening: ThreeDSceneConfig["openings"][number]): boolean {
    return opening.id === "sunroom_wraparound_glazing";
  }

  function openingDimensionsForOpening(opening: ThreeDSceneConfig["openings"][number]): { heightM: number; sillHeightM: number } {
    if (isSunroomWraparoundGlazing(opening)) {
      return { heightM: 2.18, sillHeightM: 0.02 };
    }
    if (opening.heightM !== null && opening.heightM > 0) {
      return {
        heightM: opening.heightM,
        sillHeightM: opening.type.includes("window") && opening.heightM >= 1.85 ? 0.08 : openingDimensionsForType(opening.type).sillHeightM,
      };
    }
    if (opening.windowContext === "former_external") {
      return { heightM: 1.18, sillHeightM: 0.78 };
    }
    return openingDimensionsForType(opening.type);
  }

  function offsetSunroomGlazingPanelToExterior(
    panel: OpeningPanelRenderSpec,
    opening: ThreeDSceneConfig["openings"][number],
  ): OpeningPanelRenderSpec {
    const exteriorOffsetM = 0.09;
    const room = sceneConfig?.rooms.find((item) => item.id === opening.room);
    if (!room) {
      return panel;
    }
    const normal = {
      x: Math.sin(panel.rotationY),
      z: Math.cos(panel.rotationY),
    };
    const plus = {
      x: panel.position.x + normal.x * exteriorOffsetM,
      z: panel.position.z + normal.z * exteriorOffsetM,
    };
    const minus = {
      x: panel.position.x - normal.x * exteriorOffsetM,
      z: panel.position.z - normal.z * exteriorOffsetM,
    };
    const plusDistance = Math.hypot(plus.x - room.centre.x, plus.z - room.centre.z);
    const minusDistance = Math.hypot(minus.x - room.centre.x, minus.z - room.centre.z);
    const position = plusDistance >= minusDistance ? plus : minus;
    return {
      ...panel,
      depthM: Math.max(panel.depthM, 0.055),
      position: {
        ...panel.position,
        x: position.x,
        z: position.z,
      },
    };
  }

  function offsetFormerExternalWindowPanelToSunroom(panel: OpeningPanelRenderSpec): OpeningPanelRenderSpec {
    const sunroom = sceneConfig?.rooms.find((item) => item.id === "sunroom");
    return offsetFormerExternalWindowPanelToRoom(panel, "sunroom", sunroom);
  }

  function offsetFormerExternalWindowPanelToRoom(
    panel: OpeningPanelRenderSpec,
    roomId: string | null,
    providedRoom?: ThreeDSceneConfig["rooms"][number],
  ): OpeningPanelRenderSpec {
    const room = providedRoom ?? sceneConfig?.rooms.find((item) => item.id === roomId);
    if (!room) {
      return panel;
    }
    const offsetM = Math.max(panel.depthM / 2 + 0.035, 0.08);
    const normal = {
      x: Math.sin(panel.rotationY),
      z: Math.cos(panel.rotationY),
    };
    const plus = {
      x: panel.position.x + normal.x * offsetM,
      z: panel.position.z + normal.z * offsetM,
    };
    const minus = {
      x: panel.position.x - normal.x * offsetM,
      z: panel.position.z - normal.z * offsetM,
    };
    const plusDistance = Math.hypot(plus.x - room.centre.x, plus.z - room.centre.z);
    const minusDistance = Math.hypot(minus.x - room.centre.x, minus.z - room.centre.z);
    const position = plusDistance <= minusDistance ? plus : minus;
    return {
      ...panel,
      depthM: Math.min(panel.depthM, 0.055),
      position: {
        ...panel.position,
        x: position.x,
        z: position.z,
      },
    };
  }

  function addFormerExternalWindowAssembly(
    targetScene: THREE.Scene,
    opening: ThreeDSceneConfig["openings"][number],
    panel: OpeningPanelRenderSpec,
    material: THREE.Material,
    floorElevationM: number,
    namePrefix: string,
  ) {
    addWindowSideWallReturns(targetScene, panel, floorElevationM, `${namePrefix}:side-return`);
    [
      { panel: offsetFormerExternalWindowPanelToRoom(panel, opening.room), suffix: "room-side" },
      { panel: offsetFormerExternalWindowPanelToSunroom(panel), suffix: "sunroom-side" },
    ].forEach((face) => {
      addWindowGlass(targetScene, face.panel, material, `${namePrefix}:${face.suffix}:glass`);
      addOpeningFrame(targetScene, face.panel, `${namePrefix}:${face.suffix}:frame`);
    });
  }

  function offsetOpeningPosition(
    panel: OpeningPanelRenderSpec,
    acrossM: number,
    verticalM: number,
  ) {
    return {
      x: panel.position.x + Math.cos(panel.rotationY) * acrossM,
      y: panel.position.y + verticalM,
      z: panel.position.z - Math.sin(panel.rotationY) * acrossM,
    };
  }

  function addOpeningFrame(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    namePrefix: string,
    includeCentreMullion = true,
    frameStyle: "window" | "door" = "window",
  ) {
    const frameMaterial = materialFor("frameWhite", "#f4f5ef");
    const frameWidth = frameStyle === "door" ? 0.04 : 0.075;
    const frameDepth = panel.depthM;
    const frameHeight = panel.heightM + frameWidth * 2;
    const sideOffset = Math.max(panel.widthM / 2 - frameWidth / 2, frameWidth);
    const rotationDeg = -THREE.MathUtils.radToDeg(panel.rotationY);
    addBox(targetScene, frameWidth, frameHeight, frameDepth, offsetOpeningPosition(panel, -sideOffset, 0), frameMaterial, rotationDeg, `${namePrefix}:left`);
    addBox(targetScene, frameWidth, frameHeight, frameDepth, offsetOpeningPosition(panel, sideOffset, 0), frameMaterial, rotationDeg, `${namePrefix}:right`);
    addBox(targetScene, panel.widthM + frameWidth, frameWidth, frameDepth, offsetOpeningPosition(panel, 0, frameHeight / 2), frameMaterial, rotationDeg, `${namePrefix}:top`);
    if (frameStyle === "window") {
      addBox(targetScene, panel.widthM + frameWidth, frameWidth, frameDepth, offsetOpeningPosition(panel, 0, -frameHeight / 2), frameMaterial, rotationDeg, `${namePrefix}:bottom`);
    }
    if (includeCentreMullion && panel.widthM > 1.1) {
      addBox(targetScene, frameWidth * 0.78, panel.heightM, frameDepth, panel.position, frameMaterial, rotationDeg, `${namePrefix}:mullion`);
    }
  }

  function addOpeningWallInfill(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    floorElevationM: number,
    namePrefix: string,
  ) {
    const wallHeightM = 2.35;
    const wallMaterial = materialFor("paintedWall", "#d8d2c5");
    const rotationDeg = -THREE.MathUtils.radToDeg(panel.rotationY);
    const infillWidth = panel.widthM + 0.05;
    const infillDepth = panel.depthM;
    const panelTopAboveFloorM = panel.sillHeightM + panel.heightM;
    const topHeightM = wallHeightM - panelTopAboveFloorM;

    if (panel.sillHeightM > 0.08) {
      addBox(
        targetScene,
        infillWidth,
        panel.sillHeightM,
        infillDepth,
        {
          x: panel.position.x,
          y: floorElevationM + panel.sillHeightM / 2,
          z: panel.position.z,
        },
        wallMaterial,
        rotationDeg,
        `${namePrefix}:sill-wall`,
      );
    }

    if (topHeightM > 0.08) {
      addBox(
        targetScene,
        infillWidth,
        topHeightM,
        infillDepth,
        {
          x: panel.position.x,
          y: floorElevationM + panelTopAboveFloorM + topHeightM / 2,
          z: panel.position.z,
        },
        wallMaterial,
        rotationDeg,
        `${namePrefix}:lintel-wall`,
      );
    }
  }

  function addOpeningHandle(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    openingType: string,
    namePrefix: string,
  ) {
    if (!openingType.includes("door") && !openingType.includes("slider")) {
      return;
    }
    const handleMaterial = materialFor("doorHandle", "#1f2424");
    const rotationDeg = -THREE.MathUtils.radToDeg(panel.rotationY);
    const handleOffset = Math.max(panel.widthM * 0.24, 0.18);
    addBox(
      targetScene,
      0.035,
      0.42,
      panel.depthM,
      offsetOpeningPosition(panel, handleOffset, -0.12),
      handleMaterial,
      rotationDeg,
      namePrefix,
    );
  }

  function isDoorLikeOpening(openingType: string): boolean {
    return openingType.includes("door") || openingType.includes("slider");
  }

  function isSlidingDoorOpening(openingType: string): boolean {
    return openingType.includes("slider") || openingType.includes("sliding");
  }

  function isGlazedSlidingDoorOpening(opening: ThreeDSceneConfig["openings"][number]): boolean {
    return opening.type === "slider";
  }

  function isDoubleDoorOpening(openingType: string): boolean {
    return openingType === "door_group";
  }

  function isClosedGlazedEntryDoor(opening: ThreeDSceneConfig["openings"][number]): boolean {
    return opening.id === "future_front_door" || opening.swing === "closed_glazed_entry";
  }

  function shouldRenderOpeningFrame(opening: ThreeDSceneConfig["openings"][number]): boolean {
    return opening.type !== "door" || isClosedGlazedEntryDoor(opening);
  }

  function isPlainOpening(openingType: string): boolean {
    return openingType === "opening" || openingType === "large_opening";
  }

  function addSlidingDoorPanels(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    namePrefix: string,
  ) {
    const glassMaterial = materialFor("glazing");
    const panelWidth = panel.widthM * 0.58;
    const offset = panel.widthM * 0.11;
    [-offset, offset].forEach((acrossM, index) => {
      const mesh = addBox(
        targetScene,
        panelWidth,
        panel.heightM,
        0.018,
        offsetOpeningPosition(panel, acrossM, 0),
        glassMaterial,
        0,
        `${namePrefix}:${index}`,
      );
      mesh.rotation.y = panel.rotationY;
      mesh.renderOrder = 20;
    });
  }

  function addSolidSlidingDoorPanel(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    namePrefix: string,
  ) {
    const panelMaterial = materialFor("paintedWall", "#d8d2c5");
    const handleMaterial = materialFor("doorHandle", "#1f2424");
    const rotationDeg = -THREE.MathUtils.radToDeg(panel.rotationY);
    addBox(
      targetScene,
      panel.widthM * 0.86,
      panel.heightM,
      0.032,
      offsetOpeningPosition(panel, panel.widthM * 0.22, 0),
      panelMaterial,
      rotationDeg,
      `${namePrefix}:panel`,
    );
    addBox(
      targetScene,
      0.03,
      0.38,
      0.035,
      offsetOpeningPosition(panel, -panel.widthM * 0.14, -0.08),
      handleMaterial,
      rotationDeg,
      `${namePrefix}:handle`,
    );
  }

  function addDoubleDoorLeaves(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    opening: ThreeDSceneConfig["openings"][number],
    namePrefix: string,
  ) {
    addGlazedDoubleDoorLeaves(targetScene, panel, swingDirectionForOpening(opening), namePrefix);
  }

  function swingDirectionForOpening(opening: ThreeDSceneConfig["openings"][number]): number {
    return opening.swing === "outward_to_front_path" ? -1 : 1;
  }

  function addGlazedDoubleDoorLeaves(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    swingDirection: number,
    namePrefix: string,
  ) {
    const doorFrameMaterial = materialFor("frameWhite", "#f4f5ef");
    const doorGlassMaterial = materialFor("glazing");
    const handleMaterial = materialFor("doorHandle", "#1f2424");
    const leafWidth = panel.widthM / 2;
    const frameWidth = 0.07;
    const railHeight = 0.09;
    const openAngleRad = THREE.MathUtils.degToRad(78);
    [0, 1].forEach((index) => {
      const hingeOffset = index === 0 ? -panel.widthM / 2 : panel.widthM / 2;
      const leafDirection = index === 0 ? 1 : -1;
      const hinge = offsetOpeningPosition(panel, hingeOffset, 0);
      const leafGroup = new THREE.Group();
      leafGroup.position.set(hinge.x, panel.position.y, hinge.z);
      leafGroup.rotation.y = panel.rotationY + swingDirection * (index === 0 ? openAngleRad : -openAngleRad);
      leafGroup.name = `${namePrefix}:${index}`;

      const addLeafPart = (
        widthM: number,
        heightM: number,
        depthM: number,
        localX: number,
        localY: number,
        material: THREE.Material,
        name: string,
        renderOrder = 0,
      ) => {
        const mesh = new THREE.Mesh(new THREE.BoxGeometry(widthM, heightM, depthM), material);
        mesh.position.set(localX, localY, 0);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.name = name;
        mesh.renderOrder = renderOrder;
        leafGroup.add(mesh);
      };

      addLeafPart(
        Math.max(0.08, leafWidth - frameWidth * 2),
        Math.max(0.1, panel.heightM - railHeight * 2),
        0.018,
        leafDirection * leafWidth / 2,
        0,
        doorGlassMaterial,
        `${namePrefix}:${index}:glass`,
        20,
      );

      [frameWidth / 2, leafWidth - frameWidth / 2].forEach((leafAcrossM, frameIndex) => {
        addLeafPart(
          frameWidth,
          panel.heightM,
          0.035,
          leafDirection * leafAcrossM,
          0,
          doorFrameMaterial,
          `${namePrefix}:${index}:stile:${frameIndex}`,
        );
      });
      [-panel.heightM / 2 + railHeight / 2, panel.heightM / 2 - railHeight / 2].forEach((verticalM, railIndex) => {
        addLeafPart(
          leafWidth,
          railHeight,
          0.035,
          leafDirection * leafWidth / 2,
          verticalM,
          doorFrameMaterial,
          `${namePrefix}:${index}:rail:${railIndex}`,
        );
      });
      addLeafPart(
        0.035,
        0.36,
        0.035,
        leafDirection * leafWidth * 0.78,
        -0.08,
        handleMaterial,
        `${namePrefix}:${index}:handle`,
      );

      targetScene.add(leafGroup);
    });
  }

  function addClosedGlazedEntryDoor(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    namePrefix: string,
  ) {
    const doorMaterial = materialFor("entryDoorPaint", "#b7d8bd");
    const frameMaterial = materialFor("frameWhite", "#f4f5ef");
    const glassMaterial = materialFor("glazing");
    const handleMaterial = materialFor("doorHandle", "#1f2424");
    const rotationDeg = -THREE.MathUtils.radToDeg(panel.rotationY);
    const doorDepth = 0.04;
    const railHeight = Math.max(0.08, panel.heightM * 0.06);
    const stileWidth = Math.max(0.055, panel.widthM * 0.09);
    const glassWidth = Math.max(0.12, panel.widthM - stileWidth * 2.4);
    const glassHeight = Math.max(0.78, panel.heightM * 0.6);
    const glassYOffsetM = panel.heightM * 0.16;
    const lowerPanelHeight = Math.max(0.18, panel.heightM * 0.18);
    const lowerPanelInsetWidth = panel.widthM * 0.62;
    const lowerPanelYOffsetM = -panel.heightM * 0.29;
    const borderDepth = doorDepth + 0.018;

    addBox(
      targetScene,
      panel.widthM,
      panel.heightM,
      doorDepth,
      panel.position,
      doorMaterial,
      rotationDeg,
      `${namePrefix}:slab`,
    ).renderOrder = 18;

    addBox(
      targetScene,
      panel.widthM + 0.045,
      panel.heightM + 0.045,
      doorDepth * 0.55,
      {
        x: panel.position.x,
        y: panel.position.y,
        z: panel.position.z,
      },
      doorMaterial,
      rotationDeg,
      `${namePrefix}:outer-border`,
    ).renderOrder = 17;

    addBox(
      targetScene,
      glassWidth,
      glassHeight,
      doorDepth + 0.004,
      {
        x: panel.position.x,
        y: panel.position.y + glassYOffsetM,
        z: panel.position.z,
      },
      glassMaterial,
      rotationDeg,
      `${namePrefix}:glass`,
    ).renderOrder = 22;

    [-panel.widthM / 2 + stileWidth / 2, panel.widthM / 2 - stileWidth / 2].forEach((acrossM, index) => {
      addBox(
        targetScene,
        stileWidth,
        panel.heightM,
        borderDepth,
        offsetOpeningPosition(panel, acrossM, 0),
        frameMaterial,
        rotationDeg,
        `${namePrefix}:stile:${index}`,
      );
    });

    [
      -panel.heightM / 2 + railHeight / 2,
      glassYOffsetM - glassHeight / 2 - railHeight / 2,
      glassYOffsetM + glassHeight / 2 + railHeight / 2,
      panel.heightM / 2 - railHeight / 2,
    ].forEach((localY, index) => {
      addBox(
        targetScene,
        panel.widthM,
        railHeight,
        borderDepth,
        {
          ...panel.position,
          y: panel.position.y + localY,
        },
        frameMaterial,
        rotationDeg,
        `${namePrefix}:rail:${index}`,
      );
    });

    addBox(
      targetScene,
      lowerPanelInsetWidth,
      lowerPanelHeight,
      borderDepth,
      {
        x: panel.position.x,
        y: panel.position.y + lowerPanelYOffsetM,
        z: panel.position.z,
      },
      frameMaterial,
      rotationDeg,
      `${namePrefix}:lower-panel`,
    );

    addBox(
      targetScene,
      0.035,
      0.34,
      doorDepth + 0.02,
      offsetOpeningPosition(panel, panel.widthM * 0.28, -0.12),
      handleMaterial,
      rotationDeg,
      `${namePrefix}:handle`,
    );
  }

  function addOpenDoorLeaf(
    targetScene: THREE.Scene,
    panel: OpeningPanelRenderSpec,
    openingType: string,
    namePrefix: string,
  ) {
    if (!isDoorLikeOpening(openingType)) {
      return;
    }
    const leafMaterial = materialFor("frameWhite", "#f4f5ef");
    const rotationDeg = -THREE.MathUtils.radToDeg(panel.rotationY) + 78;
    const hingeOffset = -panel.widthM / 2;
    const openOffset = panel.widthM / 2;
    const hinge = offsetOpeningPosition(panel, hingeOffset, 0);
    addBox(
      targetScene,
      panel.widthM,
      panel.heightM,
      0.035,
      {
        x: hinge.x + Math.cos(THREE.MathUtils.degToRad(-rotationDeg)) * openOffset,
        y: panel.position.y,
        z: hinge.z + Math.sin(THREE.MathUtils.degToRad(-rotationDeg)) * openOffset,
      },
      leafMaterial,
      rotationDeg,
      namePrefix,
    );
  }

  function createFurnitureGroup(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): THREE.Group {
    const group = new THREE.Group();
    group.position.set(object.xM, floorElevationM, object.zM);
    group.position.y += object.supportSurfaceHeightM;
    group.rotation.y = THREE.MathUtils.degToRad(-object.rotationDeg);
    group.name = `furniture:${object.id}`;
    targetScene.add(group);
    return group;
  }

  function addFurniturePart(
    group: THREE.Group,
    widthM: number,
    heightM: number,
    depthM: number,
    localX: number,
    baseY: number,
    localZ: number,
    material: THREE.Material,
    name: string,
    options: FurniturePartOptions = {},
  ): THREE.Mesh {
    const mesh = new THREE.Mesh(
      new THREE.BoxGeometry(Math.max(widthM, 0.01), Math.max(heightM, 0.01), Math.max(depthM, 0.01)),
      material,
    );
    mesh.position.set(localX, baseY + heightM / 2, localZ);
    mesh.rotation.y = THREE.MathUtils.degToRad(-(options.rotationDeg ?? 0));
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.name = name;
    group.add(mesh);
    return mesh;
  }

  function addFurnitureCylinder(
    group: THREE.Group,
    radiusM: number,
    heightM: number,
    localX: number,
    baseY: number,
    localZ: number,
    material: THREE.Material,
    name: string,
    radialSegments = 24,
  ): THREE.Mesh {
    const mesh = new THREE.Mesh(
      new THREE.CylinderGeometry(Math.max(radiusM, 0.01), Math.max(radiusM, 0.01), Math.max(heightM, 0.01), radialSegments),
      material,
    );
    mesh.position.set(localX, baseY + heightM / 2, localZ);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.name = name;
    group.add(mesh);
    return mesh;
  }

  function addFourFurnitureLegs(
    group: THREE.Group,
    object: ThreeDFurnitureItem,
    heightM: number,
    material: THREE.Material,
    namePrefix: string,
  ) {
    const legWidth = Math.min(0.08, Math.max(0.035, Math.min(object.widthM, object.depthM) * 0.12));
    const insetX = Math.max(object.widthM / 2 - legWidth * 1.2, 0);
    const insetZ = Math.max(object.depthM / 2 - legWidth * 1.2, 0);
    [
      [-insetX, -insetZ],
      [insetX, -insetZ],
      [-insetX, insetZ],
      [insetX, insetZ],
    ].forEach(([x, z], index) => {
      addFurniturePart(group, legWidth, heightM, legWidth, x, 0, z, material, `${namePrefix}:leg:${index}`);
    });
  }

  function addBedFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const frameMaterial = objectMaterial(object);
    const mattressMaterial = materialFor("softNeutral");
    const pillowMaterial = materialFor("frameWhite", "#f4f5ef");
    addFurniturePart(group, object.widthM, 0.18, object.depthM, 0, 0, 0, frameMaterial, `${group.name}:base`);
    addFurniturePart(group, object.widthM * 0.94, 0.18, object.depthM * 0.84, 0, 0.16, object.depthM * 0.04, mattressMaterial, `${group.name}:mattress`);
    addFurniturePart(group, object.widthM, 0.72, 0.1, 0, 0, -object.depthM / 2 + 0.05, frameMaterial, `${group.name}:headboard`);
    const pillowCount = object.widthM > 1.3 ? 2 : 1;
    for (let index = 0; index < pillowCount; index += 1) {
      const x = pillowCount === 1 ? 0 : (index === 0 ? -object.widthM * 0.24 : object.widthM * 0.24);
      addFurniturePart(group, object.widthM * 0.36, 0.1, 0.34, x, 0.35, -object.depthM * 0.28, pillowMaterial, `${group.name}:pillow:${index}`);
    }
    addFurniturePart(group, object.widthM * 0.9, 0.055, object.depthM * 0.38, 0, 0.38, object.depthM * 0.18, materialFor(`blanket:${object.id}`, object.colour || "#b8a8a6"), `${group.name}:blanket`);
    return true;
  }

  function addLShapedSofaFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const material = objectMaterial(object);
    const cushionMaterial = materialFor(`sofa-cushion:${object.id}`, object.colour || "#53514b");
    const mainDepth = Math.min(object.depthM, Math.max(0.22, object.lShape?.main_depth_m ?? object.depthM * 0.42));
    const returnWidth = Math.min(object.widthM, Math.max(0.22, object.lShape?.return_width_m ?? object.widthM * 0.42));
    addFurniturePart(group, object.widthM, 0.22, mainDepth, 0, 0.16, -(object.depthM - mainDepth) / 2, cushionMaterial, `${group.name}:main-seat`);
    addFurniturePart(group, returnWidth, 0.22, object.depthM, -(object.widthM - returnWidth) / 2, 0.16, 0, cushionMaterial, `${group.name}:return-seat`);
    addFurniturePart(group, object.widthM, 0.56, 0.12, 0, 0.25, -object.depthM / 2 + 0.06, material, `${group.name}:back`);
    addFurniturePart(group, 0.12, 0.48, object.depthM, -object.widthM / 2 + 0.06, 0.24, 0, material, `${group.name}:left-arm`);
    addFurniturePart(group, 0.12, 0.36, mainDepth, object.widthM / 2 - 0.06, 0.22, -(object.depthM - mainDepth) / 2, material, `${group.name}:right-arm`);
    [0.24, 0, -0.24].forEach((offset, index) => {
      addFurniturePart(group, Math.max(0.22, object.widthM * 0.22), 0.08, mainDepth * 0.78, offset * object.widthM, 0.4, -(object.depthM - mainDepth) / 2, material, `${group.name}:cushion-break:${index}`);
    });
    return true;
  }

  function addChairFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const material = objectMaterial(object);
    const frameMaterial = materialFor("timberFurniture");
    const isArmchair = object.catalogId === "armchair" || object.label.toLowerCase().includes("armchair");
    addFurniturePart(group, object.widthM * 0.82, 0.14, object.depthM * 0.72, 0, 0.32, object.depthM * 0.08, material, `${group.name}:seat`);
    addFurniturePart(group, object.widthM * 0.86, isArmchair ? 0.58 : 0.48, 0.08, 0, 0.38, -object.depthM * 0.32, material, `${group.name}:back`);
    if (isArmchair) {
      addFurniturePart(group, 0.1, 0.36, object.depthM * 0.72, -object.widthM * 0.44, 0.28, object.depthM * 0.08, material, `${group.name}:left-arm`);
      addFurniturePart(group, 0.1, 0.36, object.depthM * 0.72, object.widthM * 0.44, 0.28, object.depthM * 0.08, material, `${group.name}:right-arm`);
    }
    addFourFurnitureLegs(group, object, 0.34, frameMaterial, group.name);
    if (object.catalogId === "office_chair") {
      addFurniturePart(group, 0.12, 0.35, 0.12, 0, 0, 0.02, frameMaterial, `${group.name}:gas-lift`);
      addFurniturePart(group, object.widthM * 0.75, 0.06, 0.08, 0, 0, object.depthM * 0.35, frameMaterial, `${group.name}:caster-base-front`);
      addFurniturePart(group, object.widthM * 0.75, 0.06, 0.08, 0, 0, -object.depthM * 0.25, frameMaterial, `${group.name}:caster-base-back`);
    }
    return true;
  }

  function tableVisualHeight(object: ThreeDFurnitureItem): number {
    return object.catalogId === "coffee_table" ? 0.42 : object.heightM;
  }

  function addTableFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const material = objectMaterial(object);
    const visualHeight = tableVisualHeight(object);
    addFurniturePart(group, object.widthM, 0.08, object.depthM, 0, visualHeight - 0.08, 0, material, `${group.name}:top`);
    addFourFurnitureLegs(group, object, Math.max(0.18, visualHeight - 0.08), material, group.name);
    if (object.catalogId === "dining_table") {
      addFurniturePart(group, object.widthM * 0.72, 0.05, 0.08, 0, visualHeight - 0.18, -object.depthM * 0.38, material, `${group.name}:apron-back`);
      addFurniturePart(group, object.widthM * 0.72, 0.05, 0.08, 0, visualHeight - 0.18, object.depthM * 0.38, material, `${group.name}:apron-front`);
    }
    return true;
  }

  function addDeskFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const material = objectMaterial(object);
    const height = object.heightM;
    if (object.type === "l_desk" && object.lShape) {
      const mainDepth = Math.min(object.depthM, Math.max(0.18, object.lShape.main_depth_m));
      const returnWidth = Math.min(object.widthM, Math.max(0.18, object.lShape.return_width_m));
      addFurniturePart(group, object.widthM, 0.07, mainDepth, 0, height - 0.07, -(object.depthM - mainDepth) / 2, material, `${group.name}:main-top`);
      addFurniturePart(group, returnWidth, 0.07, object.depthM, -(object.widthM - returnWidth) / 2, height - 0.07, 0, material, `${group.name}:return-top`);
    } else {
      addFurniturePart(group, object.widthM, 0.07, object.depthM, 0, height - 0.07, 0, material, `${group.name}:top`);
    }
    addFourFurnitureLegs(group, object, Math.max(0.2, height - 0.07), materialFor("doorHandle"), group.name);
    addFurniturePart(group, object.widthM * 0.26, 0.38, object.depthM * 0.72, object.widthM * 0.33, 0, object.depthM * 0.04, material, `${group.name}:drawer-stack`);
    return true;
  }

  function addTvFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const screenMaterial = materialFor("darkAccent");
    const standMaterial = materialFor("doorHandle");
    addFurniturePart(group, object.widthM, object.heightM, 0.045, 0, 0.2, 0, screenMaterial, `${group.name}:screen`);
    addFurniturePart(group, object.widthM * 0.22, 0.18, 0.04, 0, 0.02, 0, standMaterial, `${group.name}:neck`);
    addFurniturePart(group, object.widthM * 0.42, 0.035, object.depthM * 0.6, 0, 0, object.depthM * 0.18, standMaterial, `${group.name}:base`);
    return true;
  }

  function isTvAboveFireplace(object: ThreeDFurnitureItem): boolean {
    if (object.type !== "tv" || !sceneConfig) {
      return false;
    }
    return sceneConfig.furniture.some((item) => {
      if (item.type !== "fireplace") {
        return false;
      }
      const horizontalTolerance = Math.max(0.35, Math.max(item.widthM, object.widthM) * 0.55);
      return Math.abs(item.xM - object.xM) <= horizontalTolerance
        && Math.abs(item.zM - object.zM) <= 0.75;
    });
  }

  function addWallMountedTvFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const screenMaterial = materialFor("darkAccent");
    const bracketMaterial = materialFor("doorHandle");
    const screenHeight = Math.max(0.42, Math.min(0.78, object.heightM));
    const screenY = 1.22;
    addFurniturePart(group, object.widthM, screenHeight, 0.045, 0, screenY, 0, screenMaterial, `${group.name}:wall-screen`);
    addFurniturePart(group, object.widthM * 0.36, 0.12, 0.035, 0, screenY - screenHeight * 0.48, object.depthM * 0.12, bracketMaterial, `${group.name}:wall-bracket`);
    return true;
  }

  function addPianoFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const timber = objectMaterial(object);
    const keyMaterial = materialFor("frameWhite");
    const darkMaterial = materialFor("doorHandle");
    addFurniturePart(group, object.widthM, object.heightM * 0.72, object.depthM * 0.55, 0, 0.28, -object.depthM * 0.12, timber, `${group.name}:upright-body`);
    addFurniturePart(group, object.widthM * 0.92, 0.08, object.depthM * 0.34, 0, 0.55, object.depthM * 0.24, keyMaterial, `${group.name}:keyboard`);
    addFurniturePart(group, object.widthM * 0.86, 0.035, object.depthM * 0.26, 0, 0.64, object.depthM * 0.24, darkMaterial, `${group.name}:black-keys`);
    addFurniturePart(group, object.widthM, 0.08, object.depthM, 0, object.heightM - 0.08, 0, timber, `${group.name}:top-lid`);
    return true;
  }

  function addFireplaceFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const surroundMaterial = objectMaterial(object);
    const fireboxMaterial = materialFor("darkAccent");
    const mantelMaterial = materialFor("timberFurniture");
    addFurniturePart(group, object.widthM, 0.12, object.depthM, 0, 0, 0, surroundMaterial, `${group.name}:hearth`);
    addFurniturePart(group, object.widthM * 0.92, object.heightM * 0.72, object.depthM * 0.3, 0, 0.12, -object.depthM * 0.12, surroundMaterial, `${group.name}:surround`);
    addFurniturePart(group, object.widthM * 0.56, object.heightM * 0.42, object.depthM * 0.34, 0, 0.18, -object.depthM * 0.02, fireboxMaterial, `${group.name}:firebox`);
    addFurniturePart(group, object.widthM, 0.08, object.depthM * 0.42, 0, object.heightM * 0.8, -object.depthM * 0.08, mantelMaterial, `${group.name}:mantel`);
    return true;
  }

  function cabinetVisualHeight(object: ThreeDFurnitureItem): number {
    if (object.catalogId === "base_cabinet" || object.catalogId === "tv_unit") {
      return object.catalogId === "tv_unit" ? 0.55 : 0.92;
    }
    if (object.catalogId === "linen_storage") {
      return 1.4;
    }
    return object.heightM;
  }

  function addStorageFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const material = objectMaterial(object);
    const accentMaterial = materialFor("doorHandle");
    const height = object.type === "bookcase" ? object.heightM : cabinetVisualHeight(object);
    if (object.type === "bookcase") {
      return addBookcaseFurniture(group, object, height, material, accentMaterial);
    }
    addFurniturePart(group, object.widthM, height, object.depthM, 0, 0, 0, material, `${group.name}:carcass`);
    if (object.catalogId === "base_cabinet" || object.catalogId === "tv_unit") {
      addFurniturePart(group, object.widthM, 0.055, object.depthM * 1.04, 0, height, 0, materialFor("whiteCounter"), `${group.name}:countertop`);
    }
    const drawerCount = object.type === "dresser_drawers" ? 4 : object.catalogId === "bedside_table" ? 2 : 3;
    for (let index = 0; index < drawerCount; index += 1) {
      const y = Math.max(0.08, height * (index + 0.55) / drawerCount);
      addFurniturePart(group, object.widthM * 0.9, 0.025, 0.025, 0, y, -object.depthM / 2 - 0.002, accentMaterial, `${group.name}:handle:${index}`);
    }
    return true;
  }

  function addBookcaseFurniture(
    group: THREE.Group,
    object: ThreeDFurnitureItem,
    height: number,
    material: THREE.Material,
    accentMaterial: THREE.Material,
  ): boolean {
    const panelThickness = Math.min(0.07, Math.max(0.035, object.widthM * 0.06));
    const backMaterial = materialFor(`bookcase-back:${object.id}`, "#26211d");
    const bookColours = ["#b94e3f", "#d6a05f", "#315f8c", "#7d8f55", "#e6dfd0"];
    addFurniturePart(group, object.widthM * 0.88, height * 0.92, panelThickness, 0, panelThickness, 0, backMaterial, `${group.name}:back-panel`);
    addFurniturePart(group, panelThickness, height, object.depthM, -object.widthM / 2 + panelThickness / 2, 0, 0, material, `${group.name}:left-side`);
    addFurniturePart(group, panelThickness, height, object.depthM, object.widthM / 2 - panelThickness / 2, 0, 0, material, `${group.name}:right-side`);
    addFurniturePart(group, object.widthM, panelThickness, object.depthM, 0, 0, 0, material, `${group.name}:bottom-rail`);
    addFurniturePart(group, object.widthM, panelThickness, object.depthM, 0, height - panelThickness, 0, material, `${group.name}:top-rail`);
    addFurniturePart(group, panelThickness, height * 0.92, object.depthM * 0.92, 0, panelThickness, 0, accentMaterial, `${group.name}:vertical-divider`);

    const shelfCount = Math.max(4, Math.min(7, Math.round(height / 0.34)));
    for (let index = 1; index < shelfCount; index += 1) {
      addFurniturePart(group, object.widthM * 0.92, panelThickness * 0.72, object.depthM * 0.88, 0, (height / shelfCount) * index, 0, material, `${group.name}:shelf:${index}`);
    }
    for (let shelfIndex = 0; shelfIndex < shelfCount - 1; shelfIndex += 1) {
      const shelfBase = (height / shelfCount) * shelfIndex + panelThickness;
      const shelfHeight = height / shelfCount;
      for (let bookIndex = 0; bookIndex < 5; bookIndex += 1) {
        const bookWidth = object.widthM * 0.065;
        const x = -object.widthM * 0.34 + bookIndex * object.widthM * 0.14 + (shelfIndex % 2) * object.widthM * 0.05;
        const bookHeight = Math.max(0.16, shelfHeight * (0.46 + ((bookIndex + shelfIndex) % 3) * 0.08));
        ([
          ["front", -object.depthM * 0.32],
          ["back", object.depthM * 0.32],
        ] as const).forEach(([face, z]) => {
          addFurniturePart(
            group,
            bookWidth,
            bookHeight,
            object.depthM * 0.16,
            x,
            shelfBase,
            z,
            materialFor(`book-spine-${face}:${object.id}:${shelfIndex}:${bookIndex}`, bookColours[(bookIndex + shelfIndex) % bookColours.length]),
            `${group.name}:book-spine-${face}:${shelfIndex}:${bookIndex}`,
          );
        });
      }
    }
    return true;
  }

  function addApplianceFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const material = objectMaterial(object);
    const darkMaterial = materialFor("doorHandle");
    const height = object.type === "refrigerator" ? 1.8 : 0.9;
    addFurniturePart(group, object.widthM, height, object.depthM, 0, 0, 0, material, `${group.name}:body`);
    if (object.type === "washer" || object.type === "dryer") {
      addFurnitureCylinder(group, Math.min(object.widthM, object.depthM) * 0.26, 0.025, 0, height * 0.42, -object.depthM / 2 - 0.004, materialFor("glazing"), `${group.name}:round-door`);
    } else if (object.catalogId === "oven_cooktop" || object.type === "appliance") {
      addFurniturePart(group, object.widthM * 0.72, 0.04, object.depthM * 0.48, 0, height + 0.01, 0, darkMaterial, `${group.name}:cooktop`);
      [-0.2, 0.2].forEach((offset, index) => {
        addFurnitureCylinder(group, Math.min(object.widthM, object.depthM) * 0.11, 0.015, object.widthM * offset, height + 0.04, 0, darkMaterial, `${group.name}:hob:${index}`);
      });
    } else if (object.type === "refrigerator") {
      addFurniturePart(group, 0.025, height * 0.72, 0.035, object.widthM * 0.38, height * 0.15, -object.depthM / 2 - 0.005, darkMaterial, `${group.name}:handle`);
      addFurniturePart(group, object.widthM * 0.92, 0.018, 0.025, 0, height * 0.55, -object.depthM / 2 - 0.004, darkMaterial, `${group.name}:door-split`);
    } else {
      addFurniturePart(group, object.widthM * 0.72, 0.38, 0.025, 0, height * 0.26, -object.depthM / 2 - 0.004, materialFor("glazing"), `${group.name}:front-panel`);
    }
    return true;
  }

  function addSinkFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const cabinetMaterial = objectMaterial(object);
    const counterMaterial = materialFor("whiteCounter");
    const metalMaterial = materialFor("doorHandle");
    addFurniturePart(group, object.widthM, 0.72, object.depthM, 0, 0, 0, cabinetMaterial, `${group.name}:cabinet`);
    addFurniturePart(group, object.widthM, 0.07, object.depthM, 0, 0.72, 0, counterMaterial, `${group.name}:counter`);
    addFurniturePart(group, object.widthM * 0.58, 0.045, object.depthM * 0.5, 0, 0.78, 0, materialFor("glazing"), `${group.name}:basin`);
    addFurniturePart(group, 0.035, 0.22, 0.035, 0, 0.82, -object.depthM * 0.12, metalMaterial, `${group.name}:tap-stem`);
    addFurniturePart(group, 0.2, 0.025, 0.025, 0.08, 1.02, -object.depthM * 0.12, metalMaterial, `${group.name}:tap-spout`);
    return true;
  }

  function addBathFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const shellMaterial = objectMaterial(object);
    addFurniturePart(group, object.widthM, 0.42, object.depthM, 0, 0, 0, shellMaterial, `${group.name}:outer-shell`);
    addFurniturePart(group, object.widthM * 0.84, 0.04, object.depthM * 0.68, 0, 0.42, 0, materialFor("glazing"), `${group.name}:inner-water`);
    addFurniturePart(group, 0.12, 0.06, 0.12, -object.widthM * 0.32, 0.47, -object.depthM * 0.2, materialFor("doorHandle"), `${group.name}:drain`);
    return true;
  }

  function addShowerFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const frameMaterial = materialFor("frameWhite");
    const glassMaterial = materialFor("glazing");
    addFurniturePart(group, object.widthM, 0.08, object.depthM, 0, 0, 0, objectMaterial(object), `${group.name}:tray`);
    addFurniturePart(group, 0.035, 1.9, object.depthM, -object.widthM / 2 + 0.018, 0.08, 0, glassMaterial, `${group.name}:left-glass`);
    addFurniturePart(group, 0.035, 1.9, object.depthM, object.widthM / 2 - 0.018, 0.08, 0, glassMaterial, `${group.name}:right-glass`);
    addFurniturePart(group, object.widthM, 1.9, 0.035, 0, 0.08, -object.depthM / 2 + 0.018, glassMaterial, `${group.name}:back-glass`);
    addFurniturePart(group, object.widthM, 0.04, 0.04, 0, 1.98, -object.depthM / 2 + 0.02, frameMaterial, `${group.name}:top-frame`);
    return true;
  }

  function addToiletFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const porcelain = objectMaterial(object);
    addFurniturePart(group, object.widthM * 0.78, 0.34, object.depthM * 0.5, 0, 0.18, object.depthM * 0.08, porcelain, `${group.name}:pan`);
    addFurnitureCylinder(group, Math.min(object.widthM, object.depthM) * 0.23, 0.08, 0, 0.48, object.depthM * 0.08, porcelain, `${group.name}:seat`);
    addFurnitureCylinder(group, Math.min(object.widthM, object.depthM) * 0.14, 0.04, 0, 0.53, object.depthM * 0.08, materialFor("glazing"), `${group.name}:bowl-inlay`);
    addFurniturePart(group, object.widthM * 0.82, 0.34, object.depthM * 0.18, 0, 0.42, -object.depthM * 0.28, porcelain, `${group.name}:cistern`);
    return true;
  }

  function addStoolFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const material = objectMaterial(object);
    addFurniturePart(group, object.widthM * 0.88, 0.09, object.depthM * 0.84, 0, object.heightM - 0.09, 0, material, `${group.name}:rounded-seat`);
    addFourFurnitureLegs(group, object, Math.max(0.18, object.heightM - 0.1), materialFor("timberFurniture"), group.name);
    return true;
  }

  function addWardrobeDoorFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const panelMaterial = materialFor("glazing");
    const frameMaterial = materialFor("frameWhite");
    addFurniturePart(group, object.widthM * 0.48, object.heightM, object.depthM, -object.widthM * 0.24, 0, 0, panelMaterial, `${group.name}:left-panel`);
    addFurniturePart(group, object.widthM * 0.48, object.heightM, object.depthM, object.widthM * 0.24, 0, 0, panelMaterial, `${group.name}:right-panel`);
    addFurniturePart(group, object.widthM, 0.035, object.depthM, 0, object.heightM - 0.035, 0, frameMaterial, `${group.name}:top-track`);
    addFurniturePart(group, object.widthM, 0.035, object.depthM, 0, 0, 0, frameMaterial, `${group.name}:bottom-track`);
    addFurniturePart(group, 0.035, object.heightM, object.depthM, 0, 0, 0, frameMaterial, `${group.name}:centre-overlap`);
    return true;
  }

  function addPartitionWallFurniture(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    const group = createFurnitureGroup(targetScene, object, floorElevationM);
    const material = objectMaterial(object);
    addFurniturePart(group, object.widthM, object.heightM, Math.min(object.depthM, 0.04), 0, 0, 0, material, `${group.name}:thin-wall`);
    addFurniturePart(group, 0.035, object.heightM, Math.min(object.depthM, 0.04), -object.widthM / 2, 0, 0, materialFor("frameWhite"), `${group.name}:left-cap`);
    addFurniturePart(group, 0.035, object.heightM, Math.min(object.depthM, 0.04), object.widthM / 2, 0, 0, materialFor("frameWhite"), `${group.name}:right-cap`);
    return true;
  }

  function addDetailedFurnitureObject(
    targetScene: THREE.Scene,
    object: ThreeDFurnitureItem,
    floorElevationM: number,
  ): boolean {
    if (object.type === "bed") {
      return addBedFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "l_sofa") {
      return addLShapedSofaFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "chair") {
      return addChairFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "table") {
      return addTableFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "desk" || object.type === "l_desk") {
      return addDeskFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "tv") {
      if (isTvAboveFireplace(object)) {
        return addWallMountedTvFurniture(targetScene, object, floorElevationM);
      }
      return addTvFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "piano") {
      return addPianoFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "fireplace") {
      return addFireplaceFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "cabinet" || object.type === "bookcase" || object.type === "bedside_table" || object.type === "dresser_drawers" || object.type === "pantry") {
      return addStorageFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "refrigerator" || object.type === "washer" || object.type === "dryer" || object.type === "dishwasher" || object.type === "appliance") {
      return addApplianceFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "sink" || object.type === "vanity") {
      return addSinkFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "bath") {
      return addBathFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "shower") {
      return addShowerFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "toilet") {
      return addToiletFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "stool") {
      return addStoolFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "wardrobe_doors") {
      return addWardrobeDoorFurniture(targetScene, object, floorElevationM);
    }
    if (object.type === "partition_wall") {
      return addPartitionWallFurniture(targetScene, object, floorElevationM);
    }
    return false;
  }

  function addFurnitureObject(targetScene: THREE.Scene, object: ThreeDFurnitureItem, floorElevationM: number) {
    const material = objectMaterial(object);
    const baseY = floorElevationM + object.heightM / 2;

    if (addDetailedFurnitureObject(targetScene, object, floorElevationM)) {
      return;
    }

    addBox(
      targetScene,
      object.widthM,
      object.heightM,
      object.depthM,
      { x: object.xM, y: baseY, z: object.zM },
      material,
      object.rotationDeg,
      `furniture:${object.id}`,
    );
  }

  function addBuiltInWardrobeDoors(
    targetScene: THREE.Scene,
    room: ThreeDSceneConfig["rooms"][number],
    floorElevationM: number,
  ) {
    const isMasterBedroomWardrobe = room.id === "master_bedroom_wardrobe";
    if (!isMasterBedroomWardrobe) {
      return;
    }
    const bounds = sceneGeometryBoundsList(room.geometry)[0];
    if (!bounds) {
      return;
    }
    const doorSets = 2;
    const frameMaterial = materialFor("frameWhite", "#f4f5ef");
    const doorMaterial = materialFor("glazing");
    const spanM = bounds.maxZ - bounds.minZ;
    const setWidthM = spanM / doorSets;
    const faceX = bounds.minX - 0.04;
    const rotationDeg = 90;
    for (let index = 0; index < doorSets; index += 1) {
      const centreZ = bounds.minZ + setWidthM * (index + 0.5);
      const baseName = `wardrobe-door:${room.id}:${index}`;
      addBox(
        targetScene,
        setWidthM * 0.92,
        2.02,
        0.026,
        {
          x: faceX,
          y: floorElevationM + 1.01,
          z: centreZ,
        },
        doorMaterial,
        rotationDeg,
        baseName,
      ).renderOrder = 18;
      addBox(
        targetScene,
        0.035,
        2.05,
        0.04,
        {
          x: faceX - 0.01,
          y: floorElevationM + 1.025,
          z: centreZ,
        },
        frameMaterial,
        rotationDeg,
        `${baseName}:centre-stile`,
      );
    }
  }

  function addFoundation(targetScene: THREE.Scene, config: ThreeDSceneConfig) {
    const material = materialFor("foundationMasonry", "#b8b1a5");
    const roomBounds = config.rooms.flatMap((room) => sceneGeometryBoundsList(room.geometry));
    const houseCentre = roomBounds.length > 0
      ? {
        x: (Math.min(...roomBounds.map((item) => item.minX)) + Math.max(...roomBounds.map((item) => item.maxX))) / 2,
        z: (Math.min(...roomBounds.map((item) => item.minZ)) + Math.max(...roomBounds.map((item) => item.maxZ))) / 2,
      }
      : { x: 0, z: 0 };
    config.foundation.skirtSegments.forEach((segment) => {
      const exteriorSegment = offsetSegmentForExteriorFace(segment, segment.exteriorFaceOffsetM, houseCentre);
      addWallSegment(
        targetScene,
        exteriorSegment,
        segment.heightM,
        segment.thicknessM,
        material,
        0,
        segment.id,
      );
    });
  }

  function offsetSegmentForExteriorFace(
    segment: { x1: number; z1: number; x2: number; z2: number },
    exteriorFaceOffsetM: number,
    houseCentre: { x: number; z: number },
  ) {
    const dx = segment.x2 - segment.x1;
    const dz = segment.z2 - segment.z1;
    const length = Math.hypot(dx, dz);
    if (length <= 0.01 || exteriorFaceOffsetM === 0) {
      return segment;
    }
    const normalA = { x: -dz / length, z: dx / length };
    const normalB = { x: dz / length, z: -dx / length };
    const mid = { x: (segment.x1 + segment.x2) / 2, z: (segment.z1 + segment.z2) / 2 };
    const distanceA = Math.hypot(mid.x + normalA.x * exteriorFaceOffsetM - houseCentre.x, mid.z + normalA.z * exteriorFaceOffsetM - houseCentre.z);
    const distanceB = Math.hypot(mid.x + normalB.x * exteriorFaceOffsetM - houseCentre.x, mid.z + normalB.z * exteriorFaceOffsetM - houseCentre.z);
    const normal = distanceA >= distanceB ? normalA : normalB;
    return {
      x1: segment.x1 + normal.x * exteriorFaceOffsetM,
      z1: segment.z1 + normal.z * exteriorFaceOffsetM,
      x2: segment.x2 + normal.x * exteriorFaceOffsetM,
      z2: segment.z2 + normal.z * exteriorFaceOffsetM,
    };
  }

  function buildSceneContents(targetScene: THREE.Scene, config: ThreeDSceneConfig) {
    addStableGroundPlane(targetScene, config.groundPlane);
    addFoundation(targetScene, config);
    config.site.forEach((siteElement) => addSiteElement(targetScene, siteElement));
    config.deckEdges.forEach((edge) => addDeckEdge(targetScene, edge));
    config.steps.forEach((step) => addDeckStep(targetScene, step));
    config.rooms.forEach((room) => {
      addPlaneGeometry(
        targetScene,
        room.geometry,
        materialFor(room.floorMaterial),
        config.floorElevationM + 0.006,
        `room:${room.id}`,
      );
      addBuiltInWardrobeDoors(targetScene, room, config.floorElevationM);
    });
    config.walls.forEach((wall) => {
      const material = materialFor(wall.material);
      renderWallSegmentsWithOpeningCuts(targetScene, wall, material, config.floorElevationM, config);
      addExteriorWallEndpointCaps(targetScene, wall, material, config.floorElevationM);
    });
    config.openings.forEach((opening) => {
      addOpeningObject(targetScene, opening, config.floorElevationM);
    });
    config.furniture.forEach((object) => addFurnitureObject(targetScene, object, config.floorElevationM));
  }

  function updateRendererSize() {
    if (!stageElement || !renderer || !camera) {
      return;
    }
    const bounds = stageElement.getBoundingClientRect();
    const width = Math.max(1, bounds.width);
    const height = Math.max(1, bounds.height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  function updateCameraLook() {
    if (!camera) {
      return;
    }
    const direction = new THREE.Vector3(
      Math.cos(cameraPitch) * Math.cos(cameraYaw),
      Math.sin(cameraPitch),
      Math.cos(cameraPitch) * Math.sin(cameraYaw),
    );
    camera.lookAt(camera.position.clone().add(direction));
  }

  function pointCameraAt(position: { x: number; y: number; z: number }, lookAt: { x: number; y: number; z: number }) {
    if (!camera) {
      return;
    }
    camera.position.set(position.x, position.y, position.z);
    const dx = lookAt.x - position.x;
    const dy = lookAt.y - position.y;
    const dz = lookAt.z - position.z;
    cameraYaw = Math.atan2(dz, dx);
    cameraPitch = Math.atan2(dy, Math.hypot(dx, dz));
    updateCameraLook();
  }

  function resetCamera() {
    if (!camera || !sceneConfig) {
      return;
    }
    selectedPhotoViewpointId = "default";
    const bounds = sceneConfig.rooms.flatMap((room) => sceneGeometryBoundsList(room.geometry));
    if (bounds.length === 0) {
      pointCameraAt({ x: 16.5, y: 4.2, z: 0.5 }, { x: 8, y: 0.9, z: 5 });
      return;
    }
    const minX = Math.min(...bounds.map((item) => item.minX));
    const maxX = Math.max(...bounds.map((item) => item.maxX));
    const minZ = Math.min(...bounds.map((item) => item.minZ));
    const maxZ = Math.max(...bounds.map((item) => item.maxZ));
    const centre = {
      x: (minX + maxX) / 2,
      y: sceneConfig.floorElevationM + 0.85,
      z: (minZ + maxZ) / 2,
    };
    const span = Math.max(maxX - minX, maxZ - minZ);
    pointCameraAt(
      {
        x: centre.x + span * 1.05,
        y: Math.max(4.2, span * 0.62),
        z: centre.z - span * 0.92,
      },
      centre,
    );
  }

  function applyPhotoViewpoint(viewpointId: string) {
    if (!sceneConfig) {
      return;
    }
    selectedPhotoViewpointId = viewpointId;
    if (viewpointId === "default") {
      resetCamera();
      return;
    }
    const viewpoint = sceneConfig.photoViewpoints.find((view) => view.id === viewpointId);
    if (viewpoint) {
      pointCameraAt(viewpoint.position, viewpoint.lookAt);
    }
  }

  function updateMovement(deltaSeconds: number) {
    if (!camera) {
      return;
    }
    const speed = keysPressed.has("shift") ? 7.0 : 3.6;
    const turnSpeed = 2.2;
    const moveStep = speed * deltaSeconds;
    const forward = new THREE.Vector3(Math.cos(cameraYaw), 0, Math.sin(cameraYaw));
    const right = new THREE.Vector3(-Math.sin(cameraYaw), 0, Math.cos(cameraYaw));

    if (keysPressed.has("j")) {
      cameraYaw -= turnSpeed * deltaSeconds;
    }
    if (keysPressed.has("l")) {
      cameraYaw += turnSpeed * deltaSeconds;
    }
    if (keysPressed.has("i")) {
      cameraPitch = THREE.MathUtils.clamp(cameraPitch + turnSpeed * deltaSeconds * 0.5, -1.1, 0.8);
    }
    if (keysPressed.has("k")) {
      cameraPitch = THREE.MathUtils.clamp(cameraPitch - turnSpeed * deltaSeconds * 0.5, -1.1, 0.8);
    }
    if (keysPressed.has("arrowup") || keysPressed.has("w")) {
      camera.position.addScaledVector(forward, moveStep);
    }
    if (keysPressed.has("arrowdown") || keysPressed.has("s")) {
      camera.position.addScaledVector(forward, -moveStep);
    }
    if (keysPressed.has("arrowright") || keysPressed.has("d")) {
      camera.position.addScaledVector(right, moveStep);
    }
    if (keysPressed.has("arrowleft") || keysPressed.has("a")) {
      camera.position.addScaledVector(right, -moveStep);
    }
    if (keysPressed.has("q")) {
      camera.position.y = THREE.MathUtils.clamp(camera.position.y - moveStep, 0.55, 3.4);
    }
    if (keysPressed.has("e")) {
      camera.position.y = THREE.MathUtils.clamp(camera.position.y + moveStep, 0.55, 3.4);
    }
    updateCameraLook();
  }

  function animateThreeDScene() {
    if (!renderer || !scene || !camera || !clock) {
      return;
    }
    updateMovement(Math.min(clock.getDelta(), 0.05));
    renderer.render(scene, camera);
    animationFrameId = requestAnimationFrame(animateThreeDScene);
  }

  function cleanupThreeDScene() {
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
    resizeObserver?.disconnect();
    resizeObserver = null;
    keysPressed.clear();
    reusableMaterials.forEach((material) => material.dispose());
    reusableMaterials.clear();
    reusableTextures.forEach((texture) => texture.dispose());
    reusableTextures.clear();
    if (scene) {
      scene.traverse((object: THREE.Object3D) => {
        if (object instanceof THREE.Mesh) {
          object.geometry.dispose();
          const meshMaterial = object.material;
          if (Array.isArray(meshMaterial)) {
            meshMaterial.forEach((material) => material.dispose());
          } else {
            meshMaterial.dispose();
          }
        }
      });
    }
    renderer?.dispose();
    if (renderer?.domElement.parentElement) {
      renderer.domElement.parentElement.removeChild(renderer.domElement);
    }
    renderer = null;
    scene = null;
    camera = null;
    clock = null;
  }

  function initialiseThreeDScene() {
    if (!stageElement || !sceneConfig) {
      return;
    }
    cleanupThreeDScene();

    const nextScene = new THREE.Scene();
    nextScene.background = new THREE.Color("#cfd7d3");
    nextScene.fog = new THREE.Fog("#cfd7d3", 12, 34);

    const nextCamera = new THREE.PerspectiveCamera(58, 1, 0.05, 80);
    const nextRenderer = new THREE.WebGLRenderer({ antialias: true });
    nextRenderer.outputColorSpace = THREE.SRGBColorSpace;
    nextRenderer.toneMapping = THREE.ACESFilmicToneMapping;
    nextRenderer.toneMappingExposure = 1.05;
    nextRenderer.shadowMap.enabled = true;
    nextRenderer.shadowMap.type = THREE.PCFSoftShadowMap;
    nextRenderer.domElement.className = "three-d-canvas";

    stageElement.appendChild(nextRenderer.domElement);
    renderer = nextRenderer;
    scene = nextScene;
    camera = nextCamera;
    clock = new THREE.Clock();

    const hemisphere = new THREE.HemisphereLight("#e5f2ff", "#887862", 1.1);
    nextScene.add(hemisphere);
    const sun = new THREE.DirectionalLight("#fff4d5", 1.8);
    sun.position.set(5, 9, -6);
    sun.castShadow = true;
    sun.shadow.mapSize.width = 2048;
    sun.shadow.mapSize.height = 2048;
    nextScene.add(sun);
    const fill = new THREE.PointLight("#ffd9ad", 0.6, 12);
    fill.position.set(7.5, 2.0, 5.5);
    nextScene.add(fill);

    buildSceneContents(nextScene, sceneConfig);
    resetCamera();
    updateRendererSize();
    resizeObserver = new ResizeObserver(updateRendererSize);
    resizeObserver.observe(stageElement);
    animationFrameId = requestAnimationFrame(animateThreeDScene);
  }

  $effect(() => {
    projectId;
    scenarioId;
    void refreshThreeDData();
  });

  onDestroy(() => {
    cleanupThreeDScene();
  });
</script>

<svelte:window onkeydown={handleKeyDown} onkeyup={handleKeyUp} />

<section class="three-d-navigation" aria-label="3D Navigation">
  {#if loading && !sceneConfig}
    <div class="state-panel">Loading native 3D model...</div>
  {:else if error && !sceneConfig}
    <div class="state-panel error">{error}</div>
  {:else if sceneConfig && reviewData}
    <button
      type="button"
      class="three-d-stage"
      aria-label="Native 3D scene"
      bind:this={stageElement}
      onkeydown={handleKeyDown}
      onpointerdown={handlePointerDown}
      onpointermove={handlePointerMove}
      onpointerup={handlePointerUp}
      onpointercancel={handlePointerUp}
      onwheel={handleWheel}
    >
    </button>

    <aside class="three-d-status" aria-label="3D model status">
      <span class="eyebrow">Furniture layout</span>
      <strong>{reviewData.furniture_layout.source === "saved" ? "Saved layout" : "Seed layout"}</strong>
      <small>{sceneConfig.furniture.length} objects loaded</small>
      {#if refreshedAt}
        <small>Refreshed {refreshedAt}</small>
      {/if}
      <label>
        <span>View preset</span>
        <select
          value={selectedPhotoViewpointId}
          onchange={(event) => applyPhotoViewpoint(event.currentTarget.value)}
        >
          <option value="default">Default overview</option>
          {#each sceneConfig.photoViewpoints as viewpoint}
            <option value={viewpoint.id}>{viewpoint.label}</option>
          {/each}
        </select>
      </label>
      <button type="button" onclick={resetCamera}>Reset view</button>
      <button type="button" onclick={refreshThreeDData}>Refresh</button>
    </aside>

    {#if error}
      <p class="inline-error">{error}</p>
    {/if}
  {/if}
</section>

<style>
  .three-d-navigation {
    position: relative;
    min-height: calc(100vh - 96px);
    overflow: hidden;
    background: #cfd4ce;
    border: 1px solid #cbd6dc;
  }

  .three-d-stage {
    position: absolute;
    inset: 0;
    min-height: calc(100vh - 98px);
    width: 100%;
    padding: 0;
    border: 0;
    outline: none;
    background:
      linear-gradient(180deg, rgba(224, 231, 230, 0.95), rgba(201, 210, 203, 0.9)),
      repeating-linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.2) 0,
        rgba(255, 255, 255, 0.2) 1px,
        transparent 1px,
        transparent 40px
      );
    cursor: grab;
  }

  .three-d-stage:active {
    cursor: grabbing;
  }

  .three-d-status {
    position: absolute;
    right: 18px;
    bottom: 18px;
    display: grid;
    gap: 6px;
    width: min(260px, calc(100% - 36px));
    padding: 14px;
    border: 1px solid rgba(67, 84, 91, 0.18);
    background: rgba(247, 249, 249, 0.92);
    box-shadow: 0 16px 42px rgba(44, 60, 68, 0.18);
    color: #26353a;
  }

  .three-d-status button {
    justify-self: start;
    margin-top: 6px;
  }

  .three-d-status label {
    display: grid;
    gap: 4px;
    margin-top: 4px;
    font-size: 0.75rem;
    color: #5f6f75;
  }

  .three-d-status select {
    min-width: 0;
    border: 1px solid #c6d4da;
    border-radius: 6px;
    padding: 7px 8px;
    background: #fff;
    color: #26353a;
  }

  :global(.three-d-canvas) {
    display: block;
    width: 100%;
    height: 100%;
  }

  .inline-error {
    position: absolute;
    left: 18px;
    bottom: 18px;
    margin: 0;
    padding: 10px 12px;
    background: #fff3f3;
    color: #8f1d1d;
    border: 1px solid #e1aaaa;
  }
</style>
