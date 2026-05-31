<script lang="ts">
  import { onMount } from "svelte";
  import DimensionBadge from "./DimensionBadge.svelte";
  import FurnitureCatalogPanel from "./FurnitureCatalogPanel.svelte";
  import FurnitureLayerControls from "./FurnitureLayerControls.svelte";
  import FurnitureObjectInspector from "./FurnitureObjectInspector.svelte";
  import PlanCanvas from "./PlanCanvas.svelte";
  import { clampPlanZoom, planZoomLabel } from "./lib/furnitureGeometry";
  import { loadFurnitureEditorData, persistFurnitureLayout } from "./lib/furnitureStore";
  import {
    addCatalogItem,
    changeObjectLayer,
    deleteObject,
    duplicateObject,
    moveObject,
    normaliseFurnitureLayout,
    recolourObject,
    resizeObject,
    rotateObject,
  } from "./lib/furnitureState";
  import type {
    FurnitureCatalog,
    FurnitureCatalogItem,
    FurnitureLayerKind,
    FurnitureLShapeDimensions,
    FurnitureLayout,
    PlanPoint,
  } from "./types";

  type FurnitureSize = {
    width_m: number;
    depth_m: number;
    l_shape?: FurnitureLShapeDimensions | null;
  };

  type SaveState = "idle" | "saving" | "saved" | "error";

  type Props = {
    projectId: string;
    backgroundAssetPath: string;
  };

  let { projectId, backgroundAssetPath }: Props = $props();

  let catalog = $state<FurnitureCatalog | null>(null);
  let layout = $state<FurnitureLayout | null>(null);
  let selectedObjectId = $state<string | null>(null);
  let fixedVisible = $state(true);
  let moveableVisible = $state(true);
  let labelsVisible = $state(false);
  let roomLabelsVisible = $state(false);
  let loading = $state(true);
  let loadError = $state<string | null>(null);
  let saveError = $state<string | null>(null);
  let saveState = $state<SaveState>("idle");
  let dimensionBadge = $state({ label: null as string | null, x: 0, y: 0 });
  let planZoom = $state(1);

  let saveTimer: ReturnType<typeof setTimeout> | null = null;

  let selectedObject = $derived(
    layout?.objects.find((object) => object.id === selectedObjectId) ?? null,
  );

  function toErrorMessage(reason: unknown): string {
    return reason instanceof Error ? reason.message : String(reason);
  }

  function scheduleSave(nextLayout: FurnitureLayout) {
    saveState = "saving";
    saveError = null;
    if (saveTimer) {
      clearTimeout(saveTimer);
    }

    saveTimer = setTimeout(async () => {
      try {
        await persistFurnitureLayout(nextLayout);
        saveState = "saved";
      } catch (reason: unknown) {
        saveState = "error";
        saveError = toErrorMessage(reason);
      }
    }, 300);
  }

  function commitLayout(nextLayout: FurnitureLayout) {
    layout = nextLayout;
    scheduleSave(nextLayout);
  }

  function handleAddCatalogItem(item: FurnitureCatalogItem) {
    if (!layout) {
      return;
    }

    const anchor = selectedObject
      ? { x: selectedObject.x_m + 0.35, y: selectedObject.y_m + 0.35 }
      : { x: 7.5, y: 5.2 };
    const nextLayout = addCatalogItem(layout, item, anchor);
    selectedObjectId = nextLayout.objects[nextLayout.objects.length - 1]?.id ?? selectedObjectId;
    commitLayout(nextLayout);
  }

  function handleMoveObject(objectId: string, point: PlanPoint) {
    if (layout) {
      commitLayout(moveObject(layout, objectId, point));
    }
  }

  function handleResizeObject(objectId: string, size: FurnitureSize, point?: PlanPoint) {
    if (layout) {
      const resizedLayout = resizeObject(layout, objectId, size);
      commitLayout(point ? moveObject(resizedLayout, objectId, point) : resizedLayout);
    }
  }

  function handleRotateObject(objectId: string, rotationDeg: number) {
    if (layout) {
      commitLayout(rotateObject(layout, objectId, rotationDeg));
    }
  }

  function handleRecolourObject(objectId: string, colour: string) {
    if (layout) {
      commitLayout(recolourObject(layout, objectId, colour));
    }
  }

  function handleChangeLayer(objectId: string, layer: FurnitureLayerKind) {
    if (layout) {
      commitLayout(changeObjectLayer(layout, objectId, layer));
    }
  }

  function handleDuplicateObject(objectId: string) {
    if (!layout) {
      return;
    }

    const nextLayout = duplicateObject(layout, objectId);
    selectedObjectId = nextLayout.objects[nextLayout.objects.length - 1]?.id ?? selectedObjectId;
    commitLayout(nextLayout);
  }

  function handleDeleteObject(objectId: string) {
    if (layout) {
      selectedObjectId = null;
      commitLayout(deleteObject(layout, objectId));
    }
  }

  function handleResizePreview(label: string | null, x: number, y: number) {
    dimensionBadge = { label, x, y };
  }

  function zoomPlan(delta: number) {
    planZoom = clampPlanZoom(planZoom + delta);
  }

  function handlePlanZoom(nextZoom: number) {
    planZoom = clampPlanZoom(nextZoom);
  }

  function resetPlanZoom() {
    planZoom = 1;
  }

  onMount(() => {
    let cancelled = false;

    async function loadData() {
      loading = true;
      loadError = null;
      try {
        const data = await loadFurnitureEditorData(projectId);
        if (cancelled) {
          return;
        }
        catalog = data.catalog;
        const normalisedLayout = normaliseFurnitureLayout(data.layoutResult.layout);
        layout = normalisedLayout;
        saveState = data.layoutResult.source === "saved" ? "saved" : "idle";
        if (JSON.stringify(normalisedLayout) !== JSON.stringify(data.layoutResult.layout)) {
          scheduleSave(normalisedLayout);
        }
      } catch (reason: unknown) {
        if (!cancelled) {
          loadError = toErrorMessage(reason);
        }
      } finally {
        if (!cancelled) {
          loading = false;
        }
      }
    }

    void loadData();

    return () => {
      cancelled = true;
      if (saveTimer) {
        clearTimeout(saveTimer);
      }
    };
  });
</script>

{#if loading}
  <div class="state-panel">Loading furniture editor...</div>
{:else if loadError}
  <div class="state-panel error">{loadError}</div>
{:else if catalog && layout}
  <section class="furniture-editor" aria-label="Furniture editor">
    <div class="editor-toolbar">
      <FurnitureLayerControls
        fixedVisible={fixedVisible}
        moveableVisible={moveableVisible}
        labelsVisible={labelsVisible}
        roomLabelsVisible={roomLabelsVisible}
        onToggleFixed={() => (fixedVisible = !fixedVisible)}
        onToggleMoveable={() => (moveableVisible = !moveableVisible)}
        onToggleLabels={() => (labelsVisible = !labelsVisible)}
        onToggleRoomLabels={() => (roomLabelsVisible = !roomLabelsVisible)}
      />
      <div class="editor-zoom-controls" aria-label="Furniture plan zoom controls">
        <button type="button" aria-label="Zoom out" onclick={() => zoomPlan(-0.1)}>-</button>
        <span>{planZoomLabel(planZoom)}</span>
        <button type="button" aria-label="Zoom in" onclick={() => zoomPlan(0.1)}>+</button>
        <button type="button" onclick={resetPlanZoom}>Reset</button>
      </div>
      <div class:error={saveState === "error"} class="save-status" aria-live="polite">
        {#if saveState === "saving"}
          Saving...
        {:else if saveState === "saved"}
          Saved
        {:else if saveState === "error"}
          {saveError ?? "Save failed"}
        {:else}
          Current layout
        {/if}
      </div>
    </div>

    <div class="editor-body">
      <FurnitureCatalogPanel {catalog} onAddItem={handleAddCatalogItem} />

      <div class="editor-plan-shell">
        <PlanCanvas
          {layout}
          {backgroundAssetPath}
          {selectedObjectId}
          {fixedVisible}
          {moveableVisible}
          showLabels={labelsVisible}
          showRoomLabels={roomLabelsVisible}
          zoom={planZoom}
          onSelectObject={(objectId) => (selectedObjectId = objectId)}
          onMoveObject={handleMoveObject}
          onResizeObject={handleResizeObject}
          onRotateObject={handleRotateObject}
          onZoomChange={handlePlanZoom}
          onResizePreview={handleResizePreview}
        />
        <DimensionBadge
          label={dimensionBadge.label}
          x={dimensionBadge.x}
          y={dimensionBadge.y}
        />
      </div>

      <FurnitureObjectInspector
        object={selectedObject}
        onMove={handleMoveObject}
        onResize={handleResizeObject}
        onRotate={handleRotateObject}
        onChangeLayer={handleChangeLayer}
        onRecolour={handleRecolourObject}
        onDuplicate={handleDuplicateObject}
        onDelete={handleDeleteObject}
      />
    </div>
  </section>
{:else}
  <div class="state-panel error">Furniture editor data is unavailable.</div>
{/if}

<style>
  .furniture-editor {
    display: grid;
    grid-template-rows: auto minmax(0, 1fr);
    gap: 12px;
    min-width: 0;
    min-height: 0;
  }

  .editor-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    justify-content: space-between;
    min-width: 0;
  }

  .editor-zoom-controls {
    display: grid;
    grid-template-columns: 34px minmax(54px, auto) 34px auto;
    gap: 6px;
    align-items: center;
    min-width: 0;
    padding: 4px;
    background: #ffffff;
    border: 1px solid #d4dde1;
    border-radius: 8px;
  }

  .editor-zoom-controls button {
    min-width: 34px;
    min-height: 32px;
    padding: 5px 8px;
    color: #203139;
    font-weight: 780;
    cursor: pointer;
    background: #f7f9fa;
    border: 1px solid #cfd8dd;
    border-radius: 6px;
  }

  .editor-zoom-controls button:hover,
  .editor-zoom-controls button:focus-visible {
    background: #e9f4f1;
    border-color: #8fcabd;
    outline: none;
  }

  .editor-zoom-controls span {
    min-width: 54px;
    color: #31434a;
    font-size: 0.8rem;
    font-weight: 760;
    text-align: center;
  }

  .save-status {
    min-height: 34px;
    padding: 8px 10px;
    color: #2c4a42;
    font-size: 0.78rem;
    font-weight: 750;
    overflow-wrap: anywhere;
    background: #edf8f5;
    border: 1px solid #b7dcd3;
    border-radius: 8px;
  }

  .save-status.error {
    color: #7c2c22;
    background: #fff1ed;
    border-color: #edb9ac;
  }

  .editor-body {
    display: grid;
    grid-template-columns: minmax(190px, 260px) minmax(0, 1fr) minmax(210px, 280px);
    gap: 12px;
    min-width: 0;
    min-height: 0;
  }

  .editor-plan-shell {
    position: relative;
    min-width: 0;
    min-height: 0;
  }

  @media (max-width: 1180px) {
    .editor-body {
      grid-template-columns: minmax(180px, 240px) minmax(0, 1fr);
    }

    .editor-body :global(.object-inspector) {
      grid-column: 1 / -1;
    }
  }

  @media (max-width: 860px) {
    .editor-body {
      grid-template-columns: 1fr;
    }
  }
</style>
