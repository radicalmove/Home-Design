<script lang="ts">
  import { dimensionLabel, objectBoundsSvg } from "./lib/furnitureGeometry";
  import { symbolForFurnitureObject } from "./lib/furnitureSymbols";
  import type { FurnitureLayout, FurnitureObject, PlanPoint } from "./types";

  type FurnitureSize = {
    width_m: number;
    depth_m: number;
  };

  type DragState = {
    kind: "move" | "resize";
    pointerId: number;
    object: FurnitureObject;
    startSvg: PlanPoint;
  };

  type Props = {
    layout: FurnitureLayout;
    backgroundAssetPath: string;
    selectedObjectId: string | null;
    fixedVisible: boolean;
    moveableVisible: boolean;
    onSelectObject: (objectId: string | null) => void;
    onMoveObject: (objectId: string, point: PlanPoint) => void;
    onResizeObject: (objectId: string, size: FurnitureSize) => void;
    onResizePreview: (label: string | null, x: number, y: number) => void;
  };

  let {
    layout,
    backgroundAssetPath,
    selectedObjectId,
    fixedVisible,
    moveableVisible,
    onSelectObject,
    onMoveObject,
    onResizeObject,
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

  function selectBackground() {
    if (!dragState) {
      onSelectObject(null);
    }
  }

  function startMove(event: PointerEvent, object: FurnitureObject) {
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

    const size = {
      width_m: Math.max(0.2, dragState.object.width_m + deltaSvg.x / layout.plan_transform.px_per_m),
      depth_m: Math.max(0.2, dragState.object.depth_m + deltaSvg.y / layout.plan_transform.px_per_m),
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

<div class="plan-canvas" aria-label="Furniture plan editor">
  <svg
    bind:this={svgElement}
    viewBox="0 0 1600 900"
    role="img"
    aria-label="Reference plan with editable furniture overlay"
    onpointermove={handlePointerMove}
    onpointerup={finishPointer}
    onpointercancel={finishPointer}
    onpointerleave={finishPointer}
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
  }

  svg {
    display: block;
    width: 100%;
    min-width: 720px;
    height: auto;
    aspect-ratio: 16 / 9;
    touch-action: none;
    background: #ffffff;
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

  line,
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
</style>
