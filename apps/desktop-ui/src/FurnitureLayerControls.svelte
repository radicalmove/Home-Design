<script lang="ts">
  type Props = {
    fixedVisible: boolean;
    moveableVisible: boolean;
    onToggleFixed: () => void;
    onToggleMoveable: () => void;
  };

  let { fixedVisible, moveableVisible, onToggleFixed, onToggleMoveable }: Props = $props();
</script>

<section class="layer-controls" aria-label="Furniture layers">
  <label>
    <input type="checkbox" checked={fixedVisible} onchange={onToggleFixed} />
    Fixed
  </label>
  <label>
    <input type="checkbox" checked={moveableVisible} onchange={onToggleMoveable} />
    Moveable
  </label>
</section>

<style>
  .layer-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
  }

  label {
    display: inline-flex;
    gap: 7px;
    align-items: center;
    min-height: 34px;
    padding: 7px 10px;
    color: #23343b;
    font-size: 0.82rem;
    font-weight: 700;
    background: #ffffff;
    border: 1px solid #cdd7dc;
    border-radius: 8px;
  }

  input {
    width: 15px;
    height: 15px;
    accent-color: #3c7a6b;
  }
</style>
