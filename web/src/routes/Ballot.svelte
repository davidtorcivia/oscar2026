<script>
  import { onMount, onDestroy } from 'svelte';
  import { user, ballot, categories, currentView } from '../lib/stores.js';
  import { api } from '../lib/api.js';
  import CategoryCard from '../components/CategoryCard.svelte';
  import ProgressBar from '../components/ProgressBar.svelte';
  import Leaderboard from '../components/Leaderboard.svelte';

  let cats = $state([]);
  let picks = $state({});
  let userData = $state(null);
  let saving = $state(false);
  let submitting = $state(false);
  let showConfirm = $state(false);
  let error = $state('');
  let showLeaderboard = $state(false);
  let hasResults = $state(false);
  let locked = $state(false);
  let pollInterval;

  categories.subscribe(c => cats = c);
  ballot.subscribe(b => picks = { ...b });
  user.subscribe(u => userData = u);

  $effect(() => {
    pickedCount = Object.keys(picks).length;
  });

  let pickedCount = $state(0);

  // Lock time: 7:30 PM EDT = 23:30 UTC on March 15, 2026
  const LOCK_UTC = new Date('2026-03-15T23:30:00Z');

  function checkLock() {
    if (new Date() >= LOCK_UTC) {
      locked = true;
      // Auto-redirect to results
      user.set({ ...userData, submitted: true });
      currentView.set('results');
    }
  }

  async function checkResults() {
    try {
      const data = await api.getResults();
      hasResults = data.categories.some(c => c.winner);
    } catch { /* ignore */ }
  }

  onMount(() => {
    checkLock();
    checkResults();
    pollInterval = setInterval(() => {
      checkLock();
      checkResults();
    }, 30000);
  });

  onDestroy(() => {
    if (pollInterval) clearInterval(pollInterval);
  });

  async function handlePick(categoryId, nomineeId) {
    const key = String(categoryId);
    picks[key] = nomineeId;
    ballot.set({ ...picks });

    // Auto-save
    saving = true;
    try {
      await api.saveBallot(userData.user_id, { [key]: nomineeId });
    } catch (err) {
      error = err.error || 'Failed to save pick.';
    } finally {
      saving = false;
    }
  }

  async function handleSubmit() {
    submitting = true;
    error = '';
    try {
      await api.submitBallot(userData.user_id, picks);
      user.set({ ...userData, submitted: true });
      currentView.set('results');
    } catch (err) {
      error = err.error || 'Failed to submit ballot.';
      showConfirm = false;
    } finally {
      submitting = false;
    }
  }
</script>

<div class="ballot-page">
  {#if hasResults}
    <div class="ballot-tabs">
      <button class:active={!showLeaderboard} onclick={() => showLeaderboard = false}>Ballot</button>
      <button class:active={showLeaderboard} onclick={() => showLeaderboard = true}>Leaderboard</button>
    </div>
  {/if}

  {#if showLeaderboard}
    <Leaderboard />
  {:else}
    <div class="lock-notice">Ballots lock at 7:30 PM ET when the awards begin</div>
    <ProgressBar picked={pickedCount} total={cats.length} />

    {#if saving}
      <div class="save-indicator">Saving...</div>
    {/if}

    <div class="categories-grid">
      {#each cats as cat, i}
        <div style="animation-delay: {i * 30}ms">
          <CategoryCard
            category={cat}
            selectedNomineeId={picks[String(cat.id)] || null}
            onPick={handlePick}
          />
        </div>
      {/each}
    </div>

    {#if error}
      <div class="error-msg">{error}</div>
    {/if}
  {/if}
</div>

<!-- Sticky footer -->
<div class="ballot-footer">
  <div class="footer-inner">
    {#if showConfirm}
      <div class="confirm-dialog">
        <p>
          {#if pickedCount < cats.length}
            You have {cats.length - pickedCount} blank categories. Blank picks cannot earn points.
          {/if}
          This is final. Once cast, your ballot cannot be changed.
        </p>
        <div class="confirm-actions">
          <button class="btn-cancel" onclick={() => showConfirm = false}>Cancel</button>
          <button class="btn-confirm" onclick={handleSubmit} disabled={submitting}>
            {submitting ? 'Submitting...' : 'Confirm'}
          </button>
        </div>
      </div>
    {:else}
      <button
        class="cast-btn"
        disabled={pickedCount === 0}
        onclick={() => showConfirm = true}
      >
        {#if pickedCount === 0}
          Pick at least one category to cast
        {:else if pickedCount < cats.length}
          Cast Ballot ({pickedCount}/{cats.length} picked)
        {:else}
          Cast Ballot
        {/if}
      </button>
    {/if}
  </div>
</div>

<style>
  .ballot-page {
    padding-bottom: 20px;
  }

  .ballot-tabs {
    display: flex;
    gap: 0;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--divider-light);
  }

  .ballot-tabs button {
    padding: 10px 20px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-dim);
    font-family: var(--font-body);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .ballot-tabs button.active {
    color: var(--gold);
    border-bottom-color: var(--gold);
  }

  .lock-notice {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--text-dim);
    text-align: center;
    padding: 8px 0 0;
  }

  .save-indicator {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--gold-dim);
    text-align: right;
    padding: 4px 0;
  }

  .categories-grid {
    display: flex;
    flex-direction: column;
  }

  @media (min-width: 768px) {
    .categories-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0 16px;
    }
  }

  .error-msg {
    margin-top: 12px;
    padding: 12px;
    background: rgba(128, 27, 29, 0.15);
    border: 1px solid var(--red);
    color: var(--red-accent);
    font-size: 0.9rem;
  }

  .ballot-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--black-card);
    border-top: 1px solid var(--divider-light);
    padding: 12px 15px;
    z-index: 100;
  }

  .footer-inner {
    max-width: 960px;
    margin: 0 auto;
  }

  .cast-btn {
    width: 100%;
    padding: 14px;
    background: var(--gold-gradient);
    color: var(--black);
    border: none;
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .cast-btn:hover:not(:disabled) {
    opacity: 0.9;
  }

  .cast-btn:disabled {
    background: var(--divider-light);
    color: var(--gray-mid);
    cursor: not-allowed;
  }

  .confirm-dialog {
    text-align: center;
  }

  .confirm-dialog p {
    color: var(--text);
    margin-bottom: 12px;
    font-size: 0.95rem;
  }

  .confirm-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
  }

  .btn-cancel {
    padding: 10px 24px;
    background: none;
    border: 1px solid var(--divider-light);
    color: var(--text-dim);
    font-family: var(--font-body);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .btn-cancel:hover {
    border-color: var(--text-dim);
  }

  .btn-confirm {
    padding: 10px 24px;
    background: var(--red);
    border: none;
    color: var(--white);
    font-family: var(--font-display);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: opacity 0.2s;
  }

  .btn-confirm:hover:not(:disabled) {
    opacity: 0.85;
  }

  .btn-confirm:disabled {
    opacity: 0.5;
  }
</style>
