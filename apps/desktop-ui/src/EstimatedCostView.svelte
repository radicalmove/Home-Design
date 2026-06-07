<script lang="ts">
  import { buildEstimatedCostAnalysis, formatEstimatedCostRange } from "./lib/estimatedCosts";
  import { loadDesignReviewData } from "./lib/homeDesignCommands";
  import type { EstimatedCostAnalysis } from "./lib/estimatedCosts";
  import type { DesignReviewData } from "./types";

  type Props = {
    projectId: string;
    scenarioId: string;
  };

  let { projectId, scenarioId }: Props = $props();

  let reviewData = $state<DesignReviewData | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let refreshedAt = $state<string | null>(null);
  let latestRefreshRequest = 0;

  let analysis = $derived<EstimatedCostAnalysis | null>(
    reviewData ? buildEstimatedCostAnalysis(reviewData) : null,
  );

  function toErrorMessage(reason: unknown): string {
    return reason instanceof Error ? reason.message : String(reason);
  }

  function formatMoney(value: number): string {
    return `NZD ${Math.round(value / 1_000)}k`;
  }

  async function refreshEstimate() {
    const refreshRequest = latestRefreshRequest + 1;
    latestRefreshRequest = refreshRequest;
    loading = true;
    error = null;
    try {
      const data = await loadDesignReviewData(projectId, scenarioId);
      if (refreshRequest !== latestRefreshRequest) {
        return;
      }
      reviewData = data;
      refreshedAt = new Intl.DateTimeFormat(undefined, {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }).format(new Date());
    } catch (reason: unknown) {
      if (refreshRequest === latestRefreshRequest) {
        error = toErrorMessage(reason);
      }
    } finally {
      if (refreshRequest === latestRefreshRequest) {
        loading = false;
      }
    }
  }

  $effect(() => {
    projectId;
    scenarioId;
    void refreshEstimate();
  });
</script>

{#if loading && !analysis}
  <div class="state-panel">Loading estimated cost...</div>
{:else if error && !analysis}
  <div class="state-panel error">{error}</div>
{:else if analysis}
  <section class="estimated-cost" aria-label="Estimated cost breakdown">
    <header class="cost-hero">
      <div>
        <span class="eyebrow">Estimated Cost</span>
        <h3>{analysis.title}</h3>
        <p>{analysis.summary}</p>
      </div>
      <div class="cost-actions">
        <button type="button" onclick={refreshEstimate}>Refresh Estimate</button>
        <span>
          {reviewData?.furniture_layout.source === "saved" ? "Saved furniture layout" : "Seed furniture layout"}
          {#if refreshedAt}
            <small>Refreshed {refreshedAt}</small>
          {/if}
        </span>
      </div>
    </header>

    {#if error}
      <p class="inline-error">{error}</p>
    {/if}

    <section class="cost-summary" aria-label="Planning Range">
      <article>
        <span class="eyebrow">Planning Range</span>
        <strong>{analysis.rangeLabel}</strong>
        <p>Low planning allowance {formatMoney(analysis.totalLow)}. High planning allowance {formatMoney(analysis.totalHigh)}+.</p>
      </article>
      <article>
        <span class="eyebrow">Confidence</span>
        <strong>Early feasibility</strong>
        <p>Useful for comparing scope, but it needs builder, designer, and roof/drainage checks before commitment.</p>
      </article>
      <article>
        <span class="eyebrow">Kitchen</span>
        <strong>Mostly retained</strong>
        <p>The estimate assumes the renovated kitchen stays largely intact and is protected during nearby work.</p>
      </article>
    </section>

    <section class="cost-breakdown-section" aria-label="Detailed estimated cost line items">
      <div class="section-heading">
        <span class="eyebrow">Breakdown</span>
        <h3>Detailed Cost Breakdown</h3>
      </div>
      <div class="cost-line-list">
        {#each analysis.lines as line}
          <article class="cost-line">
            <div class="cost-line-header">
              <div>
                <span class="cost-line-category">{line.category}</span>
                <h4>{line.item}</h4>
                <small>{line.confidence === "low" ? "Low confidence" : "Medium confidence"}</small>
              </div>
              <strong class="cost-line-range">{formatEstimatedCostRange(line)}</strong>
            </div>
            <p>{line.basis}</p>
            <ul>
              {#each line.notes as note}
                <li>{note}</li>
              {/each}
            </ul>
          </article>
        {/each}
      </div>
    </section>

    <section class="cost-detail-grid" aria-label="Assumptions and risk notes">
      <article>
        <h4>Roof And Envelope</h4>
        <ul>
          {#each analysis.roofNotes as note}
            <li>{note}</li>
          {/each}
        </ul>
      </article>
      <article>
        <h4>Furniture Editor Signals</h4>
        <ul>
          {#each analysis.furnitureSignals as signal}
            <li>{signal}</li>
          {/each}
        </ul>
      </article>
      <article>
        <h4>Assumptions</h4>
        <ul>
          {#each analysis.assumptions as assumption}
            <li>{assumption}</li>
          {/each}
        </ul>
      </article>
      <article>
        <h4>Exclusions</h4>
        <ul>
          {#each analysis.exclusions as exclusion}
            <li>{exclusion}</li>
          {/each}
        </ul>
      </article>
    </section>
  </section>
{/if}

<style>
  .estimated-cost {
    display: flex;
    flex-direction: column;
    gap: 16px;
    height: 100%;
    min-height: 0;
    overflow: auto;
    padding: 0 2px 28px;
    color: #243138;
  }

  .cost-hero,
  .cost-summary article,
  .cost-breakdown-section,
  .cost-line,
  .cost-detail-grid article {
    border: 1px solid #cbd7dc;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.9);
  }

  .cost-hero {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 18px;
    padding: 18px;
  }

  .cost-hero h3,
  .section-heading h3 {
    margin: 4px 0 8px;
    font-size: 1.35rem;
  }

  .cost-hero p,
  .cost-summary p,
  .cost-breakdown-section p {
    margin: 0;
    color: #47565d;
    line-height: 1.45;
  }

  .cost-actions {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
    min-width: 180px;
    color: #526269;
  }

  .cost-actions button {
    border: 1px solid #c4d0d6;
    border-radius: 6px;
    background: #f7fafb;
    padding: 8px 12px;
    color: #243138;
    font: inherit;
    font-weight: 700;
  }

  .cost-actions small {
    display: block;
    margin-top: 2px;
  }

  .cost-summary {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
  }

  .cost-summary article {
    padding: 14px;
  }

  .cost-summary strong {
    display: block;
    margin: 4px 0 6px;
    font-size: 1.5rem;
  }

  .cost-breakdown-section {
    padding: 16px;
  }

  .section-heading {
    padding: 0;
  }

  .cost-line-list {
    display: grid;
    gap: 10px;
    margin-top: 12px;
  }

  .cost-line {
    padding: 14px;
  }

  .cost-line-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 8px;
  }

  .cost-line h4 {
    margin: 2px 0 2px;
    font-size: 1rem;
    line-height: 1.2;
  }

  .cost-line small {
    display: block;
    color: #68777d;
    font-weight: 700;
  }

  .cost-line-category {
    color: #2b7a70;
    font-size: 0.7rem;
    font-weight: 900;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .cost-line-range {
    flex: 0 0 auto;
    min-width: 92px;
    color: #223039;
    font-size: 1rem;
    text-align: right;
    white-space: nowrap;
  }

  ul {
    margin: 8px 0 0;
    padding-left: 18px;
  }

  li + li {
    margin-top: 5px;
  }

  .cost-detail-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .cost-detail-grid article {
    padding: 14px;
  }

  .cost-detail-grid h4 {
    margin: 0 0 8px;
    font-size: 1rem;
  }

  .eyebrow {
    color: #2b7a70;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .inline-error {
    margin: 0;
    border: 1px solid #e0a9a9;
    border-radius: 6px;
    background: #fff4f4;
    padding: 10px 12px;
    color: #8b2f2f;
  }

  @media (max-width: 900px) {
    .cost-hero {
      flex-direction: column;
    }

    .cost-actions {
      align-items: flex-start;
    }

    .cost-summary,
    .cost-detail-grid {
      grid-template-columns: 1fr;
    }

    .cost-line-header {
      flex-direction: column;
      gap: 6px;
    }

    .cost-line-range {
      text-align: left;
    }
  }
</style>
