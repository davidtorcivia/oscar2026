# Oscar Ballot -- 98th Academy Awards
## Design Document v1.1

---

## 1. Overview

A self-hosted web application for predicting Oscar winners. Users enter a username, fill out a ballot across all 24 categories, and track their score against a live leaderboard as results are announced. An admin backend allows entering official winners and viewing aggregate stats.

**Ceremony:** 98th Academy Awards (March 15, 2026)
**Host:** Conan O'Brien
**Venue:** Dolby Theatre at Ovation Hollywood

---

## 2. Architecture

```
                   Cloudflare (proxy/SSL)
                          |
                     Docker Host
                   +--------------+
                   |   Nginx      |  (reverse proxy, serves static)
                   |   :80/:443   |
                   +------+-------+
                          |
              +-----------+-----------+
              |                       |
     /api/*   |               /*      |
              v                       v
      +-------+--------+    +--------+--------+
      |  Flask API      |    | Svelte SPA      |
      |  (gunicorn)     |    | (static build)  |
      |  :5000          |    | served by nginx |
      +-------+---------+    +-----------------+
              |
      +-------+---------+
      |  SQLite          |
      |  /data/oscar.db  |
      +------------------+
```

### Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Frontend | Svelte 5 (Vite), vanilla CSS        |
| Backend  | Python 3.12, Flask, gunicorn        |
| Database | SQLite 3                            |
| Proxy    | Nginx (container) or Cloudflare     |
| Deploy   | Docker Compose (2 services + volume)|

### Why this stack
- Svelte compiles to vanilla JS -- zero runtime, fast on mobile
- Flask + SQLite = single-process, no connection pooling headaches, trivial backup (copy one file)
- The entire app fits in a ~150MB Docker image

---

## 3. Data Model

### Tables

```sql
PRAGMA foreign_keys = ON;

-- Nominees data (admin-editable)
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY,
    slug        TEXT UNIQUE NOT NULL,      -- "best-picture"
    name        TEXT NOT NULL,             -- "Best Picture"
    sort_order  INTEGER NOT NULL,          -- display ordering
    num_nominees INTEGER DEFAULT 5         -- 10 for Best Picture
);

CREATE TABLE nominees (
    id          INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,             -- "Sinners"
    subtitle    TEXT,                      -- "Ryan Coogler" or film name
    is_winner   BOOLEAN DEFAULT FALSE,
    UNIQUE(category_id, name)
);

-- User ballots
CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    username      TEXT UNIQUE COLLATE NOCASE NOT NULL,
    pin_hash      TEXT NOT NULL,            -- bcrypt hash of 4-digit PIN
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at  TIMESTAMP                 -- NULL until ballot is cast; locks ballot
);

CREATE TABLE picks (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    nominee_id  INTEGER NOT NULL REFERENCES nominees(id) ON DELETE CASCADE,
    picked_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, category_id)           -- one pick per category
);

-- Indexes
CREATE INDEX idx_picks_user ON picks(user_id);
CREATE INDEX idx_nominees_category ON nominees(category_id);
```

### Seeded Data

All 24 categories with nominees hardcoded on first run. Best Picture has 10 nominees; all others have 5. Full nominee list sourced from oscars.org/oscars/ceremonies/2026.

---

## 4. API Design

### Public Endpoints (no auth)

```
POST   /api/auth/enter          { username, pin }      -> { user_id, token, ballot }
POST   /api/auth/check                                 -> { user_id, username, submitted }  (cookie-based)
GET    /api/categories                                 -> { categories[] with nominees[] }
GET    /api/ballot/:user_id                            -> { picks[], score, total, submitted }
PUT    /api/ballot/:user_id     { picks: {cat_id: nominee_id, ...} }  -> { ok }  (save draft, rejected if submitted)
POST   /api/ballot/:user_id/submit  { picks: {cat_id: nominee_id, ...} }  -> { ok }  (final cast, locks ballot)
GET    /api/leaderboard                                -> { users[] with score, rank, submitted_at }
GET    /api/results                                    -> { categories[] with winner }
```

### Admin Endpoints (password auth)

```
POST   /api/admin/login         { password }           -> { session cookie }
GET    /api/admin/users                                -> { users[] with ballots, submitted_at }
GET    /api/admin/stats                                -> { participation, accuracy dist, category breakdown }
POST   /api/admin/winner        { category_id, nominee_id }  -> { ok }
DELETE /api/admin/winner        { category_id }        -> { ok }  (undo a result)
PUT    /api/admin/category/:id  { name, nominees[] }   -> { ok, warnings[] }  (see safety notes below)
POST   /api/admin/category      { name, nominees[] }   -> { ok }  (add category)
DELETE /api/admin/category/:id                         -> { ok }  (rejected if picks exist)
```

**Category edit safety:** When updating nominees via `PUT /api/admin/category/:id`, the API must handle existing picks. If a nominee is removed that users have already picked, the endpoint returns a `warnings` array listing affected users and requires a `force: true` flag to proceed (which deletes the orphaned picks). Nominees with `is_winner = true` cannot be removed without first clearing the winner.

### Auth Mechanics

**Users:** `POST /api/auth/enter` accepts `{ username, pin }`. If the username does not exist, a new user is created with the PIN (bcrypt-hashed). If the username exists, the PIN is verified against the stored hash -- wrong PIN returns 403. A signed cookie (`ballot_token`) is set containing the user_id. Returning visitors with a valid cookie skip the entry screen entirely; `POST /api/auth/check` validates the cookie and returns user state.

**Ballot lifecycle:**
1. User creates account (username + 4-digit PIN)
2. User fills out picks -- each selection auto-saves via `PUT /api/ballot/:user_id` (draft state)
3. User hits "Cast Ballot" -- `POST /api/ballot/:user_id/submit` sets `submitted_at` on the user record and permanently locks the ballot. All 24 categories must have a pick.
4. Once submitted, the ballot is immutable. The user sees their picks in read-only mode and can view the leaderboard/results.
5. If a user returns with a valid cookie to a submitted ballot, they land directly on the Results/Leaderboard view.

**Returning users without a cookie:** If someone clears cookies or uses a new device, they re-enter their username and PIN. The PIN verifies them and a new cookie is issued. Their existing ballot (submitted or draft) is restored.

**Admin:** Single password stored in env var `ADMIN_PASSWORD`. `POST /api/admin/login` sets a session cookie. All `/api/admin/*` routes check for valid session. No username, just a password field.

---

## 4a. Ballot Locking Rules

Ballots lock individually when the user clicks "Cast Ballot." There is no global lock. The rationale: since ballots are cast-once and immutable, there is no cheating window -- you either submitted before the winner was announced or you didn't. Late submissions are still allowed (a user could cast mid-ceremony and just miss the categories already announced), but their `submitted_at` timestamp is visible on the leaderboard, so social pressure handles the rest.

Tiebreaker: users with the same score are ranked by earlier `submitted_at`.

---

## 5. Frontend Design

### Aesthetic Direction: **Art Deco Cinema**

The Oscars' visual identity is gold, black, and glamour. We lean into that hard but with a modern dark-mode sensibility. Think: 1920s movie palace lobby, reimagined for a phone screen.

#### Color Palette

```css
:root {
    --gold:          #D4A843;
    --gold-bright:   #F5D675;
    --gold-dim:      #8B7332;
    --black:         #0A0A0A;
    --black-card:    #141414;
    --black-surface: #1A1A1A;
    --cream:         #F2E8D0;
    --cream-dim:     #B8A88A;
    --red:           #8B2020;
    --red-accent:    #C43030;
    --white:         #FAFAF5;
}
```

Everything is dark. Gold is used sparingly -- for borders, selected states, and the Oscar statuette motif. Red appears only as a danger/accent color for locked-in picks or admin actions.

#### Typography

- **Display/Headers:** A high-contrast Didone serif -- something like "Playfair Display" or "Cormorant Garamond" from Google Fonts. All-caps with generous letter-spacing for category headers.
- **Body/UI:** A clean geometric sans -- "DM Sans" or "Outfit". Readable on mobile, pairs well with the serif display face.
- **Monospace accent:** For scores and numbers -- "JetBrains Mono" or similar, tabular figures.

No emojis anywhere. Use typographic symbols: * for bullet, -- for dash, | for separator. Unicode stars or checkmarks where needed.

#### Key Visual Elements

- **Gold foil texture** as a subtle CSS gradient on the header/hero area
- **Art deco geometric lines** -- thin gold borders, chevron/sunburst patterns via CSS
- **Card-based category layout** with a slight gold border on hover
- **Selected nominee** gets a gold highlight bar and a checkmark (unicode)
- **Winner announced** state: gold fill with a statuette icon (SVG, not emoji)
- **Leaderboard** styled like a cinema marquee -- dark background, gold text, ranked entries

#### Layout & Responsive Behavior

**Mobile-first.** Three main views, all within the SPA:

1. **Entry Screen** -- centered, full-viewport. Username input and a 4-digit PIN field (masked, numeric keypad on mobile) with an art deco border frame. Headline: "98th Academy Awards" in large serif type. Subhead: "Make Your Picks." If username is new, creates account. If existing, PIN is verified. Error state for wrong PIN shown inline.

2. **Ballot View** -- vertical scroll through all 24 categories. Each category is a card:
   - Category name (gold, uppercase, serif)
   - 5 (or 10) nominee buttons in a stacked list
   - Selected nominee highlighted with gold bar
   - Tapping a different nominee changes the pick instantly
   - Progress indicator at top: "17/24 picked"
   - Sticky footer with "Cast Ballot" button (disabled until all 24 picked). Tapping triggers a confirmation dialog: "This is final. Once cast, your ballot cannot be changed." Confirm submits and redirects to Results view. Picks auto-save as drafts on each selection, so refreshing or losing connection doesn't lose progress.

3. **Results / Leaderboard View** -- shown after ballot is locked or when results start coming in:
   - Top section: user's score ("14/24") with a progress ring
   - Category-by-category breakdown: your pick vs. the winner (correct = gold, wrong = dim)
   - Leaderboard table below: rank, username, score
   - Live-ish: poll `/api/results` every 60s during the ceremony

**Desktop:** Same layout but categories render in a 2-column grid. Leaderboard gets a sidebar position.

#### Animations & Micro-interactions

- Page load: categories stagger in with a subtle fade-up (CSS animation-delay)
- Nominee selection: gold highlight slides in from left (CSS transition)
- Winner reveal: brief gold shimmer/pulse animation on the winning nominee
- Score counter: number ticks up with a CSS counter animation

All CSS-only. No JS animation libraries. Keep it fast.

---

## 6. Admin Panel

Accessible at `/admin`. Minimal, functional design -- same dark theme but without the art deco flourishes. Think: backstage vs. front-of-house.

### Admin Views

1. **Login** -- single password field, no username

2. **Dashboard**
   - Total users registered
   - Ballots cast vs. still drafting
   - Most-picked nominee per category (consensus picks)
   - Accuracy distribution histogram (once results are in)

3. **Results Entry**
   - List of all 24 categories
   - Each has a dropdown to select the winner from nominees
   - "Set Winner" button per category
   - Undo button to clear a winner
   - Visual indicator: categories with winners set vs. pending

4. **User Browser**
   - Table of all users, sortable by username / score / submitted_at
   - Visual indicator for draft vs. cast ballots
   - Click a user to see their full ballot side-by-side with results
   - Export to CSV button

5. **Category Editor**
   - Edit category names and nominees
   - Add/remove nominees (warns if users have picks on a nominee being removed; requires confirmation)
   - Add/remove categories (cannot delete a category that has any picks without force-confirm)
   - Reorder categories

---

## 7. Categories & Nominees (Seed Data)

All data sourced from oscars.org for the 98th Academy Awards.

### Best Picture (10 nominees)
1. Bugonia
2. F1
3. Frankenstein
4. Hamnet
5. Marty Supreme
6. One Battle after Another
7. The Secret Agent
8. Sentimental Value
9. Sinners
10. Train Dreams

### Directing
1. Chloe Zhao -- Hamnet
2. Josh Safdie -- Marty Supreme
3. Paul Thomas Anderson -- One Battle after Another
4. Joachim Trier -- Sentimental Value
5. Ryan Coogler -- Sinners

### Actor in a Leading Role
1. Timothee Chalamet -- Marty Supreme
2. Leonardo DiCaprio -- One Battle after Another
3. Ethan Hawke -- Blue Moon
4. Michael B. Jordan -- Sinners
5. Wagner Moura -- The Secret Agent

### Actress in a Leading Role
1. Jessie Buckley -- Hamnet
2. Rose Byrne -- If I Had Legs I'd Kick You
3. Kate Hudson -- Song Sung Blue
4. Renate Reinsve -- Sentimental Value
5. Emma Stone -- Bugonia

### Actor in a Supporting Role
1. Benicio Del Toro -- One Battle after Another
2. Jacob Elordi -- Frankenstein
3. Delroy Lindo -- Sinners
4. Sean Penn -- One Battle after Another
5. Stellan Skarsgard -- Sentimental Value

### Actress in a Supporting Role
1. Elle Fanning -- Sentimental Value
2. Inga Ibsdotter Lilleaas -- Sentimental Value
3. Amy Madigan -- Weapons
4. Wunmi Mosaku -- Sinners
5. Teyana Taylor -- One Battle after Another

### Writing (Original Screenplay)
1. Blue Moon -- Robert Kaplow
2. It Was Just an Accident -- Jafar Panahi
3. Marty Supreme -- Ronald Bronstein & Josh Safdie
4. Sentimental Value -- Eskil Vogt, Joachim Trier
5. Sinners -- Ryan Coogler

### Writing (Adapted Screenplay)
1. Bugonia -- Will Tracy
2. Frankenstein -- Guillermo del Toro
3. Hamnet -- Chloe Zhao & Maggie O'Farrell
4. One Battle after Another -- Paul Thomas Anderson
5. Train Dreams -- Clint Bentley & Greg Kwedar

### Animated Feature Film
1. Arco
2. Elio
3. KPop Demon Hunters
4. Little Amelie or the Character of Rain
5. Zootopia 2

### Animated Short Film
1. Butterfly
2. Forevergreen
3. The Girl Who Cried Pearls
4. Retirement Plan
5. The Three Sisters

### International Feature Film
1. Brazil -- The Secret Agent
2. France -- It Was Just an Accident
3. Norway -- Sentimental Value
4. Spain -- Sirat
5. Tunisia -- The Voice of Hind Rajab

### Documentary Feature Film
1. The Alabama Solution
2. Come See Me in the Good Light
3. Cutting through Rocks
4. Mr. Nobody against Putin
5. The Perfect Neighbor

### Documentary Short Film
1. All the Empty Rooms
2. Armed Only with a Camera
3. Children No More: "Were and Are Gone"
4. The Devil Is Busy
5. Perfectly a Strangeness

### Live Action Short Film
1. Butcher's Stain
2. A Friend of Dorothy
3. Jane Austen's Period Drama
4. The Singers
5. Two People Exchanging Saliva

### Casting (NEW CATEGORY)
1. Hamnet -- Nina Gold
2. Marty Supreme -- Jennifer Venditti
3. One Battle after Another -- Cassandra Kulukundis
4. The Secret Agent -- Gabriel Domingues
5. Sinners -- Francine Maisler

### Cinematography
1. Frankenstein -- Dan Laustsen
2. Marty Supreme -- Darius Khondji
3. One Battle after Another -- Michael Bauman
4. Sinners -- Autumn Durald Arkapaw
5. Train Dreams -- Adolpho Veloso

### Film Editing
1. F1 -- Stephen Mirrione
2. Marty Supreme -- Ronald Bronstein & Josh Safdie
3. One Battle after Another -- Andy Jurgensen
4. Sentimental Value -- Olivier Bugge Coutte
5. Sinners -- Michael P. Shawver

### Production Design
1. Frankenstein
2. Hamnet
3. Marty Supreme
4. One Battle after Another
5. Sinners

### Costume Design
1. Avatar: Fire and Ash -- Deborah L. Scott
2. Frankenstein -- Kate Hawley
3. Hamnet -- Malgosia Turzanska
4. Marty Supreme -- Miyako Bellizzi
5. Sinners -- Ruth E. Carter

### Makeup and Hairstyling
1. Frankenstein
2. Kokuho
3. Sinners
4. The Smashing Machine
5. The Ugly Stepsister

### Sound
1. F1
2. Frankenstein
3. One Battle after Another
4. Sinners
5. Sirat

### Visual Effects
1. Avatar: Fire and Ash
2. F1
3. Jurassic World Rebirth
4. The Lost Bus
5. Sinners

### Music (Original Score)
1. Bugonia -- Jerskin Fendrix
2. Frankenstein -- Alexandre Desplat
3. Hamnet -- Max Richter
4. One Battle after Another -- Jonny Greenwood
5. Sinners -- Ludwig Goransson

### Music (Original Song)
1. "Dear Me" -- Diane Warren: Relentless
2. "Golden" -- KPop Demon Hunters
3. "I Lied to You" -- Sinners
4. "Sweet Dreams of Joy" -- Viva Verdi!
5. "Train Dreams" -- Train Dreams

---

## 8. Deployment

### docker-compose.yml structure

```yaml
services:
  api:
    build: ./api
    environment:
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - db_data:/data
    expose:
      - "5000"

  web:
    build: ./web
    ports:
      - "80:80"
    depends_on:
      - api

volumes:
  db_data:
```

### Container: api
- Python 3.12-slim base
- Flask + gunicorn (2 workers, enough for SQLite) + bcrypt (PIN hashing)
- SQLite database mounted at /data/oscar.db
- Seeds categories/nominees on first run if DB is empty

### Container: web
- Node build stage (Svelte/Vite compile)
- Nginx runtime stage (serves static + proxies /api to Flask)

### Environment Variables
```
ADMIN_PASSWORD=<your-admin-password>
SECRET_KEY=<random-string-for-flask-sessions>
```

### Cloudflare
- Proxied A record pointing to VPS IP
- SSL termination at Cloudflare (Full Strict if you want, or Flexible)
- Nginx listens on 80, Cloudflare handles TLS

---

## 9. Cookie Strategy

| Cookie         | Purpose                    | HttpOnly | SameSite | MaxAge      |
|----------------|----------------------------|----------|----------|-------------|
| ballot_token   | Signed user_id for ballot  | Yes      | Lax      | 30 days     |
| admin_session  | Flask session for admin    | Yes      | Strict   | 8 hours     |

`ballot_token` is a Flask `itsdangerous` signed value containing the user_id. On page load, the Svelte app hits `POST /api/auth/check` which validates the cookie and returns user state (including whether the ballot is submitted), or 401 if invalid/missing, triggering the entry screen. Users who cleared cookies re-authenticate with username + PIN.

---

## 10. File Structure

```
oscar-ballot/
+-- docker-compose.yml
+-- .env
+-- api/
|   +-- Dockerfile
|   +-- requirements.txt
|   +-- app.py                 (Flask app factory)
|   +-- config.py              (env var loading)
|   +-- models.py              (SQLite schema + helpers)
|   +-- seed.py                (nominee data + seeding logic)
|   +-- routes/
|   |   +-- auth.py            (user enter/check)
|   |   +-- ballot.py          (picks CRUD)
|   |   +-- leaderboard.py     (scores + rankings)
|   |   +-- admin.py           (admin routes)
|   +-- middleware.py           (auth decorators)
+-- web/
    +-- Dockerfile
    +-- nginx.conf
    +-- package.json
    +-- vite.config.js
    +-- src/
    |   +-- App.svelte
    |   +-- main.js
    |   +-- lib/
    |   |   +-- api.js          (fetch wrappers)
    |   |   +-- stores.js       (Svelte stores: user, ballot, results)
    |   +-- routes/
    |   |   +-- Entry.svelte    (username prompt)
    |   |   +-- Ballot.svelte   (pick your winners)
    |   |   +-- Results.svelte  (scores + leaderboard)
    |   |   +-- Admin.svelte    (admin login + dashboard)
    |   +-- components/
    |   |   +-- CategoryCard.svelte
    |   |   +-- NomineeButton.svelte
    |   |   +-- Leaderboard.svelte
    |   |   +-- ProgressBar.svelte
    |   |   +-- Header.svelte
    |   |   +-- AdminCategoryRow.svelte
    |   |   +-- AdminUserTable.svelte
    +-- static/
        +-- oscar-statuette.svg
        +-- fonts/ (if self-hosting)
```

---

## 11. Resolved Decisions

1. **Ballot locking:** Ballots lock permanently on cast. No global lock needed. (See Section 4a.)

2. **User identity:** 4-digit PIN required at account creation. Prevents name collisions and accidental ballot overwrites.

3. **Tiebreaking:** Same score -> earlier `submitted_at` wins. Schema supports this via the `users.submitted_at` field.

4. **Case sensitivity:** `username TEXT UNIQUE COLLATE NOCASE` on the column itself ensures "Alex" and "alex" cannot coexist.

5. **Category edit safety:** Removing nominees or categories that have existing picks requires explicit admin confirmation. CASCADE deletes handle orphaned foreign keys in the schema, but the API layer gates this behind a `force` flag with warnings.

## 12. Remaining Considerations

1. **Real-time updates:** Polling every 60s is simple. WebSockets would be fancier but adds complexity for minimal gain in a <50 user scenario.

2. **Data backup:** SQLite file is in a Docker volume. A simple cron job copying the .db file is sufficient.

3. **Rate limiting:** Not critical for a friends-only deployment. Cloudflare's default protections are enough.

---

## 13. Constraints

- No emojis anywhere in the UI. Unicode symbols (checkmarks, stars, dashes) only.
- Dark mode only. No light mode toggle.
- Mobile-first responsive. Must be fully usable on a phone held vertically.
- All nominee data sourced from oscars.org official listings.
- 24 categories total (including debut Best Casting category).
- Best Picture has 10 nominees; all other categories have 5.
