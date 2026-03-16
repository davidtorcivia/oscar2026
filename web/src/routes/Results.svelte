<script>
  import { onMount, onDestroy } from 'svelte';
  import { user, ballot, categories, results } from '../lib/stores.js';
  import { api } from '../lib/api.js';
  import CategoryCard from '../components/CategoryCard.svelte';
  import Leaderboard from '../components/Leaderboard.svelte';

  let cats = $state([]);
  let picks = $state({});
  let userData = $state(null);
  let resultsData = $state([]);
  let score = $state(0);
  let totalAnnounced = $state(0);
  let pollInterval;

  categories.subscribe(c => cats = c);
  ballot.subscribe(b => picks = { ...b });
  user.subscribe(u => userData = u);
  results.subscribe(r => resultsData = r);

  function computeScore() {
    let s = 0;
    let t = 0;
    for (const r of resultsData) {
      const winnerList = r.winners || (r.winner ? [r.winner] : []);
      if (winnerList.length > 0) {
        t++;
        const userPick = picks[String(r.id)];
        if (userPick && winnerList.some(w => w.id === userPick)) {
          s++;
        }
      }
    }
    score = s;
    totalAnnounced = t;
  }

  async function loadResults() {
    try {
      const data = await api.getResults();
      results.set(data.categories);

      // Also refresh categories to get latest winner flags
      const catData = await api.getCategories();
      categories.set(catData.categories);
    } catch { /* ignore */ }
  }

  onMount(async () => {
    await loadResults();
    if (userData) {
      try {
        const ballotData = await api.getBallot(userData.user_id);
        ballot.set(ballotData.picks || {});
      } catch { /* ignore */ }
    }
    pollInterval = setInterval(loadResults, 60000);
  });

  onDestroy(() => {
    if (pollInterval) clearInterval(pollInterval);
  });

  $effect(() => {
    computeScore();
  });
</script>

<div class="results-page">
  <div class="score-section">
    <div class="score-ring">
      <svg viewBox="0 0 120 120" width="120" height="120">
        <circle cx="60" cy="60" r="52" fill="none" stroke="#222" stroke-width="6" />
        <circle cx="60" cy="60" r="52" fill="none" stroke="var(--gold)" stroke-width="6"
          stroke-dasharray="{(totalAnnounced > 0 ? score / totalAnnounced : 0) * 327} 327"
          stroke-linecap="round"
          transform="rotate(-90 60 60)"
          style="transition: stroke-dasharray 0.5s ease"
        />
      </svg>
      <div class="score-text">
        <span class="score-num">{score}</span>
        <span class="score-slash">/</span>
        <span class="score-total">{totalAnnounced}</span>
      </div>
    </div>
    <p class="score-label">
      {#if totalAnnounced === 0}
        No results yet - check back during the ceremony
      {:else if totalAnnounced < 24}
        {totalAnnounced} of 24 announced
      {:else}
        Final score
      {/if}
    </p>
  </div>

  <div class="results-grid">
    <div class="leaderboard-col">
      <Leaderboard />
    </div>

    <div class="categories-col">
      <h2 class="section-title">Your Ballot</h2>
      {#each cats as cat, i}
        <div style="animation-delay: {i * 30}ms">
          <CategoryCard
            category={cat}
            readonly={true}
            showWinner={true}
            userPick={picks[String(cat.id)] || null}
          />
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .results-page {
    padding-top: 8px;
  }

  .score-section {
    text-align: center;
    padding: 24px 0 32px;
  }

  .score-ring {
    position: relative;
    display: inline-block;
  }

  .score-text {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
  }

  .score-num {
    font-family: var(--font-mono);
    font-size: 2rem;
    font-weight: 500;
    color: var(--gold);
  }

  .score-slash {
    font-family: var(--font-mono);
    font-size: 1.5rem;
    color: var(--text-dim);
    margin: 0 2px;
  }

  .score-total {
    font-family: var(--font-mono);
    font-size: 1.5rem;
    color: var(--text-dim);
  }

  .score-label {
    margin-top: 12px;
    font-size: 0.9rem;
    color: var(--text-dim);
  }

  .section-title {
    font-family: var(--font-display);
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 16px;
  }

  .results-grid {
    display: flex;
    flex-direction: column;
  }

  @media (min-width: 768px) {
    .results-grid {
      display: grid;
      grid-template-columns: 1fr 360px;
      gap: 24px;
      align-items: start;
    }

    .categories-col {
      order: 1;
    }

    .leaderboard-col {
      order: 2;
      position: sticky;
      top: 16px;
    }
  }
</style>
