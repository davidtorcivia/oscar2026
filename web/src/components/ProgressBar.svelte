<script>
  let { picked = 0, total = 24 } = $props();
</script>

<div class="progress-bar">
  <div class="progress-track">
    <div class="progress-fill" style="width: {(picked / total) * 100}%"></div>
  </div>
  <span class="progress-text">
    <span class="progress-num">{picked}</span>/<span class="progress-num">{total}</span> picked
  </span>
</div>

<style>
  .progress-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
  }

  .progress-track {
    flex: 1;
    height: 4px;
    background: var(--divider);
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--gold);
    transition: width 0.3s ease;
    border-radius: 2px;
  }

  .progress-text {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: var(--text-dim);
    flex-shrink: 0;
  }

  .progress-num {
    color: var(--gold);
  }
</style>
