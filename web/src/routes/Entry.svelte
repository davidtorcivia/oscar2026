<script>
  import { user, ballot, categories, currentView } from '../lib/stores.js';
  import { api } from '../lib/api.js';

  let username = $state('');
  let pin = $state('');
  let error = $state('');
  let loading = $state(false);

  async function handleSubmit() {
    error = '';
    if (!username.trim()) { error = 'Enter a username.'; return; }
    if (pin.length !== 4 || !/^\d{4}$/.test(pin)) { error = 'PIN must be exactly 4 digits.'; return; }

    loading = true;
    try {
      const data = await api.enter(username.trim(), pin);
      user.set({ user_id: data.user_id, username: data.username, submitted: data.submitted });
      ballot.set(data.ballot || {});

      const catData = await api.getCategories();
      categories.set(catData.categories);

      if (data.submitted) {
        currentView.set('results');
      } else {
        currentView.set('ballot');
      }
    } catch (err) {
      error = err.error || 'Something went wrong.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="entry-page">
  <div class="deco-frame">
    <div class="deco-corner tl"></div>
    <div class="deco-corner tr"></div>
    <div class="deco-corner bl"></div>
    <div class="deco-corner br"></div>

    <div class="entry-content">
      <div class="statuette">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Oscar_gold_silhouette.svg/120px-Oscar_gold_silhouette.svg.png" alt="Oscar statuette" width="50" height="120" />
      </div>

      <h1 class="title">98th Academy Awards</h1>
      <p class="subtitle">Make Your Picks.</p>

      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        <div class="field">
          <label for="username">Your Name</label>
          <input
            id="username"
            type="text"
            bind:value={username}
            placeholder="Enter your name"
            maxlength="30"
            autocomplete="off"
          />
        </div>

        <div class="field">
          <label for="pin">4-Digit PIN</label>
          <input
            id="pin"
            type="password"
            inputmode="numeric"
            pattern="[0-9]*"
            maxlength="4"
            bind:value={pin}
            placeholder="----"
            autocomplete="off"
          />
        </div>

        {#if error}
          <div class="error">{error}</div>
        {/if}

        <button type="submit" class="enter-btn" disabled={loading}>
          {loading ? 'Loading...' : 'Enter'}
        </button>
      </form>

      <p class="hint">New name? You'll create an account. Returning? Enter your PIN.</p>
    </div>
  </div>
</div>

<style>
  .entry-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 100px);
    padding: 20px;
  }

  .deco-frame {
    position: relative;
    background: var(--black-card);
    border: 1px solid var(--divider-light);
    padding: 48px 40px;
    max-width: 400px;
    width: 100%;
  }

  .deco-corner {
    position: absolute;
    width: 20px;
    height: 20px;
    border-color: var(--gold);
    border-style: solid;
  }
  .deco-corner.tl { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
  .deco-corner.tr { top: -1px; right: -1px; border-width: 2px 2px 0 0; }
  .deco-corner.bl { bottom: -1px; left: -1px; border-width: 0 0 2px 2px; }
  .deco-corner.br { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

  .entry-content {
    text-align: center;
  }

  .statuette {
    margin-bottom: 24px;
    opacity: 0.85;
  }

  .title {
    font-family: var(--font-display);
    font-size: 1.8rem;
    font-weight: 400;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
  }

  .subtitle {
    font-family: var(--font-display);
    font-size: 1.1rem;
    font-weight: 300;
    color: var(--text-dim);
    font-style: normal;
    margin-bottom: 32px;
    letter-spacing: 0.05em;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .field {
    text-align: left;
  }

  label {
    display: block;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--text-dim);
    margin-bottom: 6px;
  }

  input {
    width: 100%;
    padding: 12px 16px;
    background: var(--black-surface);
    border: 1px solid var(--divider-light);
    color: var(--text);
    font-family: var(--font-body);
    font-size: 1rem;
    outline: none;
    transition: border-color 0.2s;
  }

  input:focus {
    border-color: var(--gold);
  }

  input::placeholder {
    color: var(--gray-mid);
  }

  .error {
    color: var(--red-accent);
    font-size: 0.9rem;
    text-align: left;
  }

  .enter-btn {
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

  .enter-btn:hover:not(:disabled) {
    opacity: 0.9;
  }

  .enter-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .hint {
    margin-top: 20px;
    font-size: 0.8rem;
    color: var(--gray-mid);
  }

  @media (max-width: 480px) {
    .deco-frame {
      padding: 32px 24px;
    }
    .title {
      font-size: 1.4rem;
    }
  }
</style>
