<script>
  import { onMount } from 'svelte';
  import { user, ballot, categories, currentView, isAdmin } from './lib/stores.js';
  import { api } from './lib/api.js';
  import Header from './components/Header.svelte';
  import Entry from './routes/Entry.svelte';
  import Ballot from './routes/Ballot.svelte';
  import Results from './routes/Results.svelte';
  import Admin from './routes/Admin.svelte';

  let view = $state('loading');

  currentView.subscribe(v => view = v);

  onMount(async () => {
    // Check if URL is /admin
    if (window.location.pathname === '/admin') {
      try {
        await api.adminCheck();
        isAdmin.set(true);
        currentView.set('admin');
      } catch {
        currentView.set('admin');
      }
      return;
    }

    // Try to restore session from cookie
    try {
      const data = await api.check();
      user.set({ user_id: data.user_id, username: data.username, submitted: data.submitted });
      ballot.set(data.ballot || {});

      // Load categories
      const catData = await api.getCategories();
      categories.set(catData.categories);

      if (data.submitted) {
        currentView.set('results');
      } else {
        currentView.set('ballot');
      }
    } catch {
      currentView.set('entry');
    }
  });
</script>

{#if view !== 'loading' && view !== 'admin'}
  <Header />
{/if}

<main>
  {#if view === 'loading'}
    <div class="loading">
      <div class="loading-text">Loading...</div>
    </div>
  {:else if view === 'entry'}
    <Entry />
  {:else if view === 'ballot'}
    <Ballot />
  {:else if view === 'results'}
    <Results />
  {:else if view === 'admin'}
    <Admin />
  {/if}
</main>

<style>
  :global(*) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  :global(:root) {
    --gold:          #D5BA6D;
    --gold-bright:   #E2CC8A;
    --gold-dim:      #B69F66;
    --gold-gradient: linear-gradient(171.55deg, #D5BA6D 6.47%, #B69F66 93.53%);
    --black:         #000000;
    --black-card:    #0E0E0E;
    --black-surface: #161616;
    --hover:         #262626;
    --divider:       #292929;
    --divider-light: #494949;
    --text:          #FFFFFF;
    --text-dim:      #989898;
    --gray-mid:      #595959;
    --red:           #801B1D;
    --red-accent:    #A02224;
    --white:         #FFFFFF;
    --font-display:  'Jost', 'Futura PT', Futura, -apple-system, sans-serif;
    --font-body:     'Jost', 'Futura PT', Futura, -apple-system, sans-serif;
    --font-mono:     'JetBrains Mono', monospace;
  }

  :global(body) {
    background: var(--black);
    color: var(--text);
    font-family: var(--font-body);
    font-weight: 400;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  :global(a) {
    color: var(--gold);
    text-decoration: none;
  }

  main {
    max-width: 960px;
    margin: 0 auto;
    padding: 0 16px 100px;
  }

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }

  .loading-text {
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 300;
    color: var(--gold);
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
</style>
