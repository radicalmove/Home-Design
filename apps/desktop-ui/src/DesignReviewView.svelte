<script lang="ts">
  import { onMount } from "svelte";
  import { objectBoundsSvg } from "./lib/furnitureGeometry";
  import { buildDesignReviewAnalysis } from "./lib/designReview";
  import { loadDesignReviewData } from "./lib/homeDesignCommands";
  import type {
    DesignReviewAnalysis,
    DesignReviewSnippet,
  } from "./lib/designReview";
  import type { DesignReviewData, FurnitureObject } from "./types";

  type Props = {
    projectId: string;
  };

  let { projectId }: Props = $props();

  let reviewData = $state<DesignReviewData | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let refreshedAt = $state<string | null>(null);

  let analysis = $derived<DesignReviewAnalysis | null>(
    reviewData ? buildDesignReviewAnalysis(reviewData) : null,
  );

  function toErrorMessage(reason: unknown): string {
    return reason instanceof Error ? reason.message : String(reason);
  }

  async function refreshReview() {
    loading = true;
    error = null;
    try {
      reviewData = await loadDesignReviewData(projectId);
      refreshedAt = new Intl.DateTimeFormat(undefined, {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }).format(new Date());
    } catch (reason: unknown) {
      error = toErrorMessage(reason);
    } finally {
      loading = false;
    }
  }

  function highlightedObjects(snippet: DesignReviewSnippet): FurnitureObject[] {
    if (!reviewData) {
      return [];
    }
    const ids = new Set(snippet.highlightObjectIds);
    return reviewData.furniture_layout.layout.objects.filter((object) => ids.has(object.id));
  }

  function furnitureRect(object: FurnitureObject) {
    if (!reviewData) {
      return null;
    }
    return objectBoundsSvg(object, reviewData.furniture_layout.layout.plan_transform);
  }

  function furnitureTransform(object: FurnitureObject): string {
    const bounds = furnitureRect(object);
    return bounds ? `rotate(${object.rotation_deg} ${bounds.cx} ${bounds.cy})` : "";
  }

  function severityLabel(severity: string): string {
    if (severity === "good") {
      return "Strength";
    }
    return severity === "problem" ? "Problem" : "Watch";
  }

  onMount(() => {
    void refreshReview();
  });
</script>

{#if loading && !analysis}
  <div class="state-panel">Loading design review...</div>
{:else if error && !analysis}
  <div class="state-panel error">{error}</div>
{:else if analysis && reviewData}
  <section class="design-review" aria-label="Design review report">
    <header class="review-hero">
      <div>
        <span class="eyebrow">Design Review</span>
        <h3>Current House Design Review</h3>
        <p>
          Practical interior-design and builder-style review for two adults in the Master Bedroom
          and a teenage girl in Bedroom 2, refreshed from the current saved furniture layout.
        </p>
      </div>
      <div class="review-actions">
        <button type="button" onclick={refreshReview}>Refresh Review</button>
        <span>
          {analysis.layoutSource === "saved" ? "Saved furniture layout" : "Seed furniture layout"}
          {#if refreshedAt}
            <small>Refreshed {refreshedAt}</small>
          {/if}
        </span>
      </div>
    </header>

    {#if error}
      <p class="inline-error">{error}</p>
    {/if}

    <section class="metric-grid" aria-label="Review metrics">
      <article>
        <span>Rooms</span>
        <strong>{analysis.metrics.roomCount}</strong>
      </article>
      <article>
        <span>Furniture</span>
        <strong>{analysis.metrics.totalFurnitureObjects}</strong>
      </article>
      <article>
        <span>Fixed</span>
        <strong>{analysis.metrics.fixedFurnitureObjects}</strong>
      </article>
      <article>
        <span>Moveable</span>
        <strong>{analysis.metrics.moveableFurnitureObjects}</strong>
      </article>
      <article>
        <span>Winter Light Watch</span>
        <strong>{analysis.metrics.lowWinterLightRooms.length}</strong>
      </article>
      <article>
        <span>Off Plan</span>
        <strong>{analysis.offPlanObjects.length}</strong>
      </article>
    </section>

    <section class="warning-grid" aria-label="Key observations">
      {#each analysis.dynamicWarnings as warning}
        <article class:problem={warning.severity === "problem"} class:good={warning.severity === "good"}>
          <span>{severityLabel(warning.severity)}</span>
          <h4>{warning.title}</h4>
          <p>{warning.body}</p>
        </article>
      {/each}
    </section>

    <section class="review-report" aria-label="Detailed report">
      {#each analysis.reportSections as section}
        <article>
          <h4>{section.title}</h4>
          <p>{section.summary}</p>
          <ul>
            {#each section.points as point}
              <li>{point}</li>
            {/each}
          </ul>
        </article>
      {/each}
    </section>

    <section class="snippet-section" aria-label="Plan snippets">
      <div class="section-heading">
        <span class="eyebrow">Plan Snippets</span>
        <h3>2D Evidence Extracts</h3>
      </div>
      <div class="snippet-grid">
        {#each analysis.snippets as snippet}
          <article>
            <svg viewBox={snippet.viewBox} role="img" aria-label={snippet.title}>
              <image
                href="/views/reference_plan.svg"
                x="0"
                y="0"
                width={reviewData.furniture_layout.layout.plan_transform.svg_width_px}
                height={reviewData.furniture_layout.layout.plan_transform.svg_height_px}
              />
              {#each highlightedObjects(snippet) as object}
                {@const bounds = furnitureRect(object)}
                {#if bounds}
                  <g transform={furnitureTransform(object)}>
                    <rect
                      class:fixed={object.layer === "fixed"}
                      x={bounds.x}
                      y={bounds.y}
                      width={bounds.width}
                      height={bounds.height}
                      fill={object.colour}
                    />
                  </g>
                {/if}
              {/each}
            </svg>
            <h4>{snippet.title}</h4>
            <p>{snippet.body}</p>
          </article>
        {/each}
      </div>
    </section>

    <section class="room-review" aria-label="Room-by-room review">
      <div class="section-heading">
        <span class="eyebrow">Room-By-Room Review</span>
        <h3>Use, Light, And Furniture Fit</h3>
      </div>
      <div class="room-table">
        {#each analysis.rooms as room}
          <article>
            <div>
              <h4>{room.name}</h4>
              <span>{room.dimensionsLabel}</span>
            </div>
            <p>{room.daylightSummary}</p>
            <dl>
              <div>
                <dt>Fixed</dt>
                <dd>{room.fixedCount}</dd>
              </div>
              <div>
                <dt>Moveable</dt>
                <dd>{room.moveableCount}</dd>
              </div>
              <div>
                <dt>Total</dt>
                <dd>{room.objects.length}</dd>
              </div>
            </dl>
            {#if room.objects.length > 0}
              <p class="object-list">
                {room.objects.map((object) => object.label).join(", ")}
              </p>
            {/if}
          </article>
        {/each}
      </div>
    </section>

    <section class="evidence-section" aria-label="Photo evidence used">
      <div class="section-heading">
        <span class="eyebrow">Photo Evidence</span>
        <h3>Reviewed Project Photos</h3>
      </div>
      <div class="evidence-list">
        {#each analysis.photoEvidence as evidence}
          <article>
            <h4>{evidence.id.replaceAll("_", " ")}</h4>
            <p>{evidence.summary}</p>
            <ul>
              {#each evidence.photos as photo}
                <li>
                  <strong>{photo.path}</strong>
                  <span>{photo.view}</span>
                </li>
              {/each}
            </ul>
          </article>
        {/each}
      </div>
    </section>
  </section>
{:else}
  <div class="state-panel error">Design review data is unavailable.</div>
{/if}

<style>
  .design-review {
    display: grid;
    gap: 18px;
    height: 100%;
    min-height: 0;
    overflow: auto;
    padding: 0 2px 28px;
    color: #223039;
  }

  .review-hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(210px, auto);
    gap: 18px;
    align-items: start;
    padding: 22px;
    background: #fbfcfc;
    border: 1px solid #d7e0e4;
    border-radius: 8px;
  }

  .review-hero h3,
  .section-heading h3,
  .review-report h4,
  .warning-grid h4,
  .snippet-grid h4,
  .room-table h4,
  .evidence-list h4 {
    margin: 0;
    line-height: 1.15;
    letter-spacing: 0;
  }

  .review-hero h3 {
    margin-top: 4px;
    font-size: 1.45rem;
  }

  .review-hero p,
  .review-report p,
  .warning-grid p,
  .snippet-grid p,
  .room-table p,
  .evidence-list p {
    margin: 0;
    line-height: 1.5;
  }

  .review-hero p {
    max-width: 760px;
    margin-top: 8px;
    color: #52636c;
  }

  .review-actions {
    display: grid;
    gap: 8px;
    justify-items: end;
  }

  .review-actions button {
    min-height: 36px;
    padding: 7px 12px;
    color: #f8fbfb;
    font-weight: 760;
    cursor: pointer;
    background: #2d6f64;
    border: 1px solid #245a52;
    border-radius: 7px;
  }

  .review-actions span {
    display: grid;
    gap: 2px;
    color: #31444d;
    font-size: 0.82rem;
    text-align: right;
  }

  .review-actions small {
    color: #6d7b82;
  }

  .inline-error {
    margin: 0;
    padding: 10px 12px;
    color: #823c2c;
    background: #fff1ed;
    border: 1px solid #f2b7a8;
    border-radius: 7px;
  }

  .metric-grid {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 10px;
  }

  .metric-grid article,
  .warning-grid article,
  .review-report article,
  .snippet-grid article,
  .room-table article,
  .evidence-list article {
    background: #ffffff;
    border: 1px solid #d7e0e4;
    border-radius: 8px;
  }

  .metric-grid article {
    display: grid;
    gap: 6px;
    padding: 13px;
  }

  .metric-grid span,
  .warning-grid span,
  .room-table span {
    color: #667780;
    font-size: 0.76rem;
    font-weight: 720;
    text-transform: uppercase;
  }

  .metric-grid strong {
    color: #1e2e36;
    font-size: 1.6rem;
    line-height: 1;
  }

  .warning-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
  }

  .warning-grid article {
    display: grid;
    gap: 8px;
    padding: 15px;
    border-left: 4px solid #d99a38;
  }

  .warning-grid article.good {
    border-left-color: #3c8f75;
  }

  .warning-grid article.problem {
    border-left-color: #cf6044;
  }

  .warning-grid h4,
  .snippet-grid h4,
  .room-table h4,
  .evidence-list h4 {
    font-size: 0.98rem;
  }

  .review-report {
    display: grid;
    gap: 12px;
  }

  .review-report article {
    display: grid;
    gap: 10px;
    padding: 18px 20px;
  }

  .review-report h4 {
    font-size: 1.12rem;
  }

  .review-report ul,
  .evidence-list ul {
    display: grid;
    gap: 8px;
    margin: 0;
    padding-left: 20px;
  }

  .review-report li {
    line-height: 1.5;
  }

  .section-heading {
    display: grid;
    gap: 4px;
  }

  .snippet-section,
  .room-review,
  .evidence-section {
    display: grid;
    gap: 12px;
  }

  .snippet-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .snippet-grid article {
    display: grid;
    gap: 10px;
    padding: 12px;
  }

  .snippet-grid svg {
    display: block;
    width: 100%;
    aspect-ratio: 16 / 10;
    background: #f5f0e7;
    border: 1px solid #d4dde1;
    border-radius: 6px;
  }

  .snippet-grid rect {
    stroke: #1e2e36;
    stroke-width: 1.5;
    opacity: 0.82;
  }

  .snippet-grid rect.fixed {
    stroke-dasharray: 4 2;
  }

  .room-table {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .room-table article {
    display: grid;
    gap: 10px;
    padding: 14px;
  }

  .room-table article > div:first-child {
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }

  .room-table dl {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    margin: 0;
  }

  .room-table dt,
  .room-table dd {
    margin: 0;
  }

  .room-table dt {
    color: #667780;
    font-size: 0.72rem;
  }

  .room-table dd {
    font-size: 1.08rem;
    font-weight: 780;
  }

  .object-list {
    color: #52636c;
    font-size: 0.86rem;
  }

  .evidence-list {
    display: grid;
    gap: 12px;
  }

  .evidence-list article {
    display: grid;
    gap: 8px;
    padding: 14px;
  }

  .evidence-list li {
    display: grid;
    gap: 2px;
    line-height: 1.35;
  }

  .evidence-list strong {
    color: #2e4651;
    font-size: 0.82rem;
    overflow-wrap: anywhere;
  }

  .evidence-list span {
    color: #667780;
    font-size: 0.84rem;
  }

  @media (max-width: 980px) {
    .review-hero,
    .metric-grid,
    .warning-grid,
    .snippet-grid,
    .room-table {
      grid-template-columns: 1fr;
    }

    .review-actions {
      justify-items: start;
    }

    .review-actions span {
      text-align: left;
    }
  }
</style>
