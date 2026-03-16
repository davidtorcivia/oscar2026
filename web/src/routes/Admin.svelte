<script>
  import { onMount } from 'svelte';
  import { isAdmin } from '../lib/stores.js';
  import { api } from '../lib/api.js';

  let loggedIn = $state(false);
  let password = $state('');
  let loginError = $state('');

  let activeTab = $state('results');  // results, users, stats
  let categories = $state([]);
  let users = $state([]);
  let stats = $state(null);
  let error = $state('');
  let success = $state('');

  isAdmin.subscribe(v => loggedIn = v);

  onMount(async () => {
    try {
      await api.adminCheck();
      isAdmin.set(true);
      await loadData();
    } catch {
      isAdmin.set(false);
    }
  });

  async function login() {
    loginError = '';
    try {
      await api.adminLogin(password);
      isAdmin.set(true);
      password = '';
      await loadData();
    } catch (err) {
      loginError = err.error || 'Wrong password.';
    }
  }

  async function logout() {
    await api.adminLogout();
    isAdmin.set(false);
  }

  async function loadData() {
    try {
      const catData = await api.getCategories();
      categories = catData.categories;
    } catch { /* ignore */ }
  }

  async function loadUsers() {
    try {
      const data = await api.adminGetUsers();
      users = data.users;
    } catch { /* ignore */ }
  }

  async function loadStats() {
    try {
      stats = await api.adminGetStats();
    } catch { /* ignore */ }
  }

  let confirmDeleteUser = $state(null);

  async function deleteUser(userId) {
    error = '';
    success = '';
    try {
      await api.adminDeleteUser(userId);
      success = 'User deleted.';
      confirmDeleteUser = null;
      await loadUsers();
    } catch (err) {
      error = err.error || 'Failed to delete user.';
    }
  }

  async function setWinner(categoryId, nomineeId) {
    error = '';
    success = '';
    try {
      await api.adminSetWinner(categoryId, nomineeId);
      success = 'Winner set.';
      await loadData();
    } catch (err) {
      error = err.error || 'Failed to set winner.';
    }
  }

  async function clearWinner(categoryId) {
    error = '';
    success = '';
    try {
      await api.adminClearWinner(categoryId);
      success = 'Winner cleared.';
      await loadData();
    } catch (err) {
      error = err.error || 'Failed to clear winner.';
    }
  }

  function switchTab(tab) {
    activeTab = tab;
    error = '';
    success = '';
    if (tab === 'users') loadUsers();
    if (tab === 'stats') loadStats();
  }
</script>

<div class="admin-page">
  {#if !loggedIn}
    <div class="admin-login">
      <h1 class="admin-title">Admin</h1>
      <form onsubmit={(e) => { e.preventDefault(); login(); }}>
        <input
          type="password"
          bind:value={password}
          placeholder="Admin password"
          class="admin-input"
        />
        {#if loginError}
          <div class="admin-error">{loginError}</div>
        {/if}
        <button type="submit" class="admin-btn">Login</button>
      </form>
    </div>
  {:else}
    <div class="admin-header">
      <h1 class="admin-title">Admin Panel</h1>
      <button class="logout-btn" onclick={logout}>Logout</button>
    </div>

    <div class="admin-tabs">
      <button class:active={activeTab === 'results'} onclick={() => switchTab('results')}>Results</button>
      <button class:active={activeTab === 'users'} onclick={() => switchTab('users')}>Users</button>
      <button class:active={activeTab === 'stats'} onclick={() => switchTab('stats')}>Stats</button>
    </div>

    {#if error}
      <div class="admin-error">{error}</div>
    {/if}
    {#if success}
      <div class="admin-success">{success}</div>
    {/if}

    {#if activeTab === 'results'}
      <div class="results-entry">
        {#each categories as cat}
          {@const catWinners = cat.nominees.filter(n => n.is_winner)}
          <div class="cat-card" class:has-winner={catWinners.length > 0}>
            <div class="cat-card-header">
              <span class="cat-card-name">{cat.name}</span>
              {#if catWinners.length > 0}
                <button class="clear-btn" onclick={() => clearWinner(cat.id)}>Clear</button>
              {/if}
            </div>
            <div class="cat-card-nominees">
              {#each cat.nominees as nom}
                <button
                  class="nom-toggle"
                  class:is-winner={nom.is_winner}
                  onclick={() => {
                    if (nom.is_winner) {
                      // Remove this specific winner by clearing all and re-setting the others
                      clearWinner(cat.id).then(() => {
                        const others = catWinners.filter(w => w.id !== nom.id);
                        others.forEach(w => setWinner(cat.id, w.id));
                      });
                    } else {
                      setWinner(cat.id, nom.id);
                    }
                  }}
                >
                  <span class="nom-check">{nom.is_winner ? '\u2605' : '\u25CB'}</span>
                  <span class="nom-label">{nom.name}{nom.subtitle ? ` - ${nom.subtitle}` : ''}</span>
                </button>
              {/each}
            </div>
            {#if catWinners.length > 1}
              <div class="tie-badge">TIE</div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}

    {#if activeTab === 'users'}
      <div class="users-list">
        {#each users as u}
          <div class="user-card">
            <div class="user-card-top">
              <span class="user-card-name">{u.username}</span>
              <span class="user-card-status" class:submitted={u.submitted_at} class:draft={!u.submitted_at}>
                {u.submitted_at ? 'Cast' : 'Draft'}
              </span>
            </div>
            <div class="user-card-bottom">
              <span class="user-card-detail">Picks: {u.picks_count}/24</span>
              <span class="user-card-detail user-card-score">Score: {u.score}</span>
              <span class="user-card-actions">
                {#if confirmDeleteUser === u.id}
                  <button class="confirm-del-btn" onclick={() => deleteUser(u.id)}>Confirm</button>
                  <button class="cancel-del-btn" onclick={() => confirmDeleteUser = null}>Cancel</button>
                {:else}
                  <button class="del-btn" onclick={() => confirmDeleteUser = u.id}>Delete</button>
                {/if}
              </span>
            </div>
          </div>
        {/each}
        {#if users.length === 0}
          <div class="table-empty">No users yet.</div>
        {/if}
      </div>
    {/if}

    {#if activeTab === 'stats'}
      {#if stats}
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-num">{stats.total_users}</div>
            <div class="stat-label">Total users</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{stats.submitted}</div>
            <div class="stat-label">Ballots cast</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{stats.drafting}</div>
            <div class="stat-label">Still drafting</div>
          </div>
        </div>

        <h3 class="consensus-title">Consensus Picks</h3>
        <div class="consensus-list">
          {#each stats.category_stats as cs}
            <div class="consensus-row">
              <span class="consensus-cat">{cs.category}</span>
              <span class="consensus-pick">
                {cs.top_pick || '--'}
                {#if cs.top_pick_subtitle}
                  <span class="consensus-sub"> - {cs.top_pick_subtitle}</span>
                {/if}
                {#if cs.top_count > 0}
                  <span class="consensus-count">({cs.top_count})</span>
                {/if}
              </span>
            </div>
          {/each}
        </div>
      {:else}
        <div class="loading-text">Loading stats...</div>
      {/if}
    {/if}
  {/if}
</div>

<style>
  .admin-page {
    max-width: 800px;
    margin: 40px auto;
    padding: 0 16px;
  }

  .admin-login {
    max-width: 360px;
    margin: 120px auto;
    text-align: center;
  }

  .admin-title {
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 24px;
  }

  .admin-input {
    width: 100%;
    padding: 12px 16px;
    background: var(--black-surface);
    border: 1px solid var(--divider-light);
    color: var(--text);
    font-family: var(--font-body);
    font-size: 1rem;
    margin-bottom: 12px;
    outline: none;
  }

  .admin-input:focus {
    border-color: var(--gold-dim);
  }

  .admin-btn {
    width: 100%;
    padding: 12px;
    background: var(--gold);
    color: var(--black);
    border: none;
    font-family: var(--font-body);
    font-size: 1rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .admin-btn:hover {
    opacity: 0.9;
  }

  .admin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .logout-btn {
    background: none;
    border: 1px solid var(--red);
    color: var(--red-accent);
    padding: 6px 16px;
    font-family: var(--font-body);
    font-size: 0.85rem;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .admin-tabs {
    display: flex;
    gap: 0;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--divider-light);
  }

  .admin-tabs button {
    padding: 10px 20px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-dim);
    font-family: var(--font-body);
    font-size: 0.9rem;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .admin-tabs button.active {
    color: var(--gold);
    border-bottom-color: var(--gold);
  }

  .admin-error {
    padding: 10px 16px;
    background: rgba(128,27,29,0.15);
    border: 1px solid var(--red);
    color: var(--red-accent);
    font-size: 0.9rem;
    margin-bottom: 16px;
  }

  .admin-success {
    padding: 10px 16px;
    background: rgba(213,186,109,0.1);
    border: 1px solid var(--gold-dim);
    color: var(--gold);
    font-size: 0.9rem;
    margin-bottom: 16px;
  }

  /* Results Entry - Cards */
  .results-entry {
    display: grid;
    gap: 8px;
  }

  .cat-card {
    background: var(--black-card);
    border: 1px solid var(--divider);
    padding: 12px 16px;
  }

  .cat-card.has-winner {
    border-color: var(--gold-dim);
    background: rgba(213,186,109,0.05);
  }

  .cat-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .cat-card-name {
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gold);
  }

  .cat-card-nominees {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .nom-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 6px 8px;
    background: transparent;
    border: 1px solid transparent;
    color: var(--text);
    font-family: var(--font-body);
    font-size: 0.85rem;
    text-align: left;
    cursor: pointer;
    transition: all 0.15s;
  }

  .nom-toggle:hover {
    background: var(--hover);
  }

  .nom-toggle.is-winner {
    background: rgba(213,186,109,0.12);
    border-color: var(--gold-dim);
  }

  .nom-check {
    font-size: 0.85rem;
    color: var(--text-dim);
    width: 16px;
    text-align: center;
    flex-shrink: 0;
  }

  .nom-toggle.is-winner .nom-check {
    color: var(--gold);
  }

  .nom-label {
    flex: 1;
    min-width: 0;
  }

  .tie-badge {
    display: inline-block;
    margin-top: 8px;
    padding: 2px 8px;
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--gold);
    background: rgba(213,186,109,0.1);
    border: 1px solid var(--gold-dim);
    letter-spacing: 0.1em;
  }

  .clear-btn {
    padding: 3px 8px;
    background: none;
    border: 1px solid var(--red);
    color: var(--red-accent);
    font-size: 0.7rem;
    cursor: pointer;
    text-transform: uppercase;
    white-space: nowrap;
  }

  @media (min-width: 600px) {
    .results-entry {
      grid-template-columns: 1fr 1fr;
    }
  }

  /* Users - Card list */
  .users-list {
    display: grid;
    gap: 8px;
  }

  .user-card {
    background: var(--black-card);
    border: 1px solid var(--divider);
    padding: 12px 16px;
  }

  .user-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .user-card-name {
    font-weight: 500;
    font-size: 0.95rem;
  }

  .user-card-status {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .user-card-status.submitted { color: var(--gold); }
  .user-card-status.draft { color: var(--text-dim); }

  .user-card-bottom {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
  }

  .user-card-detail {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: var(--text-dim);
  }

  .user-card-score {
    color: var(--gold);
  }

  .user-card-actions {
    margin-left: auto;
    display: flex;
    gap: 4px;
  }

  .del-btn {
    padding: 3px 10px;
    background: none;
    border: 1px solid var(--red);
    color: var(--red-accent);
    font-size: 0.7rem;
    cursor: pointer;
    text-transform: uppercase;
  }

  .confirm-del-btn {
    padding: 3px 10px;
    background: var(--red);
    border: 1px solid var(--red-accent);
    color: var(--white);
    font-size: 0.7rem;
    cursor: pointer;
    text-transform: uppercase;
  }

  .cancel-del-btn {
    padding: 3px 10px;
    background: none;
    border: 1px solid var(--divider-light);
    color: var(--text-dim);
    font-size: 0.7rem;
    cursor: pointer;
    text-transform: uppercase;
  }

  .table-empty {
    padding: 20px;
    text-align: center;
    color: var(--text-dim);
  }

  /* Stats */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 32px;
  }

  .stat-card {
    background: var(--black-card);
    border: 1px solid var(--divider);
    padding: 16px 12px;
    text-align: center;
    min-width: 0;
  }

  .stat-num {
    font-family: var(--font-mono);
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--gold);
  }

  .stat-label {
    font-size: 0.7rem;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 4px;
  }

  .consensus-title {
    font-family: var(--font-display);
    font-size: 1rem;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
  }

  .consensus-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 12px;
    border-bottom: 1px solid var(--divider);
    font-size: 0.85rem;
  }

  .consensus-cat {
    color: var(--text-dim);
    flex: 1;
  }

  .consensus-pick {
    color: var(--text);
    flex: 1;
    text-align: right;
  }

  .consensus-sub {
    color: var(--text-dim);
    font-size: 0.8rem;
  }

  .consensus-count {
    color: var(--gold-dim);
    font-family: var(--font-mono);
    font-size: 0.8rem;
  }

  .loading-text {
    text-align: center;
    color: var(--text-dim);
    padding: 40px;
  }
</style>
