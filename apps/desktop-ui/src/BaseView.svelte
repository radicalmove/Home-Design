<script lang="ts">
  import { onDestroy, untrack } from "svelte";
  import FurnitureLayerControls from "./FurnitureLayerControls.svelte";
  import PlanCanvas from "./PlanCanvas.svelte";
  import { CURRENT_SCENARIO_ID } from "./lib/designScenarios";
  import {
    DESIGN_TRANSITION_DURATION_MS,
    interpolateFurnitureLayouts,
    transitionPercentLabel,
    transitionProgressAt,
  } from "./lib/designTransitions";
  import {
    FURNITURE_REUSE_CATEGORY_LABELS,
    designScenarioConceptById,
    type DesignScenarioFurnitureReuse,
  } from "./lib/designScenarioConcepts";
  import { buildDesignSanityChecks } from "./lib/designSanityChecks";
  import { clampPlanZoom, planZoomLabel } from "./lib/furnitureGeometry";
  import { loadFurnitureLayout } from "./lib/homeDesignCommands";
  import { normaliseFurnitureLayout } from "./lib/furnitureState";
  import {
    SUNLIGHT_TIME_SLIDER,
    SUNLIGHT_YEAR_POINTS,
    formatSunlightMinutes,
    sunlightYearPointAt,
  } from "./lib/sunlight";
  import type { FurnitureLayout, FurnitureLayoutLoadResult, PlanPoint } from "./types";

  type Props = {
    projectId: string;
    scenarioId: string;
    resetKey: number;
    backgroundAssetPath: string;
  };

  let { projectId, scenarioId, resetKey, backgroundAssetPath }: Props = $props();

  let layout = $state<FurnitureLayout | null>(null);
  let layoutSource = $state<FurnitureLayoutLoadResult["source"] | null>(null);
  let transitionBaseLayout = $state<FurnitureLayout | null>(null);
  let fixedVisible = $state(false);
  let moveableVisible = $state(false);
  let labelsVisible = $state(false);
  let roomLabelsVisible = $state(false);
  let sunlightVisible = $state(false);
  let sunlightYearIndex = $state(0);
  let sunlightTimeMinutes = $state(720);
  let planZoom = $state(1);
  let loading = $state(true);
  let loadError = $state<string | null>(null);
  let transitionProgress = $state(0);
  let transitionAnimationFrame = $state<number | null>(null);
  let transitionStartedAt = $state<number | null>(null);
  let reusePanelExpanded = $state(false);
  let checksPanelExpanded = $state(false);

  let showTransitionControl = $derived(scenarioId !== CURRENT_SCENARIO_ID);
  let scenarioConcept = $derived(designScenarioConceptById(scenarioId));
  let scenarioFurnitureReuse = $derived(scenarioConcept?.furniture_reuse ?? []);
  let sunlightYearLabel = $derived(sunlightYearPointAt(sunlightYearIndex).label);
  let sunlightTimeLabel = $derived(formatSunlightMinutes(sunlightTimeMinutes));
  let scenarioDesignChecks = $derived(
    layout ? buildDesignSanityChecks({ scenarioId, layout, layoutSource }) : [],
  );
  let scenarioStructuralProgress = $derived(
    showTransitionControl ? (transitionStartedAt === null ? 1 : transitionProgress) : 0,
  );
  let displayedLayout = $derived(
    layout && transitionBaseLayout && transitionStartedAt !== null
      ? interpolateFurnitureLayouts(transitionBaseLayout, layout, transitionProgress, { stagger: true })
      : layout,
  );

  function toErrorMessage(reason: unknown): string {
    return reason instanceof Error ? reason.message : String(reason);
  }

  function furnitureReuseLabel(entry: DesignScenarioFurnitureReuse): string {
    return FURNITURE_REUSE_CATEGORY_LABELS[entry.category];
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

  function handleSunlightYearInput(event: Event) {
    sunlightYearIndex = Number((event.currentTarget as HTMLInputElement).value);
  }

  function handleSunlightTimeInput(event: Event) {
    sunlightTimeMinutes = Number((event.currentTarget as HTMLInputElement).value);
  }

  function ignoreViewportCenter(_point: PlanPoint) {
  }

  function stopTransitionAnimation() {
    if (transitionAnimationFrame !== null) {
      cancelAnimationFrame(transitionAnimationFrame);
      transitionAnimationFrame = null;
    }
  }

  function updateTransitionProgress(timestamp: number) {
    if (transitionStartedAt === null) {
      return;
    }

    transitionProgress = transitionProgressAt(
      timestamp - transitionStartedAt,
      DESIGN_TRANSITION_DURATION_MS,
    );

    if (transitionProgress < 1) {
      transitionAnimationFrame = requestAnimationFrame(updateTransitionProgress);
    } else {
      transitionAnimationFrame = null;
    }
  }

  function startTransitionAnimation() {
    stopTransitionAnimation();
    transitionStartedAt = performance.now();
    transitionProgress = 0;
    transitionAnimationFrame = requestAnimationFrame(updateTransitionProgress);
  }

  $effect(() => {
    projectId;
    scenarioId;
    let cancelled = false;

    async function loadData() {
      loading = true;
      loadError = null;
      try {
        const [result, baselineResult] = await Promise.all([
          loadFurnitureLayout(projectId, scenarioId),
          scenarioId !== CURRENT_SCENARIO_ID
            ? loadFurnitureLayout(projectId, CURRENT_SCENARIO_ID)
            : Promise.resolve(null),
        ]);
        if (!cancelled) {
          layout = normaliseFurnitureLayout(result.layout);
          layoutSource = result.source;
          transitionBaseLayout = baselineResult
            ? normaliseFurnitureLayout(baselineResult.layout)
            : null;
        }
      } catch (reason: unknown) {
        if (!cancelled) {
          layoutSource = null;
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
    };
  });

  $effect(() => {
    scenarioId;
    resetKey;
    untrack(() => stopTransitionAnimation());
    transitionStartedAt = null;
    transitionProgress = 0;
    reusePanelExpanded = false;
    checksPanelExpanded = false;
  });

  $effect(() => {
    resetKey;
    planZoom = 1;
  });

  onDestroy(() => {
    stopTransitionAnimation();
  });
</script>

{#if loading}
  <div class="state-panel">Loading base view...</div>
{:else if loadError}
  <div class="state-panel error">{loadError}</div>
{:else if displayedLayout}
  <section class="base-view" aria-label="Base view with furniture overlays">
    <div class="base-view-toolbar">
      <div class="base-view-toolbar-row">
        <div class="base-layer-controls" aria-label="Base view furniture overlays">
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
          {#if showTransitionControl}
            <button
              type="button"
              class="base-transition-button"
              class:active={transitionProgress > 0 && transitionProgress < 1}
              onclick={startTransitionAnimation}
            >
              Show transition from Design 1
            </button>
          {/if}
        </div>

        <div class="base-zoom-controls" aria-label="Base plan zoom controls">
          <button type="button" aria-label="Zoom out" onclick={() => zoomPlan(-0.1)}>-</button>
          <span>{planZoomLabel(planZoom)}</span>
          <button type="button" aria-label="Zoom in" onclick={() => zoomPlan(0.1)}>+</button>
          <button type="button" onclick={resetPlanZoom}>Reset</button>
        </div>
      </div>

      <div class="base-sunlight-controls" aria-label="2D Plan sunlight controls">
        <label class="base-sunlight-toggle">
          <input
            type="checkbox"
            checked={sunlightVisible}
            onchange={() => (sunlightVisible = !sunlightVisible)}
          />
          <span>Sunlight</span>
        </label>
        <label class="base-sunlight-range">
          <span>Year</span>
          <input
            type="range"
            min="0"
            max={SUNLIGHT_YEAR_POINTS.length - 1}
            step="1"
            value={sunlightYearIndex}
            disabled={!sunlightVisible}
            oninput={handleSunlightYearInput}
          />
          <strong>{sunlightYearLabel}</strong>
        </label>
        <label class="base-sunlight-range">
          <span>Time</span>
          <input
            type="range"
            min={SUNLIGHT_TIME_SLIDER.startMinutes}
            max={SUNLIGHT_TIME_SLIDER.endMinutes}
            step={SUNLIGHT_TIME_SLIDER.stepMinutes}
            value={sunlightTimeMinutes}
            disabled={!sunlightVisible}
            oninput={handleSunlightTimeInput}
          />
          <strong>{sunlightTimeLabel}</strong>
        </label>
      </div>
    </div>

    {#if showTransitionControl}
      <div class="scenario-plan-controls" aria-label="Future design review controls">
        {#if scenarioFurnitureReuse.length > 0}
          <div class="scenario-reuse-control">
            <button
              type="button"
              class="scenario-reuse-toggle"
              aria-expanded={reusePanelExpanded}
              onclick={() => (reusePanelExpanded = !reusePanelExpanded)}
            >
              Furniture reuse
              <span aria-hidden="true">{reusePanelExpanded ? "-" : "+"}</span>
            </button>

            {#if reusePanelExpanded}
              <aside class="scenario-reuse-overlay" aria-label="Furniture reuse plan">
                <div>
                  <span>Furniture reuse plan</span>
                  <strong>{scenarioConcept?.label ?? "Future design"}</strong>
                </div>
                <ul>
                  {#each scenarioFurnitureReuse.slice(0, 5) as entry}
                    <li class={entry.category}>
                      <span>{furnitureReuseLabel(entry)}</span>
                      <p>{entry.item}</p>
                    </li>
                  {/each}
                </ul>
              </aside>
            {/if}
          </div>
        {/if}

        <div class="scenario-checks-control">
          <button
            type="button"
            class="scenario-checks-toggle"
            aria-expanded={checksPanelExpanded}
            onclick={() => (checksPanelExpanded = !checksPanelExpanded)}
          >
            Design checks
            <span aria-hidden="true">{scenarioDesignChecks.length}</span>
            <span aria-hidden="true">{checksPanelExpanded ? "-" : "+"}</span>
          </button>

          {#if checksPanelExpanded}
            <aside class="scenario-checks-overlay" aria-label="Design checks">
              <div>
                <span>Design checks</span>
                <strong>
                  {scenarioDesignChecks.length === 0
                    ? "No checks flagged"
                    : `${scenarioDesignChecks.length} checks flagged`}
                </strong>
              </div>
              {#if scenarioDesignChecks.length === 0}
                <p>No checks flagged for the current scenario layout.</p>
              {:else}
                <ul>
                  {#each scenarioDesignChecks.slice(0, 6) as check}
                    <li class={check.severity}>
                      <span>{check.severity}</span>
                      <strong>{check.title}</strong>
                      {#each check.details as detail}
                        <p>{detail}</p>
                      {/each}
                    </li>
                  {/each}
                </ul>
              {/if}
            </aside>
          {/if}
        </div>
      </div>
    {/if}

    <div class="base-plan-shell">
      <PlanCanvas
        layout={displayedLayout}
        {backgroundAssetPath}
        selectedObjectId={null}
        fixedVisible={fixedVisible}
        moveableVisible={moveableVisible}
        showLabels={labelsVisible}
        showRoomLabels={roomLabelsVisible}
        showSunlight={sunlightVisible}
        sunlightYearIndex={sunlightYearIndex}
        sunlightTimeMinutes={sunlightTimeMinutes}
        zoom={planZoom}
        structuralTransitionProgress={scenarioStructuralProgress}
        structuralTransitionScenarioId={scenarioId}
        initialCenterMode="visible"
        resetKey={resetKey}
        readOnly={true}
        onSelectObject={() => {}}
        onMoveObject={() => {}}
        onResizeObject={() => {}}
        onRotateObject={() => {}}
        onZoomChange={handlePlanZoom}
        onResizePreview={() => {}}
        onViewportCenterChange={ignoreViewportCenter}
        onBeginObjectEdit={() => {}}
        onFinishObjectEdit={() => {}}
      />
      {#if showTransitionControl && transitionProgress > 0}
        <div class="base-transition-status" aria-label="Design transition progress">
          <span>Transition {transitionPercentLabel(transitionProgress)}</span>
          <div class="base-transition-track">
            <div style={`width: ${transitionPercentLabel(transitionProgress)}`}></div>
          </div>
        </div>
      {/if}
    </div>
  </section>
{:else}
  <div class="state-panel error">Base view data is unavailable.</div>
{/if}

<style>
  .base-view {
    display: grid;
    gap: 12px;
    min-height: 0;
  }

  .base-view-toolbar {
    display: grid;
    gap: 10px;
  }

  .base-view-toolbar-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .base-layer-controls,
  .base-zoom-controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }

  .base-transition-button,
  .base-sunlight-toggle,
  .base-zoom-controls button {
    border: 1px solid #c7d4da;
    border-radius: 6px;
    background: #ffffff;
    color: #26353a;
    font: inherit;
    font-weight: 700;
    min-height: 36px;
    padding: 0 12px;
  }

  .base-sunlight-controls {
    display: grid;
    grid-template-columns: auto minmax(220px, 360px) minmax(220px, 360px);
    align-items: center;
    gap: 8px 12px;
    width: min(100%, 860px);
    padding: 4px;
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid #d3dde1;
    border-radius: 8px;
  }

  .base-sunlight-toggle {
    display: inline-flex;
    align-items: center;
    gap: 7px;
  }

  .base-sunlight-toggle input {
    width: 14px;
    height: 14px;
    margin: 0;
    accent-color: #d79222;
  }

  .base-sunlight-range {
    display: grid;
    grid-template-columns: auto minmax(220px, 360px) minmax(86px, auto);
    align-items: center;
    gap: 6px;
    min-height: 30px;
    color: #44565c;
    font-size: 0.76rem;
    font-weight: 800;
  }

  .base-sunlight-range input {
    width: 100%;
    min-width: 220px;
    accent-color: #d79222;
  }

  .base-sunlight-range input:disabled {
    opacity: 0.45;
  }

  .base-sunlight-range strong {
    color: #26353a;
    font-size: 0.76rem;
    white-space: nowrap;
  }

  @media (max-width: 980px) {
    .base-sunlight-controls {
      grid-template-columns: 1fr;
      width: 100%;
    }

    .base-sunlight-range {
      grid-template-columns: auto minmax(160px, 1fr) minmax(86px, auto);
    }

    .base-sunlight-range input {
      min-width: 160px;
    }
  }

  .base-transition-button.active {
    border-color: #6dbca9;
    background: #8bd2c2;
    color: #1d3536;
  }

  .base-zoom-controls span {
    min-width: 62px;
    text-align: center;
    font-weight: 800;
    color: #26353a;
  }

  .base-plan-shell {
    position: relative;
    min-width: 0;
    min-height: 0;
  }

  .base-transition-status {
    position: absolute;
    right: 14px;
    bottom: 14px;
    display: grid;
    gap: 7px;
    min-width: 210px;
    padding: 10px 12px;
    color: #1f3239;
    font-size: 0.82rem;
    font-weight: 760;
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid #c8d5da;
    border-radius: 8px;
    box-shadow: 0 10px 28px rgba(42, 58, 66, 0.18);
  }

  .base-transition-track {
    height: 8px;
    overflow: hidden;
    background: #dfe8eb;
    border-radius: 999px;
  }

  .base-transition-track div {
    height: 100%;
    background: #67b8a6;
  }

  .scenario-plan-controls {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }

  .scenario-reuse-control,
  .scenario-checks-control {
    display: grid;
    gap: 8px;
    max-width: min(340px, 100%);
  }

  .scenario-reuse-toggle,
  .scenario-checks-toggle {
    justify-self: start;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    min-height: 32px;
    padding: 0 10px;
    color: #203239;
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid #c8d5da;
    border-radius: 8px;
    box-shadow: 0 8px 22px rgba(42, 58, 66, 0.14);
    font: inherit;
    font-size: 0.78rem;
    font-weight: 850;
  }

  .scenario-reuse-toggle span,
  .scenario-checks-toggle span {
    color: #36786b;
    font-size: 1rem;
    line-height: 1;
  }

  .scenario-checks-toggle span:first-of-type {
    min-width: 18px;
    color: #1f3239;
    font-size: 0.74rem;
    text-align: center;
  }

  .scenario-reuse-overlay,
  .scenario-checks-overlay {
    display: grid;
    gap: 8px;
    max-height: 360px;
    overflow: auto;
    padding: 12px;
    color: #203239;
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid #c8d5da;
    border-radius: 8px;
    box-shadow: 0 10px 28px rgba(42, 58, 66, 0.18);
  }

  .scenario-reuse-overlay > div,
  .scenario-checks-overlay > div {
    display: grid;
    gap: 2px;
  }

  .scenario-reuse-overlay > div span,
  .scenario-reuse-overlay li span,
  .scenario-checks-overlay > div span,
  .scenario-checks-overlay li span {
    color: #36786b;
    font-size: 0.68rem;
    font-weight: 900;
    letter-spacing: 0;
    text-transform: uppercase;
  }

  .scenario-reuse-overlay > div strong,
  .scenario-checks-overlay > div strong,
  .scenario-checks-overlay li strong {
    color: #1f3239;
    font-size: 0.9rem;
    line-height: 1.2;
  }

  .scenario-reuse-overlay ul,
  .scenario-checks-overlay ul {
    display: grid;
    gap: 6px;
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .scenario-reuse-overlay li,
  .scenario-checks-overlay li {
    display: grid;
    gap: 2px;
    padding-left: 9px;
    border-left: 4px solid #9fb0b7;
  }

  .scenario-reuse-overlay li.reuse_in_place {
    border-left-color: #6dbca9;
  }

  .scenario-reuse-overlay li.reuse_relocated {
    border-left-color: #5a88bf;
  }

  .scenario-reuse-overlay li.modify_reuse {
    border-left-color: #c08a3c;
  }

  .scenario-reuse-overlay li.new_required {
    border-left-color: #a85f70;
  }

  .scenario-reuse-overlay li.remove_store_sell {
    border-left-color: #68757a;
  }

  .scenario-checks-overlay li.warning {
    border-left-color: #c08a3c;
  }

  .scenario-checks-overlay li.info {
    border-left-color: #5a88bf;
  }

  .scenario-reuse-overlay p,
  .scenario-checks-overlay p {
    margin: 0;
    color: #24363c;
    font-size: 0.78rem;
    font-weight: 760;
    line-height: 1.25;
  }
</style>
