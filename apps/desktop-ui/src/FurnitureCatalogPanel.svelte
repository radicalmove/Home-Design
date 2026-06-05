<script lang="ts">
  import type { FurnitureCatalog, FurnitureCatalogItem } from "./types";

  type Props = {
    catalog: FurnitureCatalog;
    onAddItem: (item: FurnitureCatalogItem) => void;
  };

  let { catalog, onAddItem }: Props = $props();
  let searchQuery = $state("");

  function catalogSearchText(groupName: string, item: FurnitureCatalogItem): string {
    return [
      groupName,
      item.id,
      item.label,
      item.layer,
      item.type,
      item.abbreviation,
      item.symbol,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
  }

  let filteredGroups = $derived(
    searchQuery.trim()
      ? catalog.groups
          .map((group) => ({
            ...group,
            items: group.items.filter((item) =>
              catalogSearchText(group.name, item).includes(searchQuery.trim().toLowerCase()),
            ),
          }))
          .filter((group) => group.items.length > 0)
      : catalog.groups,
  );

  function stopCatalogWheelPropagation(event: WheelEvent) {
    event.stopPropagation();
  }
</script>

<aside class="catalog-panel" aria-label="Furniture catalog" onwheel={stopCatalogWheelPropagation}>
  <header>
    <span class="eyebrow">Catalog</span>
    <h3>Objects</h3>
  </header>

  <label class="catalog-search">
    <span>Search</span>
    <input
      type="search"
      aria-label="Search catalog objects"
      placeholder="Search objects"
      autocomplete="off"
      bind:value={searchQuery}
    />
  </label>

  <div class="catalog-groups">
    {#if filteredGroups.length > 0}
      {#each filteredGroups as group}
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
    {:else}
      <p class="empty-search">No objects found.</p>
    {/if}
  </div>
</aside>

<style>
  .catalog-panel {
    display: grid;
    grid-template-rows: auto auto minmax(0, 1fr);
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

  .catalog-search {
    display: grid;
    gap: 5px;
    min-width: 0;
    color: #475c64;
    font-size: 0.72rem;
    font-weight: 760;
  }

  .catalog-search input {
    width: 100%;
    min-width: 0;
    height: 34px;
    padding: 6px 9px;
    color: #1e3037;
    background: #ffffff;
    border: 1px solid #cfd9de;
    border-radius: 6px;
  }

  .catalog-search input:focus {
    border-color: #7ebdae;
    outline: none;
    box-shadow: 0 0 0 2px rgba(126, 189, 174, 0.2);
  }

  .catalog-groups {
    display: grid;
    align-content: start;
    gap: 10px;
    min-height: 0;
    overflow: auto;
    overscroll-behavior: contain;
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

  .empty-search {
    margin: 0;
    padding: 10px 2px;
    color: #5d7077;
    font-size: 0.76rem;
    line-height: 1.4;
  }
</style>
