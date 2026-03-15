<script>
  let { category, selectedNomineeId = null, onPick = () => {}, readonly = false, userPick = null, showWinner = false } = $props();
</script>

<div class="category-card" class:has-winner={showWinner && category.nominees.some(n => n.is_winner)}>
  <h3 class="category-name">{category.name}</h3>
  <div class="nominees">
    {#each category.nominees as nominee}
      {@const isSelected = selectedNomineeId === nominee.id}
      {@const isWinner = nominee.is_winner}
      {@const isUserPick = userPick === nominee.id}
      {@const correct = isWinner && isUserPick}
      {@const wrong = isWinner && userPick && !isUserPick}
      <button
        class="nominee-btn"
        class:selected={isSelected && !readonly}
        class:winner={showWinner && isWinner}
        class:correct={showWinner && correct}
        class:wrong-pick={showWinner && isUserPick && !isWinner && category.nominees.some(n => n.is_winner)}
        class:user-picked={showWinner && isUserPick && !isWinner && !category.nominees.some(n => n.is_winner)}
        class:readonly
        disabled={readonly}
        onclick={() => !readonly && onPick(category.id, nominee.id)}
      >
        <span class="nominee-indicator">
          {#if showWinner && isWinner}
            &#9733;
          {:else if isSelected}
            &#10003;
          {:else}
            &#9675;
          {/if}
        </span>
        <span class="nominee-info">
          <span class="nominee-name">{nominee.name}</span>
          {#if nominee.subtitle}
            <span class="nominee-subtitle">{nominee.subtitle}</span>
          {/if}
        </span>
        {#if showWinner && isUserPick}
          <span class="your-pick">YOUR PICK</span>
        {/if}
      </button>
    {/each}
  </div>
</div>

<style>
  .category-card {
    background: var(--black-card);
    border: 1px solid var(--divider);
    padding: 20px;
    margin-bottom: 16px;
    animation: fadeUp 0.4s ease both;
  }

  .category-card.has-winner {
    border-color: var(--gold-dim);
  }

  .category-name {
    font-family: var(--font-display);
    font-size: 0.85rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gold);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--divider);
  }

  .nominees {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .nominee-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 10px 12px;
    background: transparent;
    border: 1px solid transparent;
    color: var(--text);
    font-family: var(--font-body);
    font-size: 0.9rem;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }

  .nominee-btn:not(.readonly):hover {
    background: var(--hover);
    border-color: var(--divider-light);
  }

  .nominee-btn.selected {
    background: linear-gradient(90deg, rgba(213,186,109,0.15), transparent);
    border-color: var(--gold);
  }

  .nominee-btn.winner {
    background: linear-gradient(90deg, rgba(213,186,109,0.2), rgba(213,186,109,0.05));
    border-color: var(--gold);
  }

  .nominee-btn.correct {
    background: linear-gradient(90deg, rgba(213,186,109,0.28), rgba(213,186,109,0.08));
    border-color: var(--gold-bright);
  }

  .nominee-btn.wrong-pick {
    background: rgba(128, 27, 29, 0.15);
    border-color: var(--red);
  }

  .nominee-btn.user-picked {
    background: linear-gradient(90deg, rgba(213,186,109,0.12), transparent);
    border-color: var(--gold-dim);
  }

  .nominee-btn.readonly {
    cursor: default;
  }

  .nominee-indicator {
    flex-shrink: 0;
    width: 20px;
    text-align: center;
    font-size: 0.9rem;
    color: var(--gold-dim);
  }

  .nominee-btn.selected .nominee-indicator,
  .nominee-btn.winner .nominee-indicator {
    color: var(--gold);
  }

  .nominee-info {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 0;
  }

  .nominee-name {
    font-weight: 500;
  }

  .nominee-subtitle {
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-top: 1px;
  }

  .your-pick {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--gold);
    letter-spacing: 0.1em;
    flex-shrink: 0;
    background: rgba(213,186,109,0.12);
    border: 1px solid var(--gold-dim);
    padding: 2px 6px;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
