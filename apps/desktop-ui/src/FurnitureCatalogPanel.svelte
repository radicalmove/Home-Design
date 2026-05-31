<script lang="ts">
  import type { FurnitureCatalog, FurnitureCatalogItem } from "./types";

  type Props = {
    catalog: FurnitureCatalog;
    onAddItem: (item: FurnitureCatalogItem) => void;
  };

  let { catalog, onAddItem }: Props = $props();
</script>

<aside class="catalog-panel" aria-label="Furniture catalog">
  <header>
    <span class="eyebrow">Catalog</span>
    <h3>Objects</h3>
  </header>

  <div class="catalog-groups">
    {#each catalog.groups as group}
      <details open>
        <summary>{group.name}</summary>
        <div class="catalog-items">
          {#each group.items as item}
            <button type="button" onclick={() => onAddItem(item)}>
              <span class="item-label">{item.label}</span>
              <span class="item-meta">
                {item.layer}
                {item.abbreviation ? ` · ${item.abbreviation}` : ""}
                · {item.default_width_m.toFixed(2)} x {item.default_depth_m.toFixed(2)} m
              </span>
            </button>
          {/each}
        </div>
      </details>
    {/each}
  </div>
</aside>

<style>
  .catalog-panel {
    display: grid;
    grid-template-rows: auto minmax(0, 1fr);
    gap: 12px;
    min-width: 0;
    min-height: 0;
    padding: 14px;
    overflow: hidden;
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
  }

  .catalog-groups {
    display: grid;
    align-content: start;
    gap: 10px;
    min-height: 0;
    overflow: auto;
  }

  details {
    min-width: 0;
  }

  summary {
    color: #344951;
    font-size: 0.78rem;
    font-weight: 760;
    cursor: pointer;
  }

  .catalog-items {
    display: grid;
    gap: 6px;
    padding-top: 8px;
  }

  button {
    display: grid;
    gap: 3px;
    width: 100%;
    min-height: 44px;
    padding: 8px 9px;
    color: #203139;
    text-align: left;
    cursor: pointer;
    background: #f7f9fa;
    border: 1px solid #d8e0e4;
    border-radius: 8px;
  }

  button:hover,
  button:focus-visible {
    background: #eef7f4;
    border-color: #7ebdae;
    outline: none;
  }

  .item-label,
  .item-meta {
    min-width: 0;
    overflow-wrap: anywhere;
  }

  .item-label {
    font-size: 0.82rem;
    font-weight: 730;
  }

  .item-meta {
    color: #5a6b72;
    font-size: 0.69rem;
  }
</style>
