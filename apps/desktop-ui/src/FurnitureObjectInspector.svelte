<script lang="ts">
  import {
    MIN_FURNITURE_SIZE_M,
    PARTITION_WALL_THICKNESS_M,
    isPartitionWallObject,
  } from "./lib/furnitureState";
  import type { FurnitureLShapeDimensions, FurnitureLayerKind, FurnitureObject, PlanPoint } from "./types";

  type FurnitureSize = {
    width_m: number;
    depth_m: number;
    l_shape?: FurnitureLShapeDimensions | null;
  };

  type Props = {
    object: FurnitureObject | null;
    onMove: (objectId: string, point: PlanPoint) => void;
    onResize: (objectId: string, size: FurnitureSize) => void;
    onRotate: (objectId: string, rotationDeg: number) => void;
    onChangeLayer: (objectId: string, layer: FurnitureLayerKind) => void;
    onRecolour: (objectId: string, colour: string) => void;
    onDuplicate: (objectId: string) => void;
    onDelete: (objectId: string) => void;
  };

  let {
    object,
    onMove,
    onResize,
    onRotate,
    onChangeLayer,
    onRecolour,
    onDuplicate,
    onDelete,
  }: Props = $props();

  let isPartitionWall = $derived(Boolean(object && isPartitionWallObject(object)));
  let depthInputMin = $derived(isPartitionWall ? PARTITION_WALL_THICKNESS_M : MIN_FURNITURE_SIZE_M);
  let depthInputStep = $derived(isPartitionWall ? 0.01 : 0.05);
  let depthInputValue = $derived(isPartitionWall ? PARTITION_WALL_THICKNESS_M : object?.depth_m);

  function numberValue(event: Event): number {
    return Number((event.currentTarget as HTMLInputElement).value);
  }

  function updateX(event: Event) {
    if (object) {
      onMove(object.id, { x: numberValue(event), y: object.y_m });
    }
  }

  function updateY(event: Event) {
    if (object) {
      onMove(object.id, { x: object.x_m, y: numberValue(event) });
    }
  }

  function updateWidth(event: Event) {
    if (object) {
      onResize(object.id, { width_m: numberValue(event), depth_m: object.depth_m });
    }
  }

  function updateDepth(event: Event) {
    if (object) {
      onResize(object.id, {
        width_m: object.width_m,
        depth_m: isPartitionWall ? PARTITION_WALL_THICKNESS_M : numberValue(event),
      });
    }
  }

  function updateLShapeMainDepth(event: Event) {
    if (object?.l_shape) {
      onResize(object.id, {
        width_m: object.width_m,
        depth_m: object.depth_m,
        l_shape: {
          ...object.l_shape,
          main_depth_m: numberValue(event),
        },
      });
    }
  }

  function updateLShapeReturnWidth(event: Event) {
    if (object?.l_shape) {
      onResize(object.id, {
        width_m: object.width_m,
        depth_m: object.depth_m,
        l_shape: {
          ...object.l_shape,
          return_width_m: numberValue(event),
        },
      });
    }
  }

  function updateRotation(event: Event) {
    if (object) {
      onRotate(object.id, numberValue(event));
    }
  }

  function updateLayer(event: Event) {
    if (object) {
      onChangeLayer(object.id, (event.currentTarget as HTMLSelectElement).value as FurnitureLayerKind);
    }
  }

  function updateColour(event: Event) {
    if (object) {
      onRecolour(object.id, (event.currentTarget as HTMLInputElement).value);
    }
  }
</script>

<aside class="object-inspector" aria-label="Selected furniture object">
  <header>
    <span class="eyebrow">Selection</span>
    <h3>{object?.label ?? "None"}</h3>
  </header>

  {#if object}
    <dl class="object-meta">
      <div>
        <dt>Type</dt>
        <dd>{object.type}</dd>
      </div>
    </dl>

    <div class="field-grid">
      <label>
        Layer
        <select value={object.layer} onchange={updateLayer}>
          <option value="fixed">Fixed</option>
          <option value="moveable">Moveable</option>
        </select>
      </label>
      <label>
        X m
        <input type="number" step="0.05" value={object.x_m} oninput={updateX} />
      </label>
      <label>
        Y m
        <input type="number" step="0.05" value={object.y_m} oninput={updateY} />
      </label>
      <label>
        W m
        <input type="number" min="0.2" step="0.05" value={object.width_m} oninput={updateWidth} />
      </label>
      <label>
        D m
        <input
          type="number"
          min={depthInputMin}
          step={depthInputStep}
          value={depthInputValue}
          readonly={isPartitionWall}
          oninput={updateDepth}
        />
      </label>
      {#if object.l_shape}
        <label>
          Main arm D m
          <input
            type="number"
            min="0.2"
            max={object.depth_m}
            step="0.05"
            value={object.l_shape.main_depth_m}
            oninput={updateLShapeMainDepth}
          />
        </label>
        <label>
          Return W m
          <input
            type="number"
            min="0.2"
            max={object.width_m}
            step="0.05"
            value={object.l_shape.return_width_m}
            oninput={updateLShapeReturnWidth}
          />
        </label>
      {/if}
      <label>
        Rotation
        <input type="number" step="5" value={object.rotation_deg} oninput={updateRotation} />
      </label>
      <label>
        Colour
        <input type="color" value={object.colour} oninput={updateColour} />
      </label>
    </div>

    <div class="actions">
      <button type="button" onclick={() => onDuplicate(object.id)}>Duplicate</button>
      <button type="button" class="danger" onclick={() => onDelete(object.id)}>Delete</button>
    </div>

    {#if object.notes}
      <p class="notes">{object.notes}</p>
    {/if}
  {:else}
    <p class="empty">No object selected.</p>
  {/if}
</aside>

<style>
  .object-inspector {
    display: grid;
    align-content: start;
    gap: 14px;
    min-width: 0;
    min-height: 0;
    padding: 14px;
    background: #ffffff;
    border: 1px solid #d4dde1;
    border-radius: 8px;
  }

  header {
    display: grid;
    gap: 4px;
  }

  h3 {
    margin: 0;
    color: #1d2a30;
    font-size: 1rem;
    letter-spacing: 0;
    overflow-wrap: anywhere;
  }

  .object-meta {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin: 0;
  }

  .object-meta div {
    min-width: 0;
    padding: 8px;
    background: #f7f9fa;
    border: 1px solid #dce3e6;
    border-radius: 8px;
  }

  dt,
  dd {
    margin: 0;
  }

  dt {
    color: #64767d;
    font-size: 0.68rem;
    font-weight: 700;
  }

  dd {
    color: #24343b;
    font-size: 0.78rem;
    font-weight: 740;
    overflow-wrap: anywhere;
  }

  .field-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  label {
    display: grid;
    gap: 4px;
    min-width: 0;
    color: #475c64;
    font-size: 0.72rem;
    font-weight: 760;
  }

  input,
  select {
    width: 100%;
    min-width: 0;
    height: 34px;
    padding: 6px 8px;
    color: #1e3037;
    background: #ffffff;
    border: 1px solid #cfd9de;
    border-radius: 6px;
  }

  select {
    cursor: pointer;
  }

  input[type="color"] {
    padding: 3px;
  }

  .actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }

  button {
    min-height: 36px;
    color: #153029;
    font-weight: 740;
    cursor: pointer;
    background: #e4f2ee;
    border: 1px solid #8fcabd;
    border-radius: 8px;
  }

  button:hover,
  button:focus-visible {
    background: #d5ece6;
    outline: none;
  }

  button.danger {
    color: #7c2c22;
    background: #fff1ed;
    border-color: #edb9ac;
  }

  .notes,
  .empty {
    margin: 0;
    color: #5d7077;
    font-size: 0.77rem;
    line-height: 1.45;
  }
</style>
