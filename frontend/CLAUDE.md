# Claude instructions (frontend)

Frontend is a **Vue 3** SPA built with **Vite**. It displays a leaderboard and charts by calling the backend’s `/tokens*` endpoints.

## Architecture map

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.js               # Entry point
│   ├── App.vue               # App shell
│   ├── router/
│   │   └── index.js          # Route definitions
│   ├── views/                # Route-level components
│   │   ├── LeaderboardView.vue
│   │   └── ChartsView.vue
│   ├── components/
│   │   ├── SharedControls.vue
│   │   └── features/         # Feature-specific components
│   │       ├── leaderboard/
│   │       ├── charts/
│   │       └── filters/
│   ├── composables/          # Shared state + data fetching
│   │   ├── useFilters.js     # URL + localStorage synced filters
│   │   ├── useTokenData.js
│   │   └── useModelData.js
│   └── helpers/
│       └── helpers.js        # HTTP helpers, utilities
└── (tests co-located as *.test.js)
```

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
npm run build
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
