import { writable } from 'svelte/store';

// User state
export const user = writable(null);       // { user_id, username, submitted }
export const ballot = writable({});       // { cat_id: nominee_id, ... }
export const categories = writable([]);   // full category list with nominees
export const results = writable([]);      // categories with winners
export const leaderboard = writable([]);  // sorted user scores

// App state
export const currentView = writable('loading'); // loading, entry, ballot, results, admin
export const isAdmin = writable(false);
