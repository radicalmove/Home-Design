<script lang="ts">
  import { objectBoundsSvg } from "./lib/furnitureGeometry";
  import { buildDesignReviewAnalysis } from "./lib/designReview";
  import { loadDesignReviewData } from "./lib/homeDesignCommands";
  import type {
    DesignReviewAnalysis,
    DesignReviewMovementScenario,
    DesignReviewSnippet,
  } from "./lib/designReview";
  import type { DesignReviewData, FurnitureObject } from "./types";

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

  let analysis = $derived<DesignReviewAnalysis | null>(
    reviewData ? buildDesignReviewAnalysis(reviewData) : null,
  );

  function toErrorMessage(reason: unknown): string {
    return reason instanceof Error ? reason.message : String(reason);
  }

  async function refreshReview() {
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

  function routePoints(scenario: DesignReviewMovementScenario): string {
    return scenario.points.map((point) => `${point.x},${point.y}`).join(" ");
  }

  function severityLabel(severity: string): string {
    if (severity === "good") {
      return "Strength";
    }
    return severity === "problem" ? "Problem" : "Watch";
  }

  $effect(() => {
    projectId;
    scenarioId;
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

    <section class="overall-assessment" aria-label="Overall design assessment">
      <span class="eyebrow">Assessment</span>
      <h3>{analysis.overallAssessment.title}</h3>
      {#each analysis.overallAssessment.paragraphs as paragraph}
        <p>{paragraph}</p>
      {/each}
      <ol>
        {#each analysis.overallAssessment.priorities as priority}
          <li>{priority}</li>
        {/each}
      </ol>
    </section>

    <section class="summary-list" aria-label="Strengths, weaknesses, and furniture opportunities">
      {#each analysis.summarySections as section}
        <article>
          <h4>{section.title}</h4>
          <ul>
            {#each section.points as point}
              <li>{point}</li>
            {/each}
          </ul>
        </article>
      {/each}
    </section>

    <section class="finding-grid" aria-label="Practical findings">
      {#each analysis.practicalFindings as finding}
        <article class:problem={finding.severity === "problem"} class:good={finding.severity === "good"}>
          <span>{severityLabel(finding.severity)}</span>
          <h4>{finding.title}</h4>
          <p>{finding.body}</p>
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

    <section class="movement-section" aria-label="Theoretical movement map">
      <div class="section-heading">
        <span class="eyebrow">Movement Map</span>
        <h3>Theoretical Movement Map</h3>
      </div>
      <div class="movement-layout">
        <svg
          viewBox={analysis.movementMapViewBox}
          role="img"
          aria-label="Theoretical movement routes for two adults and a teenager"
        >
          <image
            href="/views/reference_plan.svg"
            x="0"
            y="0"
            width={reviewData.furniture_layout.layout.plan_transform.svg_width_px}
            height={reviewData.furniture_layout.layout.plan_transform.svg_height_px}
          />
          {#each analysis.movementScenarios as scenario}
            {#if scenario.points.length > 1}
              <polyline
                points={routePoints(scenario)}
                stroke={scenario.colour}
                stroke-width="8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              {#each scenario.points as point, index}
                <circle cx={point.x} cy={point.y} r="10" fill={scenario.colour} />
                <text x={point.x} y={point.y + 4}>{index + 1}</text>
              {/each}
            {/if}
          {/each}
        </svg>
        <div class="movement-routes">
          {#each analysis.movementScenarios as scenario}
            <article style={`--route-colour: ${scenario.colour}`}>
              <span>{scenario.person}</span>
              <h4>{scenario.routine}</h4>
              <p>{scenario.rooms.join(" -> ")}</p>
              <small>{scenario.note}</small>
            </article>
          {/each}
        </div>
      </div>
    </section>

    <section class="data-section" aria-label="Data snapshot">
      <div class="section-heading">
        <span class="eyebrow">Data Snapshot</span>
        <h3>What The Review Is Reading</h3>
      </div>
      <div class="metric-grid">
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
      </div>
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

    <section class="room-review" aria-label="Room-by-room analysis">
      <div class="section-heading">
        <span class="eyebrow">Room-By-Room Analysis</span>
        <h3>Use, Light, Furniture, And Improvements</h3>
      </div>
      <div class="room-table">
        {#each analysis.roomAnalyses as room}
          <article>
            <div>
              <h4>{room.name}</h4>
              <span>{room.dimensions}</span>
            </div>
            <dl class="analysis-list">
              <div>
                <dt>Use</dt>
                <dd>{room.use}</dd>
              </div>
              <div>
                <dt>Light</dt>
                <dd>{room.light}</dd>
              </div>
              <div>
                <dt>Furniture</dt>
                <dd>{room.furniture}</dd>
              </div>
              <div>
                <dt>Improve</dt>
                <dd>{room.improvement}</dd>
              </div>
            </dl>
          </article>
        {/each}
      </div>
    </section>

    <section class="expert-section" aria-label="Expert review lens">
      <div class="section-heading">
        <span class="eyebrow">Expert Review Lens</span>
        <h3>Version Checked Against Three Expert Pushbacks</h3>
      </div>
      <div class="expert-list">
        {#each analysis.expertReview as review}
          <article>
            <h4>{review.role}</h4>
            <p><strong>Pushback:</strong> {review.pushback}</p>
            <p><strong>Added:</strong> {review.added}</p>
            <p><strong>Passes because:</strong> {review.passedBy}</p>
          </article>
        {/each}
      </div>
    </section>

    <section class="evidence-section" aria-label="Photo evidence used">
      <div class="section-heading">
        <span class="eyebrow">Evidence Inputs</span>
        <h3>Photos And Model Notes Used</h3>
      </div>
      <div class="evidence-list">
        {#each analysis.photoEvidence as evidence}
          <article>
            <h4>{evidence.id.replaceAll("_", " ")}</h4>
            <p>{evidence.summary}</p>
            <span>{evidence.photos.length} supporting photo{evidence.photos.length === 1 ? "" : "s"} checked</span>
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
  .overall-assessment h3,
  .summary-list h4,
  .finding-grid h4,
  .review-report h4,
  .movement-routes h4,
  .expert-list h4,
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
  .overall-assessment p,
  .finding-grid p,
  .review-report p,
  .movement-routes p,
  .expert-list p,
  .snippet-grid p,
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
  .overall-assessment,
  .summary-list article,
  .finding-grid article,
  .review-report article,
  .movement-routes article,
  .expert-list article,
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
  .finding-grid span,
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

  .overall-assessment {
    display: grid;
    gap: 12px;
    padding: 20px 22px;
    background: #ffffff;
    border: 1px solid #d7e0e4;
    border-left: 5px solid #2d6f64;
    border-radius: 8px;
  }

  .overall-assessment h3 {
    font-size: 1.18rem;
  }

  .overall-assessment p {
    max-width: 980px;
    color: #31444d;
    font-size: 1rem;
  }

  .overall-assessment ol {
    display: grid;
    gap: 8px;
    margin: 0;
    padding-left: 22px;
  }

  .overall-assessment li {
    line-height: 1.45;
  }

  .summary-list {
    display: grid;
    gap: 12px;
  }

  .summary-list article {
    display: grid;
    align-content: start;
    gap: 10px;
    padding: 17px;
  }

  .summary-list h4 {
    font-size: 1.05rem;
  }

  .summary-list ul {
    display: grid;
    gap: 8px;
    margin: 0;
    padding-left: 20px;
  }

  .summary-list li {
    line-height: 1.45;
  }

  .finding-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
  }

  .finding-grid article {
    display: grid;
    gap: 8px;
    padding: 15px;
    border-left: 4px solid #d99a38;
  }

  .finding-grid article.good {
    border-left-color: #3c8f75;
  }

  .finding-grid article.problem {
    border-left-color: #cf6044;
  }

  .finding-grid h4,
  .movement-routes h4,
  .expert-list h4,
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

  .review-report ul {
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

  .data-section,
  .movement-section,
  .snippet-section,
  .room-review,
  .expert-section,
  .evidence-section {
    display: grid;
    gap: 12px;
  }

  .movement-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(260px, 0.8fr);
    gap: 12px;
    align-items: start;
  }

  .movement-layout svg {
    display: block;
    width: 100%;
    aspect-ratio: 16 / 10;
    background: #f5f0e7;
    border: 1px solid #d4dde1;
    border-radius: 8px;
  }

  .movement-layout polyline {
    fill: none;
    opacity: 0.75;
  }

  .movement-layout circle {
    stroke: #ffffff;
    stroke-width: 3;
  }

  .movement-layout text {
    fill: #ffffff;
    font-size: 10px;
    font-weight: 800;
    text-anchor: middle;
  }

  .movement-routes,
  .expert-list {
    display: grid;
    gap: 12px;
  }

  .movement-routes article {
    display: grid;
    gap: 6px;
    padding: 14px;
    border-left: 5px solid var(--route-colour);
  }

  .movement-routes span {
    color: var(--route-colour);
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
  }

  .movement-routes small {
    color: #667780;
    line-height: 1.4;
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

  .room-table .analysis-list {
    display: grid;
    gap: 10px;
    margin: 0;
  }

  .analysis-list div {
    display: grid;
    gap: 3px;
  }

  .analysis-list dt,
  .analysis-list dd {
    margin: 0;
  }

  .analysis-list dt {
    color: #667780;
    font-size: 0.72rem;
    font-weight: 760;
    text-transform: uppercase;
  }

  .analysis-list dd {
    color: #31444d;
    font-size: 0.9rem;
    line-height: 1.42;
  }

  .expert-list article {
    display: grid;
    gap: 8px;
    padding: 15px;
  }

  .expert-list strong {
    color: #233640;
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

  .evidence-list span {
    color: #667780;
    font-size: 0.84rem;
  }

  @media (max-width: 980px) {
     .review-hero,
     .metric-grid,
    .finding-grid,
    .movement-layout,
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
