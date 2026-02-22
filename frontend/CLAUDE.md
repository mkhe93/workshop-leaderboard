# Claude instructions (frontend)

Frontend is a **Vue 3** SPA built with **Vite**. It displays a leaderboard and charts by calling the backend’s `/tokens*` endpoints.

## Architecture map

- Entry: `frontend/src/main.js`
- App shell: `frontend/src/App.vue`
- Routes: `frontend/src/router/index.js`
- Views:
  - `frontend/src/views/LeaderboardView.vue`
  - `frontend/src/views/ChartsView.vue`
- Shared controls (filters): `frontend/src/components/SharedControls.vue`
- Feature components:
  - Leaderboard: `frontend/src/components/features/leaderboard/*`
  - Charts: `frontend/src/components/features/charts/*`
  - Filters: `frontend/src/components/features/filters/*`
- Data + state:
  - `frontend/src/composables/useFilters.js` (URL + localStorage synced)
  - `frontend/src/composables/useTokenData.js`
  - `frontend/src/composables/useModelData.js`
  - plus success-rate / cost-efficiency composables
- HTTP helpers: `frontend/src/helpers/helpers.js`

## Commands

From `frontend/`:

```bash
npm ci

# dev server
npm run dev

# unit tests
npm test

# lint
npm run lint

# build
```

## Environment variables

Used by frontend code:
- `VITE_BACKEND_URL` — base URL for backend API (`frontend/src/helpers/helpers.js`)
- `VITE_LEADERBOARD_FRONTEND_PORT` — Vite dev server port (`frontend/vite.config.js`)
- `VITE_WORKSHOP_USER` — used to construct `allowedHosts` (`frontend/vite.config.js`)
- `SERVER_BASIC_AUTH_TOKEN` — optional auth token; added to requests only when backend is not localhost (`frontend/src/helpers/helpers.js`)

## Implementation guidance

- Keep route-level orchestration in `frontend/src/views/`.
- Keep reusable, presentational components in `frontend/src/components/`.
- Put shared state + fetching in `frontend/src/composables/`.
- Prefer pure transformations in `frontend/src/helpers/`.

## Testing guidance

- Unit tests use Vitest + Vue Test Utils.
- Tests are co-located as `*.test.js` next to the unit.
- Prefer mocking:
  - chart components (`vue-chartjs`) to keep DOM deterministic
  - composables that fetch remote data, returning stable `ref` values

## Safety / secrets

Do not hardcode tokens or API keys in frontend code. Treat `SERVER_BASIC_AUTH_TOKEN` as sensitive in any real deployment.
