<script lang="ts">
  import { onMount } from "svelte";
  import BaseView from "./BaseView.svelte";
  import DesignReviewView from "./DesignReviewView.svelte";
  import FurnitureEditorView from "./FurnitureEditorView.svelte";
  import ThreeDNavigationView from "./ThreeDNavigationView.svelte";
  import { withCheckedViewAvailability } from "./lib/assetAvailability";
  import { basePlanBackgroundAssetPath } from "./lib/basePlanView";
  import { sortedScenarios } from "./lib/designScenarios";
  import {
    getAppStatus,
    loadBuiltinModelStatus,
    loadBuiltinProject,
  } from "./lib/homeDesignCommands";
  import {
    navigationMessageForKeyEvent,
    type ThreeDNavigationKeyEventKind,
  } from "./lib/keyboardForwarding";
  import {
    activeScenario,
    activeView,
    selectAvailableScenarioView,
  } from "./lib/viewState";
  import type {
    AppStatus,
    BuiltInModelStatus,
    DesignScenarioDescriptor,
    ProjectManifest,
  } from "./types";

  const fallbackStatus: AppStatus = {
    app_name: "Home Design",
    runtime: "tauri-desktop",
    built_in_project_count: 0,
  };

  let status = $state<AppStatus>(fallbackStatus);
  let project = $state<ProjectManifest | null>(null);
  let modelStatus = $state<BuiltInModelStatus | null>(null);
  let modelStatusError = $state<string | null>(null);
  let selectedScenarioId = $state<string | null>(null);
  let selectedViewId = $state<string | null>(null);
  let collapsedScenarioIds = $state<Set<string>>(new Set());
  let viewActivationKey = $state(0);
  let activeFrame = $state<HTMLIFrameElement | null>(null);
  let loading = $state(true);
  let appError = $state<string | null>(null);

  let orderedScenarios = $derived(project ? sortedScenarios(project) : []);
  let selectedScenario = $derived(activeScenario(project, selectedScenarioId));
  let selectedView = $derived(activeView(project, selectedViewId));
  let measurementAudit = $derived(modelStatus?.summary.measurement_audit ?? null);
  let selectedViewDisplayPath = $derived(
    selectedView?.mode === "three_d_navigation" || selectedView?.mode === "design_review"
      ? "Native renderer"
      : selectedView?.mode === "base_plan" && project
        ? basePlanBackgroundAssetPath(project)
      : selectedView?.asset_path,
  );

  function toErrorMessage(reason: unknown): string {
    return reason instanceof Error ? reason.message : String(reason);
  }

  function initialiseSelectedView(loadedProject: ProjectManifest) {
    const selection = selectAvailableScenarioView(loadedProject, "current", "base-view");
    selectedScenarioId = selection?.scenarioId ?? null;
    selectedViewId = selection?.viewId ?? null;
    collapsedScenarioIds = new Set(
      loadedProject.scenarios
        .filter((scenario) => scenario.id !== selectedScenarioId)
        .map((scenario) => scenario.id),
    );
  }

  function expandScenario(scenarioId: string) {
    const nextCollapsed = new Set(collapsedScenarioIds);
    nextCollapsed.delete(scenarioId);
    collapsedScenarioIds = nextCollapsed;
  }

  function toggleScenario(scenarioId: string) {
    const nextCollapsed = new Set(collapsedScenarioIds);
    if (nextCollapsed.has(scenarioId)) {
      nextCollapsed.delete(scenarioId);
    } else {
      nextCollapsed.add(scenarioId);
    }
    collapsedScenarioIds = nextCollapsed;
  }

  function isScenarioCollapsed(scenarioId: string): boolean {
    return collapsedScenarioIds.has(scenarioId);
  }

  function scenarioDisplayName(scenario: DesignScenarioDescriptor): string {
    const prefix = `${scenario.short_label} - `;
    return scenario.label.startsWith(prefix) ? scenario.label.slice(prefix.length) : scenario.label;
  }

  function handleSelectScenarioView(scenarioId: string, viewId: string) {
    if (!project) {
      return;
    }
    const selection = selectAvailableScenarioView(project, scenarioId, viewId);
    selectedScenarioId = selection?.scenarioId ?? null;
    selectedViewId = selection?.viewId ?? null;
    viewActivationKey += 1;
    if (selection) {
      expandScenario(selection.scenarioId);
    }
  }

  function isEditableTarget(target: EventTarget | null): boolean {
    return target instanceof HTMLElement
      && Boolean(target.closest("input, textarea, select, [contenteditable='true']"));
  }

  function forward3DNavigationKey(kind: ThreeDNavigationKeyEventKind, event: KeyboardEvent) {
    if (
      selectedView?.mode !== "three_d_navigation"
      || selectedViewDisplayPath === "Native renderer"
      || !activeFrame
      || isEditableTarget(event.target)
    ) {
      return;
    }

    const message = navigationMessageForKeyEvent(kind, event);
    if (!message) {
      return;
    }

    event.preventDefault();
    activeFrame?.contentWindow?.postMessage(message, "*");
  }

  onMount(async () => {
    loading = true;
    appError = null;
    try {
      status = await getAppStatus();
      project = await withCheckedViewAvailability(await loadBuiltinProject());
      initialiseSelectedView(project);
      try {
        modelStatus = await loadBuiltinModelStatus();
      } catch (reason: unknown) {
        modelStatusError = toErrorMessage(reason);
      }
    } catch (reason: unknown) {
      appError = `Could not load Home Design: ${toErrorMessage(reason)}`;
    } finally {
      loading = false;
    }
  });
</script>

<svelte:window
  onkeydown={(event) => forward3DNavigationKey("keydown", event)}
  onkeyup={(event) => forward3DNavigationKey("keyup", event)}
/>

<main class="app-shell">
  <aside class="sidebar" aria-label="Project navigation">
    <div class="brand">
      <h1>Home Design</h1>
      <p>{status.runtime}</p>
    </div>

    {#if project}
      <section class="project-summary" aria-label="Current project">
        <span class="eyebrow">Project</span>
        <h2>{project.name}</h2>
        <p>{project.model_source}</p>
      </section>

      {#if modelStatus}
        <section class="model-summary" aria-label="Model validation status">
          <span class="eyebrow">Model</span>
          <div class="model-state">
            <strong class:invalid={!modelStatus.valid}>
              {modelStatus.valid ? "Validated" : "Needs review"}
            </strong>
            <span>
              {modelStatus.validation_error_count + modelStatus.validation_warning_count} issues
            </span>
          </div>
          <dl>
            <div>
              <dt>Rooms</dt>
              <dd>{modelStatus.summary.room_count}</dd>
            </div>
            <div>
              <dt>Features</dt>
              <dd>{modelStatus.summary.current_feature_count}</dd>
            </div>
            <div>
              <dt>Site</dt>
              <dd>{modelStatus.summary.site_element_count}</dd>
            </div>
          </dl>
        </section>
        {#if measurementAudit}
          <section class="audit-summary" aria-label="Measurement audit status">
            <span class="eyebrow">Measurements</span>
            <div class="audit-state">
              <strong>{measurementAudit.measured_count} measured</strong>
              <span>{measurementAudit.total_count} records</span>
            </div>
            <dl>
              <div>
                <dt>Partial</dt>
                <dd>{measurementAudit.partly_measured_count}</dd>
              </div>
              <div>
                <dt>Estimated</dt>
                <dd>{measurementAudit.estimated_count}</dd>
              </div>
              <div>
                <dt>Check</dt>
                <dd>{measurementAudit.needs_checking_count}</dd>
              </div>
            </dl>
          </section>
        {/if}
      {:else if modelStatusError}
        <section class="model-summary warning" aria-label="Model validation status">
          <span class="eyebrow">Model</span>
          <strong>Unavailable</strong>
          <p>{modelStatusError}</p>
        </section>
      {/if}

      <nav class="design-navigation" aria-label="Design scenarios and views">
        {#each orderedScenarios as scenario}
          <section
            class="design-group"
            class:active={selectedScenarioId === scenario.id}
            aria-label={scenario.label}
          >
            <button
              type="button"
              class="design-group-heading"
              aria-expanded={!isScenarioCollapsed(scenario.id)}
              onclick={() => toggleScenario(scenario.id)}
            >
              <span>
                <strong>{scenario.short_label}</strong>
                <small>{scenarioDisplayName(scenario)}</small>
              </span>
              <span class="design-group-meta">
                {#if !scenario.complete}
                  <small>Draft</small>
                {/if}
                <span aria-hidden="true">{isScenarioCollapsed(scenario.id) ? "+" : "-"}</span>
              </span>
            </button>

            {#if !isScenarioCollapsed(scenario.id)}
              <div class="view-tabs">
                {#each project.views as view}
                  <button
                    type="button"
                    class:selected={selectedScenarioId === scenario.id && selectedViewId === view.id}
                    disabled={!view.available}
                    onclick={() => handleSelectScenarioView(scenario.id, view.id)}
                  >
                    <span>{view.label}</span>
                    {#if !view.available}
                      <small>Unavailable</small>
                    {/if}
                  </button>
                {/each}
              </div>
            {/if}
          </section>
        {/each}
      </nav>
    {/if}
  </aside>

  <section class="workspace" aria-label="Home design workspace">
    {#if loading}
      <div class="state-panel">Loading Home Design...</div>
    {:else if appError}
      <div class="state-panel error">{appError}</div>
    {:else if selectedView && selectedScenario}
      <header class="workspace-header">
        <div>
          <span class="eyebrow">Explorer</span>
          <h2>{selectedScenario.label}</h2>
          <p class="workspace-subtitle">{selectedView.label}</p>
        </div>
        <span class="asset-path">{selectedViewDisplayPath}</span>
      </header>
      {#if selectedView.mode === "furniture_editor" && project}
        <FurnitureEditorView projectId={project.id} scenarioId={selectedScenario.id} backgroundAssetPath={selectedView.asset_path} />
      {:else if selectedView.mode === "base_plan" && project}
        <BaseView projectId={project.id} scenarioId={selectedScenario.id} resetKey={viewActivationKey} backgroundAssetPath={basePlanBackgroundAssetPath(project)} />
      {:else if selectedView.mode === "design_review" && project}
        <DesignReviewView projectId={project.id} scenarioId={selectedScenario.id} />
      {:else if selectedView.mode === "three_d_navigation" && project}
        <ThreeDNavigationView projectId={project.id} scenarioId={selectedScenario.id} />
      {:else}
        <div class="view-frame">
          <iframe
            bind:this={activeFrame}
            title={selectedView.label}
            src={selectedView.asset_path}
            sandbox="allow-scripts allow-same-origin allow-pointer-lock allow-forms"
          ></iframe>
        </div>
      {/if}
    {:else}
      <div class="state-panel error">No packaged views are available.</div>
    {/if}
  </section>
</main>
