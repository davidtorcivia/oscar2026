const BASE = '/api';

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: {},
    credentials: 'same-origin',
  };
  if (body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(`${BASE}${path}`, opts);
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, ...data };
  }
  return data;
}

export const api = {
  // Auth
  enter: (username, pin) => request('POST', '/auth/enter', { username, pin }),
  check: () => request('POST', '/auth/check'),
  logout: () => request('POST', '/auth/logout'),

  // Ballot
  getCategories: () => request('GET', '/categories'),
  getBallot: (userId) => request('GET', `/ballot/${userId}`),
  saveBallot: (userId, picks) => request('PUT', `/ballot/${userId}`, { picks }),
  submitBallot: (userId, picks) => request('POST', `/ballot/${userId}/submit`, { picks }),

  // Results
  getLeaderboard: () => request('GET', '/leaderboard'),
  getResults: () => request('GET', '/results'),

  // Admin
  adminLogin: (password) => request('POST', '/admin/login', { password }),
  adminLogout: () => request('POST', '/admin/logout'),
  adminCheck: () => request('GET', '/admin/check'),
  adminGetUsers: () => request('GET', '/admin/users'),
  adminGetStats: () => request('GET', '/admin/stats'),
  adminSetWinner: (category_id, nominee_id) => request('POST', '/admin/winner', { category_id, nominee_id }),
  adminClearWinner: (category_id) => request('DELETE', '/admin/winner', { category_id }),
  adminDeleteUser: (userId) => request('DELETE', `/admin/user/${userId}`),
};
