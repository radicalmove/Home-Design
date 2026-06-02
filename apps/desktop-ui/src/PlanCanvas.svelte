<script lang="ts">
  import {
    anchoredViewOriginAfterZoom,
    angleDegFromCenter,
    centeredViewOrigin,
    dimensionLabel,
    lShapePath,
    nearestWallDistanceGuides,
    nextWheelPlanZoom,
    normaliseDegrees,
    objectBoundsSvg,
    planViewBoxSize,
    resizeObjectFromHandle,
    rotateDeltaIntoObjectSpace,
    roundedLShapePath,
    screenPixelsToSvgUnits,
    svgPointInViewBox,
    svgToMetres,
    visibleCanvasCenterOffset,
    viewOriginAfterPan,
  } from "./lib/furnitureGeometry";
  import {
    MIN_FURNITURE_SIZE_M,
    fixedDepthForObject,
    sortedFurnitureObjects,
  } from "./lib/furnitureState";
  import { symbolForFurnitureObject } from "./lib/furnitureSymbols";
  import type { ResizeHandleName, WallDistanceGuide, WallSegment } from "./lib/furnitureGeometry";
  import type { FurnitureLShapeDimensions, FurnitureLayout, FurnitureObject, PlanPoint } from "./types";

  type FurnitureSize = {
    width_m: number;
    depth_m: number;
    l_shape?: FurnitureLShapeDimensions | null;
  };

  type DragState = {
    kind: "move" | "resize" | "rotate";
    pointerId: number;
    object: FurnitureObject;
    startSvg: PlanPoint;
    resizeHandle?: ResizeHandleName;
    startAngleDeg?: number;
    startRotationDeg?: number;
  };

  type PanState = {
    pointerId: number;
    startClient: PlanPoint;
    startOrigin: PlanPoint;
  };

  type RoomLabel = {
    id: string;
    x: number;
    y: number;
    lines: string[];
  };

  type Props = {
    layout: FurnitureLayout;
    backgroundAssetPath: string;
    selectedObjectId: string | null;
    fixedVisible: boolean;
    moveableVisible: boolean;
    showLabels: boolean;
    showRoomLabels: boolean;
    zoom: number;
    onSelectObject: (objectId: string | null) => void;
    onMoveObject: (objectId: string, point: PlanPoint) => void;
    onResizeObject: (objectId: string, size: FurnitureSize, point?: PlanPoint) => void;
    onRotateObject: (objectId: string, rotationDeg: number) => void;
    onZoomChange: (zoom: number) => void;
    onResizePreview: (label: string | null, x: number, y: number) => void;
    onViewportCenterChange: (point: PlanPoint) => void;
    onBeginObjectEdit: (objectId: string) => void;
    onFinishObjectEdit: () => void;
  };

  const RESIZE_HANDLES: Array<{
    name: ResizeHandleName;
    x: number;
    y: number;
    label: string;
  }> = [
    { name: "n", x: 0.5, y: 0, label: "top edge" },
    { name: "ne", x: 1, y: 0, label: "top right corner" },
    { name: "e", x: 1, y: 0.5, label: "right edge" },
    { name: "se", x: 1, y: 1, label: "bottom right corner" },
    { name: "s", x: 0.5, y: 1, label: "bottom edge" },
    { name: "sw", x: 0, y: 1, label: "bottom left corner" },
    { name: "w", x: 0, y: 0.5, label: "left edge" },
    { name: "nw", x: 0, y: 0, label: "top left corner" },
  ];

  const ROOM_LABELS: RoomLabel[] = [
    { id: "sunroom", x: 608.2, y: 415.0, lines: ["Sunroom"] },
    { id: "lounge", x: 710.0, y: 389.4, lines: ["Lounge"] },
    { id: "kitchen-dining", x: 796.5, y: 372.0, lines: ["Kitchen / Dining"] },
    { id: "entrance", x: 853.2, y: 506.2, lines: ["Entrance"] },
    { id: "laundry", x: 929.6, y: 558.0, lines: ["Laundry"] },
    { id: "toilet", x: 929.6, y: 587.5, lines: ["Toilet"] },
    { id: "hallway", x: 684.0, y: 504.0, lines: ["Hallway"] },
    { id: "master-bedroom", x: 580.5, y: 512.0, lines: ["Master", "Bedroom"] },
    { id: "office", x: 687.0, y: 554.0, lines: ["Office"] },
    { id: "bathroom", x: 750.5, y: 562.4, lines: ["Bathroom"] },
    { id: "bedroom-2", x: 838.4, y: 592.0, lines: ["Bedroom 2"] },
  ];

  const WALL_THICKNESS_PX = {
    exterior: 8,
    thinExterior: 3.7,
    toiletExterior: 7.2,
    interior: 3.7,
    thinInterior: 3.3,
  } as const;

  const EXTERIOR_WALL_SEGMENT_IDS = new Set([
    "lounge-exterior",
    "lounge-sunroom-wall",
    "lounge-sunroom-lower-wall",
    "master-sunroom-old-external-wall",
    "hallway-north-wall",
    "hallway-sunroom-right-jamb",
    "kitchen-dining-west-wall",
    "kitchen-dining-north-wall",
    "kitchen-dining-east-wall",
    "private-rooms-south-wall",
    "master-west-wall",
    "laundry-toilet-exterior",
  ]);

  const THIN_EXTERIOR_WALL_SEGMENT_IDS = new Set([
    "entrance-deck-wall-west",
    "entrance-deck-wall-east",
  ]);

  const TOILET_EXTERIOR_WALL_SEGMENT_IDS = new Set(["toilet-south-external-wall"]);

  const THIN_INTERIOR_WALL_SEGMENT_IDS = new Set([
    "kitchen-entrance-return-wall",
    "entrance-north-return-wall",
    "bedroom2-north-wall-west",
    "bedroom2-north-wall-east",
    "master-office-wall-upper",
    "master-office-wall-mid-upper",
    "master-office-wall-mid-lower",
    "master-office-wall-lower",
    "wardrobe-office-wall",
    "office-bathroom-wall",
    "bathroom-bedroom2-wall",
    "laundry-toilet-wall-west",
    "laundry-toilet-wall-east",
  ]);

  function wallThicknessForSegment(segmentId: string): number {
    if (EXTERIOR_WALL_SEGMENT_IDS.has(segmentId)) {
      return WALL_THICKNESS_PX.exterior;
    }
    if (THIN_EXTERIOR_WALL_SEGMENT_IDS.has(segmentId)) {
      return WALL_THICKNESS_PX.thinExterior;
    }
    if (TOILET_EXTERIOR_WALL_SEGMENT_IDS.has(segmentId)) {
      return WALL_THICKNESS_PX.toiletExterior;
    }
    if (THIN_INTERIOR_WALL_SEGMENT_IDS.has(segmentId)) {
      return WALL_THICKNESS_PX.thinInterior;
    }
    return WALL_THICKNESS_PX.interior;
  }

  function withWallThickness(segments: Array<Omit<WallSegment, "thickness_px">>): WallSegment[] {
    return segments.map((segment) => ({
      ...segment,
      thickness_px: wallThicknessForSegment(segment.id),
    }));
  }

  function resizeHandlesForObject(object: FurnitureObject): typeof RESIZE_HANDLES {
    return fixedDepthForObject(object) !== null
      ? RESIZE_HANDLES.filter((handle) => handle.y === 0.5)
      : RESIZE_HANDLES;
  }

  const OUTLINE_ONLY_SYMBOLS = new Set(["armchair", "sliding-door", "stool", "table-and-chairs", "toilet"]);
  const INTRINSIC_TEXT_SYMBOLS = new Set(["dryer", "refrigerator", "washer"]);
  const SQUARE_CORNER_SYMBOLS = new Set([
    "bedside-table",
    "desk",
    "drawers",
    "fireplace",
    "partition-wall",
    "shower",
    "sink",
    "sliding-door",
    "storage",
    "wardrobe",
  ]);

  function symbolUsesBaseRect(shape: string): boolean {
    return !OUTLINE_ONLY_SYMBOLS.has(shape);
  }

  function symbolShowsIntrinsicText(shape: string): boolean {
    return INTRINSIC_TEXT_SYMBOLS.has(shape);
  }

  function symbolCornerRadius(shape: string): number {
    return SQUARE_CORNER_SYMBOLS.has(shape) ? 0 : 2;
  }

  function isLShapedSofa(object: FurnitureObject): boolean {
    return object.type === "l_sofa" || object.catalog_id === "l_sofa";
  }

  function lShapeMainDepthSvg(
    bounds: Pick<ReturnType<typeof objectBoundsSvg>, "height">,
    lShape: FurnitureLShapeDimensions,
  ): number {
    return Math.min(bounds.height, Math.max(0, lShape.main_depth_m * layout.plan_transform.px_per_m));
  }

  function lShapeReturnWidthSvg(
    bounds: Pick<ReturnType<typeof objectBoundsSvg>, "width">,
    lShape: FurnitureLShapeDimensions,
  ): number {
    return Math.min(bounds.width, Math.max(0, lShape.return_width_m * layout.plan_transform.px_per_m));
  }

  const REFERENCE_WALL_SEGMENTS: WallSegment[] = withWallThickness([
    { id: "sunroom-west-frame", x1: 549.2, y1: 483.4, x2: 549.2, y2: 442.3 },
    { id: "sunroom-front-frame", x1: 549.2, y1: 442.3, x2: 568, y2: 442.3 },
    { id: "sunroom-east-frame", x1: 606, y1: 401.6, x2: 606, y2: 346.7 },
    { id: "sunroom-north-frame", x1: 606, y1: 346.7, x2: 663.1, y2: 346.7 },
    { id: "lounge-exterior", x1: 659.1, y1: 348.8, x2: 762.8, y2: 348.8 },
    { id: "lounge-sunroom-wall", x1: 663.1, y1: 348.8, x2: 663.1, y2: 377.8 },
    { id: "lounge-sunroom-lower-wall", x1: 663.1, y1: 460, x2: 663.1, y2: 484.6 },
    { id: "master-sunroom-old-external-wall", x1: 533.9, y1: 482.4, x2: 627.1, y2: 482.4 },
    { id: "hallway-north-wall", x1: 627.1, y1: 482.4, x2: 635.2, y2: 482.4 },
    { id: "hallway-sunroom-right-jamb", x1: 655.4, y1: 482.4, x2: 663.1, y2: 482.4 },
    { id: "lounge-hallway-wall-west", x1: 663.1, y1: 484.6, x2: 701.5, y2: 484.6 },
    { id: "lounge-hallway-wall-east", x1: 723.5, y1: 484.6, x2: 760.9, y2: 484.6 },
    { id: "kitchen-dining-west-wall", x1: 758.8, y1: 348.8, x2: 758.8, y2: 302.3 },
    { id: "kitchen-dining-north-wall", x1: 758.8, y1: 302.3, x2: 833, y2: 302.3 },
    { id: "kitchen-dining-east-wall", x1: 833, y1: 302.3, x2: 833, y2: 491.9 },
    { id: "entrance-deck-wall-west", x1: 834.3, y1: 489.1, x2: 841.9, y2: 489.1 },
    { id: "entrance-deck-wall-east", x1: 881.8, y1: 489.1, x2: 956.4, y2: 489.1 },
    { id: "kitchen-entrance-return-wall", x1: 834.3, y1: 489.1, x2: 834.3, y2: 495.9 },
    { id: "entrance-north-return-wall", x1: 834.3, y1: 495.9, x2: 803.7, y2: 495.9 },
    { id: "private-rooms-south-wall", x1: 533.9, y1: 601.8, x2: 902.8, y2: 601.8 },
    { id: "toilet-south-external-wall", x1: 900.6, y1: 602.2, x2: 960.4, y2: 602.2 },
    { id: "bedroom2-east-wall", x1: 902.8, y1: 516.1, x2: 902.8, y2: 602.2 },
    { id: "master-west-wall", x1: 533.9, y1: 482.4, x2: 533.9, y2: 601.8 },
    { id: "kitchen-lounge-nub", x1: 760.9, y1: 348.8, x2: 760.9, y2: 361.3 },
    { id: "lounge-kitchen-divider", x1: 760.9, y1: 392.4, x2: 760.9, y2: 493 },
    { id: "hallway-south-wall-west", x1: 627.1, y1: 523, x2: 695.5, y2: 523 },
    { id: "hallway-south-wall-centre", x1: 717.3, y1: 523, x2: 727.1, y2: 523 },
    { id: "hallway-south-wall-east", x1: 743.4, y1: 523, x2: 773.9, y2: 523 },
    { id: "hallway-kitchen-door-wall", x1: 760.9, y1: 515, x2: 760.9, y2: 523 },
    { id: "bedroom2-north-wall-west", x1: 773.9, y1: 523.3, x2: 778.6, y2: 523.3 },
    { id: "bedroom2-north-wall-east", x1: 800.6, y1: 523.3, x2: 902.8, y2: 523.3 },
    { id: "master-office-wall-upper", x1: 627.1, y1: 482.4, x2: 627.1, y2: 494 },
    { id: "master-office-wall-mid-upper", x1: 627.1, y1: 516, x2: 627.1, y2: 527 },
    { id: "master-office-wall-mid-lower", x1: 627.1, y1: 558, x2: 627.1, y2: 567 },
    { id: "master-office-wall-lower", x1: 627.1, y1: 598, x2: 627.1, y2: 601.8 },
    { id: "wardrobe-office-wall", x1: 646.8, y1: 523, x2: 646.8, y2: 601.8 },
    { id: "office-bathroom-wall", x1: 727.1, y1: 521.2, x2: 727.1, y2: 601.8 },
    { id: "bathroom-bedroom2-wall", x1: 773.9, y1: 523, x2: 773.9, y2: 601.8 },
    { id: "entrance-laundry-wall", x1: 902.8, y1: 489.1, x2: 902.8, y2: 496.5 },
    { id: "laundry-toilet-wall-west", x1: 902.8, y1: 572.9, x2: 908.8, y2: 572.9 },
    { id: "laundry-toilet-wall-east", x1: 924.8, y1: 572.9, x2: 956.4, y2: 572.9 },
    { id: "kitchen-entrance-door-wall-upper", x1: 803.7, y1: 495.9, x2: 803.7, y2: 499.7 },
    { id: "kitchen-entrance-door-wall-lower", x1: 803.7, y1: 519.5, x2: 803.7, y2: 523.3 },
    { id: "laundry-toilet-exterior", x1: 956.4, y1: 487.3, x2: 956.4, y2: 602.2 },
  ]);

  let {
    layout,
    backgroundAssetPath,
    selectedObjectId,
    fixedVisible,
    moveableVisible,
    showLabels,
    showRoomLabels,
    zoom,
    onSelectObject,
    onMoveObject,
    onResizeObject,
    onRotateObject,
    onZoomChange,
    onResizePreview,
    onViewportCenterChange,
    onBeginObjectEdit,
    onFinishObjectEdit,
  }: Props = $props();

  let canvasElement = $state<HTMLDivElement | null>(null);
  let svgElement = $state<SVGSVGElement | null>(null);
  let dragState = $state<DragState | null>(null);
  let panState = $state<PanState | null>(null);
  let viewOrigin = $state<PlanPoint>({ x: 0, y: 0 });
  let canvasWidth = $state(0);
  let canvasHeight = $state(0);
  let viewOriginInitialised = $state(false);
  let previousZoom = $state(1);
  let internallyAnchoredZoom = $state<number | null>(null);
  let wallDistanceGuides = $state<WallDistanceGuide[]>([]);

  let visibleObjects = $derived(
    sortedFurnitureObjects(layout.objects).filter(
      (object) =>
        (object.layer === "fixed" && fixedVisible) || (object.layer === "moveable" && moveableVisible),
    ),
  );
  let canvasSize = $derived({
    width: canvasWidth || layout.plan_transform.svg_width_px,
    height: canvasHeight || layout.plan_transform.svg_height_px * 2,
  });
  let viewBoxSize = $derived(
    planViewBoxSize(canvasSize, zoom, layout.plan_transform.svg_width_px),
  );
  let viewBoxValue = $derived(
    `${viewOrigin.x.toFixed(3)} ${viewOrigin.y.toFixed(3)} ${viewBoxSize.width.toFixed(3)} ${viewBoxSize.height.toFixed(3)}`,
  );
  let resizeHandleSize = $derived(screenPixelsToSvgUnits(canvasSize, viewBoxSize, 12));
  let resizeHandleHalfSize = $derived(resizeHandleSize / 2);
  let rotateHandleRadius = $derived(screenPixelsToSvgUnits(canvasSize, viewBoxSize, 7));
  let rotateStemLength = $derived(screenPixelsToSvgUnits(canvasSize, viewBoxSize, 18));
  let rotateHandleOffset = $derived(screenPixelsToSvgUnits(canvasSize, viewBoxSize, 25));
  let wallDistanceLabelFontSize = $derived(screenPixelsToSvgUnits(canvasSize, viewBoxSize, 11));
  let wallDistanceLabelStrokeWidth = $derived(screenPixelsToSvgUnits(canvasSize, viewBoxSize, 3));

  $effect(() => {
    if (viewOriginInitialised || canvasWidth <= 0 || canvasHeight <= 0) {
      return;
    }

    viewOrigin = centeredViewOrigin(viewBoxSize, {
      width: layout.plan_transform.svg_width_px,
      height: layout.plan_transform.svg_height_px,
    });
    viewOriginInitialised = true;
  });

  $effect(() => {
    if (!viewOriginInitialised || previousZoom === zoom) {
      return;
    }

    if (internallyAnchoredZoom === zoom) {
      internallyAnchoredZoom = null;
      previousZoom = zoom;
      return;
    }

    const previousViewBoxSize = planViewBoxSize(
      canvasSize,
      previousZoom,
      layout.plan_transform.svg_width_px,
    );
    viewOrigin = anchoredViewOriginAfterZoom(
      viewOrigin,
      { x: canvasSize.width / 2, y: canvasSize.height / 2 },
      canvasSize,
      previousViewBoxSize,
      viewBoxSize,
    );
    previousZoom = zoom;
  });

  $effect(() => {
    if (!viewOriginInitialised) {
      return;
    }

    const viewportCenter = visibleViewportCenterInMetres();
    if (viewportCenter) {
      onViewportCenterChange(viewportCenter);
    }
  });

  function visibleViewportCenterInMetres(): PlanPoint | null {
    const rect = canvasElement?.getBoundingClientRect();
    if (!rect || typeof window === "undefined") {
      return null;
    }

    const visibleCenter = visibleCanvasCenterOffset(rect, {
      width: window.innerWidth,
      height: window.innerHeight,
    });

    return svgToMetres(
      svgPointInViewBox(viewOrigin, visibleCenter, canvasSize, viewBoxSize),
      layout.plan_transform,
    );
  }

  function svgPointFromEvent(event: PointerEvent): PlanPoint {
    const rect = canvasElement?.getBoundingClientRect();
    if (!rect) {
      return { x: 0, y: 0 };
    }

    return svgPointInViewBox(
      viewOrigin,
      { x: event.clientX - rect.left, y: event.clientY - rect.top },
      canvasSize,
      viewBoxSize,
    );
  }

  function localPointFromEvent(event: PointerEvent): PlanPoint {
    const rect = canvasElement?.getBoundingClientRect();
    if (!rect) {
      return { x: 0, y: 0 };
    }

    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  }

  function preventDragDefaults(event: Event) {
    event.preventDefault();
  }

  function updateWallDistanceGuides(object: FurnitureObject) {
    wallDistanceGuides = nearestWallDistanceGuides(
      objectBoundsSvg(object, layout.plan_transform),
      REFERENCE_WALL_SEGMENTS,
      layout.plan_transform,
    );
  }

  function clearWallDistanceGuides() {
    wallDistanceGuides = [];
  }

  function startBackgroundPan(event: PointerEvent) {
    event.preventDefault();
    if (event.button !== 0 || dragState || !canvasElement) {
      return;
    }

    onSelectObject(null);
    clearWallDistanceGuides();
    panState = {
      pointerId: event.pointerId,
      startClient: { x: event.clientX, y: event.clientY },
      startOrigin: viewOrigin,
    };
    canvasElement.setPointerCapture(event.pointerId);
  }

  function handlePanPointerMove(event: PointerEvent) {
    if (!panState || event.pointerId !== panState.pointerId || !canvasElement) {
      return;
    }

    event.preventDefault();
    viewOrigin = viewOriginAfterPan(
      panState.startOrigin,
      panState.startClient,
      { x: event.clientX, y: event.clientY },
      canvasSize,
      viewBoxSize,
    );
  }

  function finishPan(event: PointerEvent) {
    if (!panState || event.pointerId !== panState.pointerId) {
      return;
    }

    canvasElement?.releasePointerCapture(event.pointerId);
    panState = null;
  }

  function handleWheel(event: WheelEvent) {
    if (!canvasElement || event.deltaY === 0) {
      return;
    }

    event.preventDefault();
    const nextZoom = nextWheelPlanZoom(zoom, event.deltaY);
    if (nextZoom === zoom) {
      return;
    }

    const canvasBounds = canvasElement.getBoundingClientRect();
    const nextViewBoxSize = planViewBoxSize(
      { width: canvasBounds.width, height: canvasBounds.height },
      nextZoom,
      layout.plan_transform.svg_width_px,
    );
    viewOrigin = anchoredViewOriginAfterZoom(
      viewOrigin,
      { x: event.clientX - canvasBounds.left, y: event.clientY - canvasBounds.top },
      { width: canvasBounds.width, height: canvasBounds.height },
      viewBoxSize,
      nextViewBoxSize,
    );
    internallyAnchoredZoom = nextZoom;
    onZoomChange(nextZoom);
  }

  function startMove(event: PointerEvent, object: FurnitureObject) {
    event.preventDefault();
    event.stopPropagation();
    onBeginObjectEdit(object.id);
    dragState = {
      kind: "move",
      pointerId: event.pointerId,
      object,
      startSvg: svgPointFromEvent(event),
    };
    updateWallDistanceGuides(object);
    svgElement?.setPointerCapture(event.pointerId);
  }

  function startResize(event: PointerEvent, object: FurnitureObject, handle: ResizeHandleName) {
    event.preventDefault();
    event.stopPropagation();
    onBeginObjectEdit(object.id);
    clearWallDistanceGuides();
    dragState = {
      kind: "resize",
      pointerId: event.pointerId,
      object,
      startSvg: svgPointFromEvent(event),
      resizeHandle: handle,
    };
    svgElement?.setPointerCapture(event.pointerId);
    const local = localPointFromEvent(event);
    onResizePreview(dimensionLabel(object), local.x, local.y);
  }

  function startRotate(event: PointerEvent, object: FurnitureObject) {
    event.preventDefault();
    event.stopPropagation();
    const startSvg = svgPointFromEvent(event);
    const bounds = objectBoundsSvg(object, layout.plan_transform);
    dragState = {
      kind: "rotate",
      pointerId: event.pointerId,
      object,
      startSvg,
      startAngleDeg: angleDegFromCenter(startSvg, bounds),
      startRotationDeg: object.rotation_deg,
    };
    onBeginObjectEdit(object.id);
    clearWallDistanceGuides();
    svgElement?.setPointerCapture(event.pointerId);
    const local = localPointFromEvent(event);
    onResizePreview(`${normaliseDegrees(object.rotation_deg)} deg`, local.x, local.y);
  }

  function handlePointerMove(event: PointerEvent) {
    if (!dragState || event.pointerId !== dragState.pointerId) {
      return;
    }

    const currentSvg = svgPointFromEvent(event);
    const deltaSvg = {
      x: currentSvg.x - dragState.startSvg.x,
      y: currentSvg.y - dragState.startSvg.y,
    };

    if (dragState.kind === "move") {
      const nextPoint = {
        x: dragState.object.x_m + deltaSvg.x / layout.plan_transform.px_per_m,
        y: dragState.object.y_m + deltaSvg.y / layout.plan_transform.px_per_m,
      };
      updateWallDistanceGuides({
        ...dragState.object,
        x_m: nextPoint.x,
        y_m: nextPoint.y,
      });
      onMoveObject(dragState.object.id, nextPoint);
      return;
    }

    if (dragState.kind === "rotate") {
      const bounds = objectBoundsSvg(dragState.object, layout.plan_transform);
      const currentAngle = angleDegFromCenter(currentSvg, bounds);
      const nextRotation = normaliseDegrees(
        (dragState.startRotationDeg ?? dragState.object.rotation_deg)
          + currentAngle
          - (dragState.startAngleDeg ?? currentAngle),
      );
      onRotateObject(dragState.object.id, nextRotation);
      const local = localPointFromEvent(event);
      onResizePreview(`${nextRotation} deg`, local.x, local.y);
      return;
    }

    const localDelta = rotateDeltaIntoObjectSpace(
      deltaSvg,
      dragState.object.rotation_deg,
      layout.plan_transform,
    );
    const fixedDepth = fixedDepthForObject(dragState.object);
    const resizeDelta = fixedDepth !== null ? { ...localDelta, deltaDepthM: 0 } : localDelta;
    const resized = resizeObjectFromHandle(
      dragState.object,
      dragState.resizeHandle ?? "se",
      resizeDelta,
      fixedDepth !== null
        ? { widthM: MIN_FURNITURE_SIZE_M, depthM: fixedDepth }
        : MIN_FURNITURE_SIZE_M,
    );
    const size = {
      width_m: resized.width_m,
      depth_m: fixedDepth ?? resized.depth_m,
    };
    onResizeObject(dragState.object.id, size, { x: resized.x_m, y: resized.y_m });
    const local = localPointFromEvent(event);
    onResizePreview(`${size.width_m.toFixed(2)} m x ${size.depth_m.toFixed(2)} m`, local.x, local.y);
  }

  function finishPointer(event: PointerEvent) {
    if (!dragState || event.pointerId !== dragState.pointerId) {
      return;
    }
    svgElement?.releasePointerCapture(event.pointerId);
    onFinishObjectEdit();
    dragState = null;
    clearWallDistanceGuides();
    onResizePreview(null, 0, 0);
  }
</script>

<div
  bind:this={canvasElement}
  bind:clientWidth={canvasWidth}
  bind:clientHeight={canvasHeight}
  class="plan-canvas"
  class:is-panning={Boolean(panState)}
  role="group"
  aria-label="Furniture plan editor"
  ondragstart={preventDragDefaults}
  onselectstart={preventDragDefaults}
  onwheel={handleWheel}
  onpointermove={handlePanPointerMove}
  onpointerup={finishPan}
  onpointercancel={finishPan}
>
  <svg
    bind:this={svgElement}
    viewBox={viewBoxValue}
    role="img"
    aria-label="Reference plan with editable furniture overlay"
    onpointermove={handlePointerMove}
    onpointerup={finishPointer}
    onpointercancel={finishPointer}
    onpointerdown={startBackgroundPan}
  >
    <image href={backgroundAssetPath} width="1600" height="900" preserveAspectRatio="xMidYMid meet" />

    {#if showRoomLabels}
      <g class="room-label-layer" aria-hidden="true">
        {#each ROOM_LABELS as roomLabel (roomLabel.id)}
          <text class="room-label" x={roomLabel.x} y={roomLabel.y}>
            {#if roomLabel.lines.length === 1}
              {roomLabel.lines[0]}
            {:else}
              {#each roomLabel.lines as line, index}
                <tspan x={roomLabel.x} dy={index === 0 ? -4 : 9}>{line}</tspan>
              {/each}
            {/if}
          </text>
        {/each}
      </g>
    {/if}

    <g class="furniture-layer">
      {#each visibleObjects as object (object.id)}
        {@const bounds = objectBoundsSvg(object, layout.plan_transform)}
        {@const symbol = symbolForFurnitureObject(object.type, object.abbreviation, object.catalog_id)}
        <g
          class:selected={selectedObjectId === object.id}
          class={`furniture-object ${object.layer} ${symbol.shape}`}
          data-furniture-object={object.id}
          role="button"
          aria-label={object.label}
          tabindex="0"
          transform={`rotate(${object.rotation_deg}, ${bounds.cx}, ${bounds.cy})`}
          onpointerdown={(event) => startMove(event, object)}
        >
          {#if !symbolUsesBaseRect(symbol.shape)}
            <rect
              class="symbol-hit-target"
              x={bounds.x}
              y={bounds.y}
              width={bounds.width}
              height={bounds.height}
            />
          {/if}

          {#if symbol.shape === "l-shape" && object.l_shape && isLShapedSofa(object)}
            {@const sofaRadius = Math.max(2, Math.min(bounds.width, bounds.height) * 0.08)}
            {@const sofaPath = roundedLShapePath(bounds, object.l_shape, layout.plan_transform, sofaRadius)}
            <path class="l-sofa-body symbol-body" d={sofaPath} fill={object.colour} />
            <path class="l-sofa-outline" d={sofaPath} />
          {:else if symbol.shape === "l-shape" && object.l_shape}
            <path
              class="symbol-body"
              d={lShapePath(bounds, object.l_shape, layout.plan_transform)}
              fill={object.colour}
            />
          {:else if symbolUsesBaseRect(symbol.shape)}
            <rect
              class="symbol-body"
              x={bounds.x}
              y={bounds.y}
              width={bounds.width}
              height={bounds.height}
              rx={symbolCornerRadius(symbol.shape)}
              fill={object.colour}
            />
          {/if}

          {#if symbol.shape === "sofa"}
            <line x1={bounds.x + bounds.width * 0.1} y1={bounds.y + bounds.height * 0.26} x2={bounds.x + bounds.width * 0.9} y2={bounds.y + bounds.height * 0.26} />
            <line class="sofa-cushion-divider" x1={bounds.x + bounds.width * 0.34} y1={bounds.y + bounds.height * 0.26} x2={bounds.x + bounds.width * 0.34} y2={bounds.y + bounds.height * 0.86} />
            <line class="sofa-cushion-divider" x1={bounds.x + bounds.width * 0.66} y1={bounds.y + bounds.height * 0.26} x2={bounds.x + bounds.width * 0.66} y2={bounds.y + bounds.height * 0.86} />
            <line x1={bounds.x + bounds.width * 0.1} y1={bounds.y + bounds.height * 0.86} x2={bounds.x + bounds.width * 0.9} y2={bounds.y + bounds.height * 0.86} />
          {:else if symbol.shape === "l-shape" && object.l_shape && isLShapedSofa(object)}
            {@const sofaMainDepth = lShapeMainDepthSvg(bounds, object.l_shape)}
            {@const sofaReturnWidth = lShapeReturnWidthSvg(bounds, object.l_shape)}
            <line
              class="l-sofa-cushion-divider"
              x1={bounds.x + bounds.width * 0.34}
              y1={bounds.y + sofaMainDepth * 0.18}
              x2={bounds.x + bounds.width * 0.34}
              y2={bounds.y + sofaMainDepth * 0.88}
            />
            <line
              class="l-sofa-cushion-divider"
              x1={bounds.x + bounds.width * 0.67}
              y1={bounds.y + sofaMainDepth * 0.18}
              x2={bounds.x + bounds.width * 0.67}
              y2={bounds.y + sofaMainDepth * 0.88}
            />
            <line
              class="l-sofa-cushion-divider"
              x1={bounds.x + sofaReturnWidth * 0.18}
              y1={bounds.y + sofaMainDepth + (bounds.height - sofaMainDepth) * 0.5}
              x2={bounds.x + sofaReturnWidth * 0.88}
              y2={bounds.y + sofaMainDepth + (bounds.height - sofaMainDepth) * 0.5}
            />
            <line
              class="l-sofa-cushion-divider"
              x1={bounds.x + sofaReturnWidth * 0.2}
              y1={bounds.y + sofaMainDepth * 0.14}
              x2={bounds.x + sofaReturnWidth * 0.2}
              y2={bounds.y + bounds.height * 0.9}
            />
          {:else if symbol.shape === "fireplace"}
            <rect x={bounds.x + bounds.width * 0.18} y={bounds.y + bounds.height * 0.2} width={bounds.width * 0.64} height={bounds.height * 0.52} rx="0" />
            <line x1={bounds.x + bounds.width * 0.28} y1={bounds.y + bounds.height * 0.72} x2={bounds.x + bounds.width * 0.72} y2={bounds.y + bounds.height * 0.72} />
            <line x1={bounds.cx} y1={bounds.y + bounds.height * 0.28} x2={bounds.cx} y2={bounds.y + bounds.height * 0.62} />
          {:else if symbol.shape === "bed"}
            <line x1={bounds.x} y1={bounds.y + bounds.height * 0.25} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.25} />
            <rect x={bounds.x + bounds.width * 0.1} y={bounds.y + bounds.height * 0.06} width={bounds.width * 0.34} height={bounds.height * 0.15} rx="2" />
            <rect x={bounds.x + bounds.width * 0.56} y={bounds.y + bounds.height * 0.06} width={bounds.width * 0.34} height={bounds.height * 0.15} rx="2" />
            <path class="bed-blanket-fold" d={`M ${bounds.x} ${bounds.y + bounds.height * 0.56} L ${bounds.x + bounds.width * 0.32} ${bounds.y + bounds.height * 0.34} L ${bounds.x + bounds.width * 0.32} ${bounds.y + bounds.height}`} />
          {:else if symbol.shape === "bath"}
            <rect class="bath-inner" x={bounds.x + bounds.width * 0.08} y={bounds.y + bounds.height * 0.16} width={bounds.width * 0.84} height={bounds.height * 0.68} rx={Math.min(bounds.width, bounds.height) * 0.18} />
            <circle cx={bounds.x + bounds.width * 0.18} cy={bounds.cy} r={Math.max(1.5, Math.min(bounds.width, bounds.height) * 0.08)} />
          {:else if symbol.shape === "basin"}
            <ellipse class="basin-bowl" cx={bounds.cx} cy={bounds.y + bounds.height * 0.58} rx={Math.max(3, bounds.width * 0.34)} ry={Math.max(3, bounds.height * 0.3)} />
            <line x1={bounds.cx} y1={bounds.y} x2={bounds.cx} y2={bounds.y + bounds.height * 0.3} />
            <circle cx={bounds.cx} cy={bounds.y + bounds.height * 0.38} r={Math.max(1.5, Math.min(bounds.width, bounds.height) * 0.06)} />
          {:else if symbol.shape === "sink"}
            <rect
              class="sink-bowl"
              x={bounds.x + bounds.width * 0.18}
              y={bounds.y + bounds.height * 0.24}
              width={bounds.width * 0.64}
              height={bounds.height * 0.48}
              rx={Math.max(1, Math.min(bounds.width, bounds.height) * 0.08)}
            />
            <line x1={bounds.cx} y1={bounds.y} x2={bounds.cx} y2={bounds.y + bounds.height * 0.24} />
            <circle cx={bounds.cx} cy={bounds.y + bounds.height * 0.34} r={Math.max(1.5, Math.min(bounds.width, bounds.height) * 0.06)} />
          {:else if symbol.shape === "toilet"}
            <rect class="toilet-tank" x={bounds.x} y={bounds.y} width={bounds.width} height={bounds.height * 0.24} rx="2" fill={object.colour} />
            <circle cx={bounds.cx} cy={bounds.y + bounds.height * 0.1} r={Math.max(1.3, Math.min(bounds.width, bounds.height) * 0.05)} />
            <ellipse class="toilet-bowl" cx={bounds.cx} cy={bounds.y + bounds.height * 0.6} rx={Math.max(3, bounds.width * 0.48)} ry={Math.max(4, bounds.height * 0.4)} fill={object.colour} />
            <ellipse class="toilet-inlay" cx={bounds.cx} cy={bounds.y + bounds.height * 0.6} rx={Math.max(2, bounds.width * 0.24)} ry={Math.max(3, bounds.height * 0.2)} />
          {:else if symbol.shape === "shower"}
            <circle class="shower-head" cx={bounds.x + bounds.width * 0.18} cy={bounds.y + bounds.height * 0.2} r={Math.max(1.5, Math.min(bounds.width, bounds.height) * 0.05)} />
            <line class="shower-head-arm" x1={bounds.x + bounds.width * 0.22} y1={bounds.y + bounds.height * 0.22} x2={bounds.x + bounds.width * 0.42} y2={bounds.y + bounds.height * 0.22} />
            <line class="shower-head-arm" x1={bounds.x + bounds.width * 0.22} y1={bounds.y + bounds.height * 0.26} x2={bounds.x + bounds.width * 0.22} y2={bounds.y + bounds.height * 0.42} />
          {:else if symbol.shape === "oven"}
            <circle cx={bounds.x + bounds.width * 0.3} cy={bounds.y + bounds.height * 0.32} r={Math.max(2, Math.min(bounds.width, bounds.height) * 0.12)} />
            <circle cx={bounds.x + bounds.width * 0.7} cy={bounds.y + bounds.height * 0.32} r={Math.max(2, Math.min(bounds.width, bounds.height) * 0.12)} />
            <circle cx={bounds.x + bounds.width * 0.3} cy={bounds.y + bounds.height * 0.68} r={Math.max(2.5, Math.min(bounds.width, bounds.height) * 0.17)} />
            <circle cx={bounds.x + bounds.width * 0.7} cy={bounds.y + bounds.height * 0.68} r={Math.max(2.5, Math.min(bounds.width, bounds.height) * 0.17)} />
            <line x1={bounds.x} y1={bounds.y + bounds.height * 0.92} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.92} />
          {:else if symbol.shape === "island"}
            <rect x={bounds.x + bounds.width * 0.08} y={bounds.y + bounds.height * 0.08} width={bounds.width * 0.84} height={bounds.height * 0.84} rx={Math.min(bounds.width, bounds.height) * 0.16} />
          {:else if symbol.shape === "bedside-table"}
            <rect class="bedside-table-top" x={bounds.x + bounds.width * 0.18} y={bounds.y + bounds.height * 0.18} width={bounds.width * 0.64} height={bounds.height * 0.64} rx="0" />
            <circle cx={bounds.cx} cy={bounds.y + bounds.height * 0.58} r={Math.max(1.5, Math.min(bounds.width, bounds.height) * 0.08)} />
          {:else if symbol.shape === "desk"}
            <line x1={bounds.x} y1={bounds.y + bounds.height * 0.72} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.72} />
          {:else if symbol.shape === "table"}
            <ellipse cx={bounds.cx} cy={bounds.cy} rx={Math.max(3, bounds.width * 0.42)} ry={Math.max(3, bounds.height * 0.38)} />
          {:else if symbol.shape === "table-and-chairs"}
            <rect x={bounds.x + bounds.width * 0.08} y={bounds.y + bounds.height * 0.24} width={bounds.width * 0.84} height={bounds.height * 0.52} />
            <ellipse class="table-chair top" cx={bounds.x + bounds.width * 0.28} cy={bounds.y + bounds.height * 0.12} rx={bounds.width * 0.09} ry={bounds.height * 0.08} />
            <ellipse class="table-chair top" cx={bounds.cx} cy={bounds.y + bounds.height * 0.12} rx={bounds.width * 0.09} ry={bounds.height * 0.08} />
            <ellipse class="table-chair top" cx={bounds.x + bounds.width * 0.72} cy={bounds.y + bounds.height * 0.12} rx={bounds.width * 0.09} ry={bounds.height * 0.08} />
            <ellipse class="table-chair bottom" cx={bounds.x + bounds.width * 0.28} cy={bounds.y + bounds.height * 0.88} rx={bounds.width * 0.09} ry={bounds.height * 0.08} />
            <ellipse class="table-chair bottom" cx={bounds.cx} cy={bounds.y + bounds.height * 0.88} rx={bounds.width * 0.09} ry={bounds.height * 0.08} />
            <ellipse class="table-chair bottom" cx={bounds.x + bounds.width * 0.72} cy={bounds.y + bounds.height * 0.88} rx={bounds.width * 0.09} ry={bounds.height * 0.08} />
          {:else if symbol.shape === "chair"}
            <rect x={bounds.x + bounds.width * 0.18} y={bounds.y + bounds.height * 0.2} width={bounds.width * 0.64} height={bounds.height * 0.64} rx="2" />
            <line x1={bounds.x + bounds.width * 0.22} y1={bounds.y + bounds.height * 0.18} x2={bounds.x + bounds.width * 0.78} y2={bounds.y + bounds.height * 0.18} />
          {:else if symbol.shape === "stool"}
            <rect
              class="stool-seat symbol-body"
              x={bounds.x}
              y={bounds.y}
              width={bounds.width}
              height={bounds.height}
              rx={Math.max(2, Math.min(bounds.width, bounds.height) * 0.18)}
              fill={object.colour}
            />
            <circle cx={bounds.cx} cy={bounds.cy} r={Math.max(1.4, Math.min(bounds.width, bounds.height) * 0.08)} />
            <line x1={bounds.x + bounds.width * 0.28} y1={bounds.y + bounds.height * 0.28} x2={bounds.x + bounds.width * 0.18} y2={bounds.y + bounds.height * 0.18} />
            <line x1={bounds.x + bounds.width * 0.72} y1={bounds.y + bounds.height * 0.28} x2={bounds.x + bounds.width * 0.82} y2={bounds.y + bounds.height * 0.18} />
            <line x1={bounds.x + bounds.width * 0.28} y1={bounds.y + bounds.height * 0.72} x2={bounds.x + bounds.width * 0.18} y2={bounds.y + bounds.height * 0.82} />
            <line x1={bounds.x + bounds.width * 0.72} y1={bounds.y + bounds.height * 0.72} x2={bounds.x + bounds.width * 0.82} y2={bounds.y + bounds.height * 0.82} />
          {:else if symbol.shape === "armchair"}
            <rect class="armchair-seat symbol-body" x={bounds.x + bounds.width * 0.22} y={bounds.y + bounds.height * 0.22} width={bounds.width * 0.56} height={bounds.height * 0.58} rx="2" fill={object.colour} />
            <rect class="armchair-arm left symbol-body" x={bounds.x} y={bounds.y + bounds.height * 0.32} width={bounds.width * 0.18} height={bounds.height * 0.38} rx="2" fill={object.colour} />
            <rect class="armchair-arm right symbol-body" x={bounds.x + bounds.width * 0.82} y={bounds.y + bounds.height * 0.32} width={bounds.width * 0.18} height={bounds.height * 0.38} rx="2" fill={object.colour} />
            <rect class="armchair-back symbol-body" x={bounds.x + bounds.width * 0.24} y={bounds.y} width={bounds.width * 0.52} height={bounds.height * 0.14} rx="3" fill={object.colour} />
          {:else if symbol.shape === "drawers"}
            <line x1={bounds.x} y1={bounds.y + bounds.height * 0.33} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.33} />
            <line x1={bounds.x} y1={bounds.y + bounds.height * 0.66} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.66} />
            <circle cx={bounds.cx} cy={bounds.y + bounds.height * 0.16} r={Math.max(1.4, Math.min(bounds.width, bounds.height) * 0.04)} />
            <circle cx={bounds.cx} cy={bounds.y + bounds.height * 0.5} r={Math.max(1.4, Math.min(bounds.width, bounds.height) * 0.04)} />
            <circle cx={bounds.cx} cy={bounds.y + bounds.height * 0.83} r={Math.max(1.4, Math.min(bounds.width, bounds.height) * 0.04)} />
          {:else if symbol.shape === "tv"}
            <rect x={bounds.x + bounds.width * 0.08} y={bounds.y + bounds.height * 0.2} width={bounds.width * 0.84} height={bounds.height * 0.58} rx="1.5" />
            <line x1={bounds.cx} y1={bounds.y + bounds.height * 0.78} x2={bounds.cx} y2={bounds.y + bounds.height} />
            <line x1={bounds.x + bounds.width * 0.36} y1={bounds.y + bounds.height} x2={bounds.x + bounds.width * 0.64} y2={bounds.y + bounds.height} />
          {:else if symbol.shape === "heat-pump"}
            <line x1={bounds.x + bounds.width * 0.12} y1={bounds.y + bounds.height * 0.32} x2={bounds.x + bounds.width * 0.88} y2={bounds.y + bounds.height * 0.32} />
            <line x1={bounds.x + bounds.width * 0.12} y1={bounds.y + bounds.height * 0.5} x2={bounds.x + bounds.width * 0.88} y2={bounds.y + bounds.height * 0.5} />
            <line x1={bounds.x + bounds.width * 0.12} y1={bounds.y + bounds.height * 0.68} x2={bounds.x + bounds.width * 0.88} y2={bounds.y + bounds.height * 0.68} />
            <circle cx={bounds.x + bounds.width * 0.88} cy={bounds.y + bounds.height * 0.18} r={Math.max(1.5, Math.min(bounds.width, bounds.height) * 0.06)} />
          {:else if symbol.shape === "partition-wall"}
            <line x1={bounds.x} y1={bounds.cy} x2={bounds.x + bounds.width} y2={bounds.cy} />
          {:else if symbol.shape === "sliding-door"}
            <rect
              class="wardrobe-door-panel fixed"
              x={bounds.x}
              y={bounds.y + bounds.height * 0.52}
              width={bounds.width * 0.58}
              height={bounds.height * 0.34}
            />
            <rect
              class="wardrobe-door-panel sliding"
              x={bounds.x + bounds.width * 0.42}
              y={bounds.y + bounds.height * 0.14}
              width={bounds.width * 0.58}
              height={bounds.height * 0.34}
            />
          {:else if symbol.shape === "wardrobe"}
            <line class="wardrobe-base-line" x1={bounds.x} y1={bounds.y + bounds.height * 0.78} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.78} />
            <circle cx={bounds.x + bounds.width * 0.24} cy={bounds.y + bounds.height * 0.9} r={Math.max(1, Math.min(bounds.width, bounds.height) * 0.04)} />
            <circle cx={bounds.x + bounds.width * 0.76} cy={bounds.y + bounds.height * 0.9} r={Math.max(1, Math.min(bounds.width, bounds.height) * 0.04)} />
          {:else if symbol.shape === "storage"}
            <line x1={bounds.x} y1={bounds.y + bounds.height * 0.5} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.5} />
          {:else if symbol.shape === "appliance" || symbol.shape === "fixture"}
            <rect x={bounds.x + 4} y={bounds.y + 4} width={Math.max(4, bounds.width - 8)} height={Math.max(4, bounds.height - 8)} rx="3" />
          {/if}

          {#if showLabels && symbolShowsIntrinsicText(symbol.shape)}
            {#if symbol.shape === "washer" || symbol.shape === "dryer"}
              <text class="symbol-mark" x={bounds.cx} y={bounds.cy}>{symbol.shape === "washer" ? "W" : "D"}</text>
            {:else if symbol.shape === "refrigerator"}
              <text class="symbol-mark" x={bounds.cx} y={bounds.cy}>REF</text>
            {/if}
          {/if}

          {#if showLabels && symbol.abbreviation}
            {#if !symbolShowsIntrinsicText(symbol.shape)}
              <text x={bounds.cx} y={bounds.cy}>{symbol.abbreviation}</text>
            {/if}
          {/if}

          {#if selectedObjectId === object.id}
            <line
              class="rotate-stem"
              x1={bounds.cx}
              y1={bounds.y}
              x2={bounds.cx}
              y2={bounds.y - rotateStemLength}
            />
            <circle
              class="rotate-handle"
              cx={bounds.cx}
              cy={bounds.y - rotateHandleOffset}
              r={rotateHandleRadius}
              role="button"
              aria-label={`Rotate ${object.label}`}
              tabindex="0"
              onpointerdown={(event) => startRotate(event, object)}
            />
            {#each resizeHandlesForObject(object) as handle}
              <rect
                class={`resize-handle ${handle.name}`}
                data-resize-handle={handle.name}
                x={bounds.x + bounds.width * handle.x - resizeHandleHalfSize}
                y={bounds.y + bounds.height * handle.y - resizeHandleHalfSize}
                width={resizeHandleSize}
                height={resizeHandleSize}
                role="button"
                aria-label={`Resize ${object.label} from ${handle.label}`}
                tabindex="0"
                onpointerdown={(event) => startResize(event, object, handle.name)}
              />
            {/each}
          {/if}
        </g>
      {/each}
    </g>

    {#if wallDistanceGuides.length > 0}
      <g class="wall-distance-guides" aria-hidden="true">
        {#each wallDistanceGuides as guide (`${guide.side}-${guide.wallId}`)}
          <line
            class="wall-distance-guide"
            data-wall-distance-guide={guide.side}
            x1={guide.x1}
            y1={guide.y1}
            x2={guide.x2}
            y2={guide.y2}
          />
          <text
            class="wall-distance-label"
            x={guide.labelX}
            y={guide.labelY}
            font-size={wallDistanceLabelFontSize}
            stroke-width={wallDistanceLabelStrokeWidth}
          >
            {guide.label}
          </text>
        {/each}
      </g>
    {/if}
  </svg>
</div>

<style>
  .plan-canvas {
    position: relative;
    width: 100%;
    min-height: 560px;
    min-width: 0;
    aspect-ratio: 1 / 2;
    overflow: hidden;
    background: #ffffff;
    border: 1px solid #cfd8dd;
    border-radius: 8px;
    overscroll-behavior: contain;
    cursor: grab;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
  }

  .plan-canvas.is-panning {
    cursor: grabbing;
  }

  svg {
    display: block;
    width: 100%;
    height: 100%;
    touch-action: none;
    background: #ffffff;
    user-select: none;
    -webkit-user-select: none;
  }

  image {
    pointer-events: none;
    user-select: none;
    -webkit-user-drag: none;
    -webkit-user-select: none;
  }

  .furniture-object {
    cursor: grab;
  }

  .furniture-object:active {
    cursor: grabbing;
  }

  .symbol-body {
    stroke: #203139;
    stroke-width: 1.3;
    vector-effect: non-scaling-stroke;
  }

  .furniture-object.fixed .symbol-body {
    fill-opacity: 0.92;
    stroke-dasharray: none;
  }

  .furniture-object.moveable .symbol-body {
    fill-opacity: 0.86;
  }

  .furniture-object.selected .symbol-body {
    stroke: #d84d2a;
    stroke-width: 2.4;
  }

  .l-sofa-body {
    stroke: none;
  }

  .l-sofa-outline {
    fill: none;
    stroke: transparent;
    stroke-width: 1.3;
    stroke-linecap: round;
    stroke-linejoin: round;
    vector-effect: non-scaling-stroke;
  }

  .furniture-object.selected .l-sofa-outline {
    stroke: #d84d2a;
    stroke-width: 2.4;
  }

  .l-sofa-cushion-divider {
    stroke: #203139;
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
  }

  .furniture-object.partition-wall .symbol-body {
    stroke-dasharray: none;
    fill-opacity: 0.96;
  }

  line:not(.rotate-stem),
  ellipse:not(.symbol-body):not(.toilet-bowl):not(.toilet-inlay),
  circle:not(.symbol-body):not(.rotate-handle),
  path:not(.symbol-body):not(.l-sofa-outline),
  .furniture-object rect:not(.symbol-body):not(.resize-handle):not(.symbol-hit-target):not(.toilet-tank):not(.wardrobe-door-panel) {
    fill: none;
    stroke: #203139;
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
  }

  .toilet-tank,
  .toilet-bowl,
  .toilet-inlay {
    stroke: #203139;
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
  }

  .toilet-inlay {
    fill: #fffdf8;
  }

  .symbol-hit-target {
    fill: transparent;
    stroke: none;
    pointer-events: all;
  }

  .wardrobe-door-panel {
    fill: #fffdf8;
    stroke: #111;
    stroke-width: 0.45;
    vector-effect: non-scaling-stroke;
  }

  .furniture-object text {
    font-size: 13px;
    font-weight: 800;
    text-anchor: middle;
    dominant-baseline: middle;
    fill: #203139;
    paint-order: stroke;
    stroke: #ffffff;
    stroke-width: 3px;
    pointer-events: none;
  }

  .room-label-layer {
    pointer-events: none;
  }

  .room-label {
    font-size: 9px;
    font-weight: 500;
    text-anchor: middle;
    dominant-baseline: middle;
    fill: #1d2522;
    pointer-events: none;
  }

  .wall-distance-guides {
    pointer-events: none;
  }

  .wall-distance-guide {
    stroke: #0f766e;
    stroke-width: 1.3;
    stroke-dasharray: 4 3;
    vector-effect: non-scaling-stroke;
  }

  .wall-distance-label {
    font-weight: 800;
    text-anchor: middle;
    dominant-baseline: middle;
    fill: #0b514c;
    paint-order: stroke;
    stroke: #ffffff;
    stroke-linejoin: round;
  }

  .resize-handle {
    cursor: nwse-resize;
    fill: #ffffff;
    stroke: #d84d2a;
    stroke-width: 2;
    vector-effect: non-scaling-stroke;
  }

  .resize-handle.n,
  .resize-handle.s {
    cursor: ns-resize;
  }

  .resize-handle.e,
  .resize-handle.w {
    cursor: ew-resize;
  }

  .resize-handle.ne,
  .resize-handle.sw {
    cursor: nesw-resize;
  }

  .resize-handle.nw,
  .resize-handle.se {
    cursor: nwse-resize;
  }

  .rotate-stem {
    stroke: #d84d2a;
    stroke-width: 1.4;
    stroke-dasharray: 3 2;
    vector-effect: non-scaling-stroke;
  }

  .rotate-handle {
    cursor: grab;
    fill: #ffffff;
    stroke: #d84d2a;
    stroke-width: 2;
    vector-effect: non-scaling-stroke;
    pointer-events: all;
  }

  .rotate-handle:active {
    cursor: grabbing;
  }
</style>
