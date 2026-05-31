<script lang="ts">
  import {
    anchoredViewOriginAfterZoom,
    angleDegFromCenter,
    centeredViewOrigin,
    dimensionLabel,
    nextWheelPlanZoom,
    normaliseDegrees,
    objectBoundsSvg,
    planViewBoxSize,
    resizeObjectFromHandle,
    rotateDeltaIntoObjectSpace,
    svgPointInViewBox,
    viewOriginAfterPan,
  } from "./lib/furnitureGeometry";
  import { symbolForFurnitureObject } from "./lib/furnitureSymbols";
  import type { ResizeHandleName } from "./lib/furnitureGeometry";
  import type { FurnitureLayout, FurnitureObject, PlanPoint } from "./types";

  type FurnitureSize = {
    width_m: number;
    depth_m: number;
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

  type Props = {
    layout: FurnitureLayout;
    backgroundAssetPath: string;
    selectedObjectId: string | null;
    fixedVisible: boolean;
    moveableVisible: boolean;
    showLabels: boolean;
    zoom: number;
    onSelectObject: (objectId: string | null) => void;
    onMoveObject: (objectId: string, point: PlanPoint) => void;
    onResizeObject: (objectId: string, size: FurnitureSize, point?: PlanPoint) => void;
    onRotateObject: (objectId: string, rotationDeg: number) => void;
    onZoomChange: (zoom: number) => void;
    onResizePreview: (label: string | null, x: number, y: number) => void;
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

  let {
    layout,
    backgroundAssetPath,
    selectedObjectId,
    fixedVisible,
    moveableVisible,
    showLabels,
    zoom,
    onSelectObject,
    onMoveObject,
    onResizeObject,
    onRotateObject,
    onZoomChange,
    onResizePreview,
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

  let visibleObjects = $derived(
    layout.objects.filter(
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

  function startBackgroundPan(event: PointerEvent) {
    event.preventDefault();
    if (event.button !== 0 || dragState || !canvasElement) {
      return;
    }

    onSelectObject(null);
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
    onSelectObject(object.id);
    dragState = {
      kind: "move",
      pointerId: event.pointerId,
      object,
      startSvg: svgPointFromEvent(event),
    };
    svgElement?.setPointerCapture(event.pointerId);
  }

  function startResize(event: PointerEvent, object: FurnitureObject, handle: ResizeHandleName) {
    event.preventDefault();
    event.stopPropagation();
    onSelectObject(object.id);
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
    onSelectObject(object.id);
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
      onMoveObject(dragState.object.id, {
        x: dragState.object.x_m + deltaSvg.x / layout.plan_transform.px_per_m,
        y: dragState.object.y_m + deltaSvg.y / layout.plan_transform.px_per_m,
      });
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
    const resized = resizeObjectFromHandle(
      dragState.object,
      dragState.resizeHandle ?? "se",
      localDelta,
    );
    const size = {
      width_m: resized.width_m,
      depth_m: resized.depth_m,
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
    dragState = null;
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

    <g class="furniture-layer">
      {#each visibleObjects as object (object.id)}
        {@const bounds = objectBoundsSvg(object, layout.plan_transform)}
        {@const symbol = symbolForFurnitureObject(object.type, object.abbreviation)}
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
          <rect
            class="symbol-body"
            x={bounds.x}
            y={bounds.y}
            width={bounds.width}
            height={bounds.height}
            rx="2"
            fill={object.colour}
          />

          {#if symbol.shape === "sofa"}
            <line x1={bounds.x} y1={bounds.y + bounds.height * 0.35} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.35} />
            <line x1={bounds.x + bounds.width * 0.5} y1={bounds.y} x2={bounds.x + bounds.width * 0.5} y2={bounds.y + bounds.height * 0.35} />
          {:else if symbol.shape === "bed"}
            <rect x={bounds.x + 4} y={bounds.y + 4} width={Math.max(5, bounds.width - 8)} height={Math.max(5, bounds.height * 0.22)} rx="2" />
          {:else if symbol.shape === "desk"}
            <line x1={bounds.x} y1={bounds.y + bounds.height * 0.72} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.72} />
          {:else if symbol.shape === "table"}
            <ellipse cx={bounds.cx} cy={bounds.cy} rx={Math.max(3, bounds.width * 0.42)} ry={Math.max(3, bounds.height * 0.38)} />
          {:else if symbol.shape === "chair"}
            <line x1={bounds.x + bounds.width * 0.25} y1={bounds.y + bounds.height * 0.2} x2={bounds.x + bounds.width * 0.25} y2={bounds.y + bounds.height * 0.85} />
            <line x1={bounds.x + bounds.width * 0.75} y1={bounds.y + bounds.height * 0.2} x2={bounds.x + bounds.width * 0.75} y2={bounds.y + bounds.height * 0.85} />
          {:else if symbol.shape === "storage"}
            <line x1={bounds.x} y1={bounds.y + bounds.height * 0.5} x2={bounds.x + bounds.width} y2={bounds.y + bounds.height * 0.5} />
          {:else if symbol.shape === "appliance" || symbol.shape === "fixture"}
            <rect x={bounds.x + 4} y={bounds.y + 4} width={Math.max(4, bounds.width - 8)} height={Math.max(4, bounds.height - 8)} rx="3" />
          {/if}

          {#if showLabels && symbol.abbreviation}
            <text x={bounds.cx} y={bounds.cy}>{symbol.abbreviation}</text>
          {/if}

          {#if selectedObjectId === object.id}
            <line
              class="rotate-stem"
              x1={bounds.cx}
              y1={bounds.y}
              x2={bounds.cx}
              y2={bounds.y - 18}
            />
            <circle
              class="rotate-handle"
              cx={bounds.cx}
              cy={bounds.y - 25}
              r="7"
              role="button"
              aria-label={`Rotate ${object.label}`}
              tabindex="0"
              onpointerdown={(event) => startRotate(event, object)}
            />
            {#each RESIZE_HANDLES as handle}
              <rect
                class={`resize-handle ${handle.name}`}
                data-resize-handle={handle.name}
                x={bounds.x + bounds.width * handle.x - 5}
                y={bounds.y + bounds.height * handle.y - 5}
                width="10"
                height="10"
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
    stroke-dasharray: 4 2;
  }

  .furniture-object.moveable .symbol-body {
    fill-opacity: 0.86;
  }

  .furniture-object.selected .symbol-body {
    stroke: #d84d2a;
    stroke-width: 2.4;
  }

  line:not(.rotate-stem),
  ellipse,
  .furniture-object rect:not(.symbol-body):not(.resize-handle) {
    fill: none;
    stroke: #203139;
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
  }

  text {
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
  }

  .rotate-handle:active {
    cursor: grabbing;
  }
</style>
