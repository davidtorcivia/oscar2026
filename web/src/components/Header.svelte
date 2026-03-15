<script>
  import { user, currentView } from '../lib/stores.js';
  import { api } from '../lib/api.js';

  let userData = $state(null);
  user.subscribe(u => userData = u);

  let view = $state('');
  currentView.subscribe(v => view = v);

  async function logout() {
    await api.logout();
    user.set(null);
    currentView.set('entry');
  }
</script>

<header>
  <div class="header-inner">
    <div class="brand" role="button" tabindex="0"
      onclick={() => {
        if (userData?.submitted) currentView.set('results');
        else if (userData) currentView.set('ballot');
        else currentView.set('entry');
      }}
      onkeydown={(e) => { if (e.key === 'Enter') e.currentTarget.click(); }}
    >
      <div class="brand-line">98th Academy Awards</div>
    </div>
    {#if userData}
      <div class="user-info">
        <span class="username">{userData.username}</span>
        <button class="logout-btn" onclick={logout}>Exit</button>
      </div>
    {/if}
  </div>
  <div class="gold-line"></div>
</header>

<style>
  header {
    margin-bottom: 24px;
  }

  .header-inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 16px 15px 12px;
    max-width: 960px;
    margin: 0 auto;
  }

  .brand {
    cursor: pointer;
  }

  .brand-line {
    font-family: var(--font-display);
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
    text-align: center;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .username {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--text-dim);
  }

  .logout-btn {
    font-family: var(--font-body);
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    background: none;
    border: 1px solid var(--divider-light);
    color: var(--text-dim);
    padding: 4px 12px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .logout-btn:hover {
    border-color: var(--gold-dim);
    color: var(--gold);
  }

  .gold-line {
    height: 1px;
    background: var(--gold-gradient);
    opacity: 0.4;
  }

  @media (min-width: 768px) {
    .header-inner {
      flex-direction: row;
      justify-content: center;
      position: relative;
      padding: 20px 20px;
    }

    .brand {
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
    }

    .user-info {
      margin-left: auto;
    }
  }
</style>
