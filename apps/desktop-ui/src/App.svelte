<script lang="ts">
  import { onMount } from "svelte";
  import { withCheckedViewAvailability } from "./lib/assetAvailability";
  import { getAppStatus, loadBuiltinProject } from "./lib/homeDesignCommands";
  import { activeView, selectAvailableView } from "./lib/viewState";
  import type { AppStatus, ProjectManifest } from "./types";

  const fallbackStatus: AppStatus = {
    app_name: "Home Design",
    runtime: "tauri-desktop",
    built_in_project_count: 0,
  };

  let status = $state<AppStatus>(fallbackStatus);
  let project = $state<ProjectManifest | null>(null);
  let selectedViewId = $state<string | null>(null);
  let loading = $state(true);
  let appError = $state<string | null>(null);

  let selectedView = $derived(activeView(project, selectedViewId));

  function toErrorMessage(reason: unknown): string {
    return reason instanceof Error ? reason.message : String(reason);
  }

  function handleSelectView(viewId: string) {
    if (!project) {
      return;
    }
    selectedViewId = selectAvailableView(project, viewId);
  }

  onMount(async () => {
    loading = true;
    appError = null;
    try {
      status = await getAppStatus();
      project = await withCheckedViewAvailability(await loadBuiltinProject());
      selectedViewId = selectAvailableView(project, "base-view");
    } catch (reason: unknown) {
      appError = `Could not load Home Design: ${toErrorMessage(reason)}`;
    } finally {
      loading = false;
    }
  });
</script>

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

      <nav class="view-tabs" aria-label="View modes">
        {#each project.views as view}
          <button
            type="button"
            class:selected={selectedViewId === view.id}
            disabled={!view.available}
            onclick={() => handleSelectView(view.id)}
          >
            <span>{view.label}</span>
            {#if !view.available}
              <small>Unavailable</small>
            {/if}
          </button>
        {/each}
      </nav>
    {/if}
  </aside>

  <section class="workspace" aria-label="Home design workspace">
    {#if loading}
      <div class="state-panel">Loading Home Design...</div>
    {:else if appError}
      <div class="state-panel error">{appError}</div>
    {:else if selectedView}
      <header class="workspace-header">
        <div>
          <span class="eyebrow">Explorer</span>
          <h2>{selectedView.label}</h2>
        </div>
        <span class="asset-path">{selectedView.asset_path}</span>
      </header>
      <div class="view-frame">
        <iframe
          title={selectedView.label}
          src={selectedView.asset_path}
          sandbox="allow-scripts allow-same-origin allow-pointer-lock allow-forms"
        ></iframe>
      </div>
    {:else}
      <div class="state-panel error">No packaged views are available.</div>
    {/if}
  </section>
</main>
