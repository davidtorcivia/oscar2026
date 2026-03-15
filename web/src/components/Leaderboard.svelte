<script>
  import { api } from '../lib/api.js';
  import { leaderboard, user } from '../lib/stores.js';
  import { onMount, onDestroy } from 'svelte';

  let entries = $state([]);
  let totalAnnounced = $state(0);
  let pollInterval;

  leaderboard.subscribe(v => entries = v);

  async function loadLeaderboard() {
    try {
      const data = await api.getLeaderboard();
      leaderboard.set(data.users);
      totalAnnounced = data.total_announced;
    } catch { /* ignore */ }
  }

  onMount(() => {
    loadLeaderboard();
    pollInterval = setInterval(loadLeaderboard, 60000);
  });

  onDestroy(() => {
    if (pollInterval) clearInterval(pollInterval);
  });

  let currentUser = $state(null);
  user.subscribe(u => currentUser = u);
</script>

<div class="leaderboard">
  <h2 class="lb-title">Leaderboard</h2>
  {#if totalAnnounced > 0}
    <p class="lb-announced">{totalAnnounced}/24 categories announced</p>
  {/if}

  <div class="lb-table">
    <div class="lb-header">
      <span class="lb-rank">#</span>
      <span class="lb-name">Name</span>
      <span class="lb-score">Score</span>
    </div>
    {#each entries as entry}
      <div class="lb-row" class:is-you={currentUser && entry.user_id === currentUser.user_id}>
        <span class="lb-rank">{entry.rank}</span>
        <span class="lb-name">
          {entry.username}
          {#if currentUser && entry.user_id === currentUser.user_id}
            <span class="you-tag">(you)</span>
          {/if}
        </span>
        <span class="lb-score">{entry.score}/{entry.total}</span>
      </div>
    {/each}
    {#if entries.length === 0}
      <div class="lb-empty">No ballots cast yet.</div>
    {/if}
  </div>
</div>

<style>
  .leaderboard {
    margin-top: 32px;
  }

  .lb-title {
    font-family: var(--font-display);
    font-size: 1.2rem;
    font-weight: 500;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
  }

  .lb-announced {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-bottom: 16px;
  }

  .lb-table {
    background: var(--black-card);
    border: 1px solid var(--divider);
  }

  .lb-header {
    display: flex;
    padding: 10px 16px;
    border-bottom: 1px solid var(--gold-dim);
    font-family: var(--font-body);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-dim);
  }

  .lb-row {
    display: flex;
    padding: 10px 16px;
    border-bottom: 1px solid var(--divider);
    transition: background 0.2s;
  }

  .lb-row:last-child {
    border-bottom: none;
  }

  .lb-row:hover {
    background: var(--black-surface);
  }

  .lb-row.is-you {
    background: rgba(213,186,109,0.08);
    border-left: 2px solid var(--gold);
  }

  .lb-rank {
    width: 40px;
    font-family: var(--font-mono);
    font-size: 0.9rem;
    color: var(--gold-dim);
    flex-shrink: 0;
  }

  .lb-name {
    flex: 1;
    font-size: 0.9rem;
  }

  .you-tag {
    font-size: 0.75rem;
    color: var(--gold-dim);
  }

  .lb-score {
    font-family: var(--font-mono);
    font-size: 0.9rem;
    color: var(--gold);
    flex-shrink: 0;
  }

  .lb-empty {
    padding: 20px;
    text-align: center;
    color: var(--text-dim);
    font-size: 0.9rem;
  }
</style>
