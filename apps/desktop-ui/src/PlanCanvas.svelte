<script lang="ts">
  import {
    angleDegFromCenter,
    dimensionLabel,
    normaliseDegrees,
    objectBoundsSvg,
    rotateDeltaIntoObjectSpace,
  } from "./lib/furnitureGeometry";
  import { symbolForFurnitureObject } from "./lib/furnitureSymbols";
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
    startAngleDeg?: number;
    startRotationDeg?: number;
  };

  type Props = {
    layout: FurnitureLayout;
    backgroundAssetPath: string;
    selectedObjectId: string | null;
    fixedVisible: boolean;
    moveableVisible: boolean;
    zoom: number;
    onSelectObject: (objectId: string | null) => void;
    onMoveObject: (objectId: string, point: PlanPoint) => void;
    onResizeObject: (objectId: string, size: FurnitureSize) => void;
    onRotateObject: (objectId: string, rotationDeg: number) => void;
    onResizePreview: (label: string | null, x: number, y: number) => void;
  };

  let {
    layout,
    backgroundAssetPath,
    selectedObjectId,
    fixedVisible,
    moveableVisible,
    zoom,
    onSelectObject,
    onMoveObject,
    onResizeObject,
    onRotateObject,
    onResizePreview,
  }: Props = $props();

  let svgElement = $state<SVGSVGElement | null>(null);
  let dragState = $state<DragState | null>(null);

  let visibleObjects = $derived(
    layout.objects.filter(
      (object) =>
        (object.layer === "fixed" && fixedVisible) || (object.layer === "moveable" && moveableVisible),
    ),
  );

  function svgPointFromEvent(event: PointerEvent): PlanPoint {
    const rect = svgElement?.getBoundingClientRect();
    if (!rect) {
      return { x: 0, y: 0 };
    }

    return {
      x: ((event.clientX - rect.left) / rect.width) * layout.plan_transform.svg_width_px,
      y: ((event.clientY - rect.top) / rect.height) * layout.plan_transform.svg_height_px,
    };
  }

  function localPointFromEvent(event: PointerEvent): PlanPoint {
    const rect = svgElement?.getBoundingClientRect();
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

  function selectBackground(event: PointerEvent) {
    event.preventDefault();
    if (!dragState) {
      onSelectObject(null);
    }
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

  function startResize(event: PointerEvent, object: FurnitureObject) {
    event.preventDefault();
    event.stopPropagation();
    onSelectObject(object.id);
    dragState = {
      kind: "resize",
      pointerId: event.pointerId,
      object,
      startSvg: svgPointFromEvent(event),
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
    const size = {
      width_m: Math.max(0.2, dragState.object.width_m + localDelta.deltaWidthM),
      depth_m: Math.max(0.2, dragState.object.depth_m + localDelta.deltaDepthM),
    };
    onResizeObject(dragState.object.id, size);
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
  class="plan-canvas"
  role="group"
  aria-label="Furniture plan editor"
  style={`--plan-zoom: ${zoom};`}
  ondragstart={preventDragDefaults}
  onselectstart={preventDragDefaults}
>
  <svg
    bind:this={svgElement}
    viewBox="0 0 1600 900"
    role="img"
    aria-label="Reference plan with editable furniture overlay"
    onpointermove={handlePointerMove}
    onpointerup={finishPointer}
    onpointercancel={finishPointer}
    onpointerdown={selectBackground}
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

          {#if symbol.abbreviation}
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
            <rect
              class="resize-handle"
              x={bounds.x + bounds.width - 5}
              y={bounds.y + bounds.height - 5}
              width="10"
              height="10"
              role="button"
              aria-label={`Resize ${object.label}`}
              tabindex="0"
              onpointerdown={(event) => startResize(event, object)}
            />
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
    min-width: 0;
    overflow: auto;
    background: #ffffff;
    border: 1px solid #cfd8dd;
    border-radius: 8px;
    overscroll-behavior: contain;
    user-select: none;
    -webkit-user-select: none;
  }

  svg {
    display: block;
    width: calc(100% * var(--plan-zoom));
    min-width: calc(720px * var(--plan-zoom));
    height: auto;
    aspect-ratio: 16 / 9;
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
