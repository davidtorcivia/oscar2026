# Oscar Ballot - 98th Academy Awards

A self-hosted web app for predicting Oscar winners with friends. Enter a username, fill out a ballot across all 24 categories, and track scores on a live leaderboard as results are announced.

**Stack:** Svelte 5 + Flask + SQLite, deployed via Docker Compose.

## Quick Start

```bash
cp .env.example .env  # edit ADMIN_PASSWORD and SECRET_KEY
docker compose up -d
```

App runs on port 9010. Admin panel at `/admin`.

## Notes

- This was vibe-coded for a single Oscar night with friends. It is not security tested, pen-tested, or production-hardened. Do not deploy this on the open internet expecting it to withstand abuse.
- The 24 categories and all nominees are **hardcoded** in `api/seed.py` for the 98th Academy Awards (2026). To use this for a different year, edit that file before first run.
- Auth is a 4-digit PIN. It's meant to stop your friends from messing with each other's ballots, not to protect state secrets.
- SQLite is the database. It lives in a Docker volume. Back it up by copying the file.

## License

MIT
