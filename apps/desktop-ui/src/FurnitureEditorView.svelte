<script lang="ts">
  import { onMount } from "svelte";
  import DimensionBadge from "./DimensionBadge.svelte";
  import FurnitureCatalogPanel from "./FurnitureCatalogPanel.svelte";
  import FurnitureLayerControls from "./FurnitureLayerControls.svelte";
  import FurnitureObjectInspector from "./FurnitureObjectInspector.svelte";
  import PlanCanvas from "./PlanCanvas.svelte";
  import { clampPlanZoom, planZoomLabel } from "./lib/furnitureGeometry";
  import {
    FURNITURE_HISTORY_LIMIT,
    finishFurnitureGestureHistory,
    pushFurnitureHistory,
    redoFurnitureHistory,
    undoFurnitureHistory,
  } from "./lib/furnitureHistory";
  import { loadFurnitureEditorData, persistFurnitureLayout } from "./lib/furnitureStore";
  import {
    addCatalogItem,
    changeObjectLayer,
    deleteObject,
    duplicateObject,
    moveObject,
    normaliseFurnitureLayout,
    recolourObject,
    reorderObject,
    resizeObject,
    rotateObject,
  } from "./lib/furnitureState";
  import type { FurnitureOrderAction } from "./lib/furnitureState";
  import type {
    FurnitureCatalog,
    FurnitureCatalogItem,
    FurnitureLayerKind,
    FurnitureLShapeDimensions,
    FurnitureLayout,
    PlanPoint,
  } from "./types";
  import type { FurnitureHistoryState, FurnitureHistorySnapshot } from "./lib/furnitureHistory";

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
  let currentViewportCenter = $state<PlanPoint | null>(null);
  let history = $state<FurnitureHistoryState>({ undoStack: [], redoStack: [] });
  let activeObjectEditSnapshot = $state<FurnitureHistorySnapshot | null>(null);

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

  function currentHistorySnapshot(): FurnitureHistorySnapshot | null {
    return layout ? { layout, selectedObjectId } : null;
  }

  function restoreHistorySnapshot(snapshot: FurnitureHistorySnapshot) {
    layout = snapshot.layout;
    selectedObjectId = snapshot.selectedObjectId;
    dimensionBadge = { label: null, x: 0, y: 0 };
    scheduleSave(snapshot.layout);
  }

  function commitLayout(nextLayout: FurnitureLayout, nextSelectedObjectId = selectedObjectId) {
    const currentSnapshot = currentHistorySnapshot();
    if (currentSnapshot) {
      history = pushFurnitureHistory(history, currentSnapshot);
    }
    layout = nextLayout;
    selectedObjectId = nextSelectedObjectId;
    scheduleSave(nextLayout);
  }

  function previewLayout(nextLayout: FurnitureLayout, nextSelectedObjectId = selectedObjectId) {
    layout = nextLayout;
    selectedObjectId = nextSelectedObjectId;
  }

  function applyObjectEditLayout(
    nextLayout: FurnitureLayout,
    nextSelectedObjectId = selectedObjectId,
  ) {
    if (activeObjectEditSnapshot) {
      previewLayout(nextLayout, nextSelectedObjectId);
      return;
    }

    commitLayout(nextLayout, nextSelectedObjectId);
  }

  function handleBeginObjectEdit(objectId: string) {
    if (!layout) {
      return;
    }

    activeObjectEditSnapshot ??= { layout, selectedObjectId: objectId };
    selectedObjectId = objectId;
  }

  function handleFinishObjectEdit() {
    if (!activeObjectEditSnapshot || !layout) {
      activeObjectEditSnapshot = null;
      return;
    }

    const startSnapshot = activeObjectEditSnapshot;
    const currentSnapshot = { layout, selectedObjectId };
    activeObjectEditSnapshot = null;

    const nextHistory = finishFurnitureGestureHistory(history, startSnapshot, currentSnapshot);
    if (nextHistory !== history) {
      history = nextHistory;
      scheduleSave(layout);
    }
  }

  function handleAddCatalogItem(item: FurnitureCatalogItem) {
    if (!layout) {
      return;
    }

    const nextLayout = addCatalogItem(layout, item, currentViewportCenter ?? { x: 7.5, y: 5.2 });
    const nextSelectedObjectId = nextLayout.objects[nextLayout.objects.length - 1]?.id ?? selectedObjectId;
    commitLayout(nextLayout, nextSelectedObjectId);
  }

  function handleMoveObject(objectId: string, point: PlanPoint) {
    if (layout) {
      applyObjectEditLayout(moveObject(layout, objectId, point));
    }
  }

  function handleResizeObject(objectId: string, size: FurnitureSize, point?: PlanPoint) {
    if (layout) {
      const resizedLayout = resizeObject(layout, objectId, size);
      applyObjectEditLayout(point ? moveObject(resizedLayout, objectId, point) : resizedLayout);
    }
  }

  function handleRotateObject(objectId: string, rotationDeg: number) {
    if (layout) {
      applyObjectEditLayout(rotateObject(layout, objectId, rotationDeg));
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

  function handleReorderObject(objectId: string, action: FurnitureOrderAction) {
    if (layout) {
      const nextLayout = reorderObject(layout, objectId, action);
      if (nextLayout !== layout) {
        commitLayout(nextLayout);
      }
    }
  }

  function handleDuplicateObject(objectId: string) {
    if (!layout) {
      return;
    }

    const nextLayout = duplicateObject(layout, objectId);
    const nextSelectedObjectId = nextLayout.objects[nextLayout.objects.length - 1]?.id ?? selectedObjectId;
    commitLayout(nextLayout, nextSelectedObjectId);
  }

  function handleDeleteObject(objectId: string) {
    if (layout) {
      commitLayout(deleteObject(layout, objectId), null);
    }
  }

  function undoLayout() {
    const currentSnapshot = currentHistorySnapshot();
    if (!currentSnapshot) {
      return;
    }

    const result = undoFurnitureHistory(history, currentSnapshot);
    if (!result) {
      return;
    }

    history = result.history;
    restoreHistorySnapshot(result.snapshot);
  }

  function redoLayout() {
    const currentSnapshot = currentHistorySnapshot();
    if (!currentSnapshot) {
      return;
    }

    const result = redoFurnitureHistory(history, currentSnapshot);
    if (!result) {
      return;
    }

    history = result.history;
    restoreHistorySnapshot(result.snapshot);
  }

  function isEditableKeyboardTarget(target: EventTarget | null): boolean {
    return target instanceof Element
      ? Boolean(target.closest("input, textarea, select, [contenteditable='true']"))
      : false;
  }

  function isUndoKeyboardShortcut(event: KeyboardEvent): boolean {
    return (event.ctrlKey || event.metaKey) && !event.shiftKey && event.key.toLowerCase() === "z";
  }

  function isRedoKeyboardShortcut(event: KeyboardEvent): boolean {
    const key = event.key.toLowerCase();
    return (event.ctrlKey || event.metaKey) && ((event.shiftKey && key === "z") || key === "y");
  }

  function handleEditorKeyDown(event: KeyboardEvent) {
    if (isEditableKeyboardTarget(event.target)) {
      return;
    }

    if (isUndoKeyboardShortcut(event)) {
      event.preventDefault();
      undoLayout();
      return;
    }

    if (isRedoKeyboardShortcut(event)) {
      event.preventDefault();
      redoLayout();
      return;
    }

    if (!selectedObjectId || (event.key !== "Delete" && event.key !== "Backspace")) {
      return;
    }

    event.preventDefault();
    handleDeleteObject(selectedObjectId);
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
        history = { undoStack: [], redoStack: [] };
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

<svelte:window onkeydown={handleEditorKeyDown} />

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
      <div class="editor-history-controls" aria-label="Furniture edit history controls">
        <button
          type="button"
          aria-label="Undo"
          title={`Undo (${history.undoStack.length}/${FURNITURE_HISTORY_LIMIT})`}
          disabled={history.undoStack.length === 0}
          onclick={undoLayout}
        >
          Undo
        </button>
        <button
          type="button"
          aria-label="Redo"
          title={`Redo (${history.redoStack.length}/${FURNITURE_HISTORY_LIMIT})`}
          disabled={history.redoStack.length === 0}
          onclick={redoLayout}
        >
          Redo
        </button>
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
          onBeginObjectEdit={handleBeginObjectEdit}
          onFinishObjectEdit={handleFinishObjectEdit}
          onMoveObject={handleMoveObject}
          onResizeObject={handleResizeObject}
          onRotateObject={handleRotateObject}
          onZoomChange={handlePlanZoom}
          onResizePreview={handleResizePreview}
          onViewportCenterChange={(point) => (currentViewportCenter = point)}
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
        onReorder={handleReorderObject}
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
    height: 100%;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
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

  .editor-history-controls {
    display: grid;
    grid-template-columns: repeat(2, minmax(58px, auto));
    gap: 6px;
    align-items: center;
    min-width: 0;
    padding: 4px;
    background: #ffffff;
    border: 1px solid #d4dde1;
    border-radius: 8px;
  }

  .editor-zoom-controls button,
  .editor-history-controls button {
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
  .editor-zoom-controls button:focus-visible,
  .editor-history-controls button:hover,
  .editor-history-controls button:focus-visible {
    background: #e9f4f1;
    border-color: #8fcabd;
    outline: none;
  }

  .editor-history-controls button:disabled {
    color: #8a999f;
    cursor: not-allowed;
    background: #f1f4f5;
    border-color: #d8e0e3;
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
