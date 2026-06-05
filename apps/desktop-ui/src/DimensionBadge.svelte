<script lang="ts">
  type Props = {
    label: string | null;
    x: number;
    y: number;
  };

  let { label, x, y }: Props = $props();
</script>

{#if label}
  <div class="dimension-badge" style={`left:${x}px; top:${y}px;`}>
    {label}
  </div>
{/if}

<style>
  .dimension-badge {
    position: absolute;
    z-index: 4;
    padding: 3px 6px;
    color: #263238;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
    pointer-events: none;
    background: #fffdf8;
    border: 1px solid #263238;
    transform: translate(-50%, -120%);
  }
</style>
