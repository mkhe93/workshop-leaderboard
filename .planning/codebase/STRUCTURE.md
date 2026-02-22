# Codebase Structure

**Analysis Date:** 2026-02-22

## Directory Layout

```text
/IdeaProjects/leaderboard/
├── backend/                 # FastAPI backend service
│   ├── src/
│   │   ├── api/             # FastAPI app factory and API response models
│   │   ├── client/          # HTTP client and Pydantic models for LiteLLM gateway
│   │   ├── services/        # Domain services and protocols
│   │   └── utils/           # Dependency config, date utilities, endpoint helpers, common config
│   └── tests/               # Python unit tests (not analyzed in detail here)
├── frontend/                # Vue 3 SPA frontend
│   ├── src/
│   │   ├── components/      # UI, layout, and feature components
│   │   │   ├── layouts/     # Layout components (header, navigation)
│   │   │   ├── ui/          # UI primitives (buttons, charts, messages)
│   │   │   └── features/    # Feature-level components (leaderboard, filters, charts)
│   │   ├── composables/     # Shared reactive state and data-fetching logic
│   │   ├── helpers/         # Pure helper and transformation functions
│   │   ├── router/          # Vue Router configuration
│   │   ├── styles/          # Global and variables CSS
│   │   └── views/           # Route-level view components
├── .planning/
│   └── codebase/            # Generated architecture/planning documents
├── .devcontainer/           # Devcontainer configuration
├── .github/workflows/       # CI/CD workflows
└── .opencode/, .claude/     # Tooling for AI-assisted workflows
```

## Directory Purposes

### `/IdeaProjects/leaderboard/backend/src/api`
- Purpose: Expose HTTP API surface and HTTP-level configuration.
- Contains:
  - `server.py` – FastAPI app factory and route handlers
  - `models.py` – Pydantic models for API I/O
  - `__init__.py` and `SOLUTION_server.py` (alternate implementation)
- Key files:
  - `/IdeaProjects/leaderboard/backend/src/api/server.py`
  - `/IdeaProjects/leaderboard/backend/src/api/models.py`

### `/IdeaProjects/leaderboard/backend/src/client`
- Purpose: Integrate with external LiteLLM gateway API.
- Contains:
  - `api_client.py` – `LiteLLMAPI` HTTP client
  - `models.py` – Pydantic models mirroring external API schema
  - `__init__.py`
- Key files:
  - `/IdeaProjects/leaderboard/backend/src/client/api_client.py`
  - `/IdeaProjects/leaderboard/backend/src/client/models.py`

### `/IdeaProjects/leaderboard/backend/src/services`
- Purpose: Implement backend domain logic and analytics operations.
- Contains:
  - `team_service.py` – team metadata fetching & caching
  - `team_daily_activity_service.py` – daily activity fetch & serialization
  - `token_aggregation_service.py` – aggregated token counts with breakdowns
  - `time_series_service.py` – daily time series transformation
  - `success_rate_service.py` – success-rate analytics
  - `cost_efficiency_service.py` – cost efficiency analytics
  - `protocols.py` – service and client interfaces (Protocols)
  - `SOLUTION_model_usage_service.py` – alternate solution implementation
  - `__init__.py`
- Key files:
  - `/IdeaProjects/leaderboard/backend/src/services/token_aggregation_service.py`
  - `/IdeaProjects/leaderboard/backend/src/services/time_series_service.py`
  - `/IdeaProjects/leaderboard/backend/src/services/success_rate_service.py`
  - `/IdeaProjects/leaderboard/backend/src/services/cost_efficiency_service.py`
  - `/IdeaProjects/leaderboard/backend/src/services/team_service.py`
  - `/IdeaProjects/leaderboard/backend/src/services/team_daily_activity_service.py`
  - `/IdeaProjects/leaderboard/backend/src/services/protocols.py`

### `/IdeaProjects/leaderboard/backend/src/utils`
- Purpose: Shared utilities and configuration wiring for the backend.
- Contains:
  - `dependency_config.py` – FastAPI dependency providers for services and client
  - `endpoint_utils.py` – common endpoint execution patterns (date-range logic, error mapping)
  - `date_utils.py` – date parsing and formatting helpers
  - `common.py` – configuration helpers for base URL and API key (not read but imported)
  - `SOLUTION_dependency_config.py` – alternate DI wiring
  - `__init__.py`
- Key files:
  - `/IdeaProjects/leaderboard/backend/src/utils/dependency_config.py`
  - `/IdeaProjects/leaderboard/backend/src/utils/endpoint_utils.py`
  - `/IdeaProjects/leaderboard/backend/src/utils/date_utils.py`

### `/IdeaProjects/leaderboard/backend/tests`
- Purpose: Backend tests (unit/integration).
- Contains: Test modules mirroring services (e.g., `tests/services/*`).
- Key files: Not fully enumerated here; follow the `tests/services/<service>_test.py` naming for adding new tests.

### `/IdeaProjects/leaderboard/frontend/src/components`
- Purpose: Component library for the frontend.
- Contains:
  - `layouts/` – app header, navigation, layout components
    - `/IdeaProjects/leaderboard/frontend/src/components/layouts/AppHeader.vue`
    - `/IdeaProjects/leaderboard/frontend/src/components/layouts/NavigationTabs.vue`
  - `ui/` – low-level reusable UI elements
    - `/IdeaProjects/leaderboard/frontend/src/components/ui/BaseButton.vue`
    - `/IdeaProjects/leaderboard/frontend/src/components/ui/BaseInput.vue`
    - `/IdeaProjects/leaderboard/frontend/src/components/ui/LoadingSpinner.vue`
    - `/IdeaProjects/leaderboard/frontend/src/components/ui/ErrorMessage.vue`
    - `/IdeaProjects/leaderboard/frontend/src/components/ui/BaseBarChart.vue`
  - `features/` – feature‑specific components organized by domain
    - `leaderboard/` – leaderboard table and rows
      - `/IdeaProjects/leaderboard/frontend/src/components/features/leaderboard/LeaderboardTable.vue`
      - `/IdeaProjects/leaderboard/frontend/src/components/features/leaderboard/TeamRow.vue`
      - `/IdeaProjects/leaderboard/frontend/src/components/features/leaderboard/TokenBar.vue`
      - `/IdeaProjects/leaderboard/frontend/src/components/features/leaderboard/TeamBreakdown.vue`
    - `filters/` – search and date range controls
      - `/IdeaProjects/leaderboard/frontend/src/components/features/filters/SearchInput.vue`
      - `/IdeaProjects/leaderboard/frontend/src/components/features/filters/DateRangeSelector.vue`
    - `charts/` – chart visuals and model filter UI
      - `/IdeaProjects/leaderboard/frontend/src/components/features/charts/TokenTypeBreakdown.vue`
      - `/IdeaProjects/leaderboard/frontend/src/components/features/charts/RequestSuccessSummary.vue`
      - `/IdeaProjects/leaderboard/frontend/src/components/features/charts/CostEfficiencyHeatmap.vue`
      - `/IdeaProjects/leaderboard/frontend/src/components/features/charts/ModelUsageChart.vue`
      - `/IdeaProjects/leaderboard/frontend/src/components/features/charts/ModelFilter.vue`
  - `SharedControls.vue` – composite control bar reused across views

### `/IdeaProjects/leaderboard/frontend/src/composables`
- Purpose: Global reactive state and data-fetching.
- Contains:
  - `useFilters.js` – cross‑route filter state synced with URL/localStorage
  - `useTokenData.js` – token aggregation + time series data source
  - `useModelData.js` – model usage data source
  - `useTeamSuccessRateData.js` – team success metrics data source
  - `useCostEfficiencyData.js` – cost efficiency data source
- Key files:
  - `/IdeaProjects/leaderboard/frontend/src/composables/useFilters.js`
  - `/IdeaProjects/leaderboard/frontend/src/composables/useTokenData.js`
  - `/IdeaProjects/leaderboard/frontend/src/composables/useModelData.js`

### `/IdeaProjects/leaderboard/frontend/src/helpers`
- Purpose: Reusable helper functions for data fetching and transformation.
- Contains:
  - `helpers.js` – leaderboard fetch, filtering, API-key masking, debounce
  - `barChartHelpers.js` – helpers for model chart data
  - `chartHelpers.js` – additional chart-specific helpers (not inspected)
- Key files:
  - `/IdeaProjects/leaderboard/frontend/src/helpers/helpers.js`
  - `/IdeaProjects/leaderboard/frontend/src/helpers/barChartHelpers.js`

### `/IdeaProjects/leaderboard/frontend/src/views`
- Purpose: Route‑level components (pages).
- Contains:
  - `LeaderboardView.vue` – leaderboard page
  - `ChartsView.vue` – analytics dashboard page
  - `*.test.js` – view-level tests for ChartsView
- Key files:
  - `/IdeaProjects/leaderboard/frontend/src/views/LeaderboardView.vue`
  - `/IdeaProjects/leaderboard/frontend/src/views/ChartsView.vue`

### `/IdeaProjects/leaderboard/frontend/src/router`
- Purpose: Vue Router configuration.
- Contains: `index.js` route definitions and router creation.
- Key files:
  - `/IdeaProjects/leaderboard/frontend/src/router/index.js`

### `/IdeaProjects/leaderboard/frontend/src/styles`
- Purpose: Global styling and CSS variables.
- Contains:
  - `variables.css` – CSS variables for colors, spacing, typography
  - `global.css` – base styles consumed in `main.js`
- Key files:
  - `/IdeaProjects/leaderboard/frontend/src/styles/global.css`
  - `/IdeaProjects/leaderboard/frontend/src/styles/variables.css`

### `/IdeaProjects/leaderboard/.planning/codebase`
- Purpose: Generated codebase documentation used by AI tooling.
- Contains:
  - `ARCHITECTURE.md`, `STRUCTURE.md`, and other mapping documents.

## Key File Locations

### Entry Points
- Backend app factory:
  - `/IdeaProjects/leaderboard/backend/src/api/server.py` – `create_backend()` used as ASGI entry
- Frontend app bootstrap:
  - `/IdeaProjects/leaderboard/frontend/src/main.js` – creates and mounts Vue app
- Frontend router:
  - `/IdeaProjects/leaderboard/frontend/src/router/index.js` – route definitions and history mode

### Configuration & Environment
- Backend dependency and environment wiring:
  - `/IdeaProjects/leaderboard/backend/src/utils/dependency_config.py` – DI bindings for services and API client
  - `/IdeaProjects/leaderboard/backend/src/utils/common.py` – base URL and API key retrieval (not fully inspected)
- Frontend environment usage:
  - `/IdeaProjects/leaderboard/frontend/src/helpers/helpers.js` – uses `import.meta.env.VITE_BACKEND_URL` and `SERVER_BASIC_AUTH_TOKEN`
  - `/IdeaProjects/leaderboard/frontend/src/composables/useTokenData.js` – same pattern for `/tokens/timeseries`
  - `/IdeaProjects/leaderboard/frontend/src/composables/useModelData.js` – same for `/tokens/models`

### Core Backend Logic
- Token aggregation and breakdown:
  - `/IdeaProjects/leaderboard/backend/src/services/token_aggregation_service.py`
- Time series aggregation:
  - `/IdeaProjects/leaderboard/backend/src/services/time_series_service.py`
- Success rate analytics:
  - `/IdeaProjects/leaderboard/backend/src/services/success_rate_service.py`
- Cost efficiency analytics:
  - `/IdeaProjects/leaderboard/backend/src/services/cost_efficiency_service.py`
- External API client & models:
  - `/IdeaProjects/leaderboard/backend/src/client/api_client.py`
  - `/IdeaProjects/leaderboard/backend/src/client/models.py`
- Endpoint utility & date formatting:
  - `/IdeaProjects/leaderboard/backend/src/utils/endpoint_utils.py`
  - `/IdeaProjects/leaderboard/backend/src/utils/date_utils.py`

### Core Frontend Logic
- Global filters and persistence:
  - `/IdeaProjects/leaderboard/frontend/src/composables/useFilters.js`
- Token data fetching & caching:
  - `/IdeaProjects/leaderboard/frontend/src/composables/useTokenData.js`
  - `/IdeaProjects/leaderboard/frontend/src/helpers/helpers.js`
- Model usage & cost/success metrics:
  - `/IdeaProjects/leaderboard/frontend/src/composables/useModelData.js`
  - `/IdeaProjects/leaderboard/frontend/src/composables/useTeamSuccessRateData.js`
  - `/IdeaProjects/leaderboard/frontend/src/composables/useCostEfficiencyData.js`
- Feature components:
  - Leaderboard: `/IdeaProjects/leaderboard/frontend/src/components/features/leaderboard/*`
  - Charts: `/IdeaProjects/leaderboard/frontend/src/components/features/charts/*`
  - Filters: `/IdeaProjects/leaderboard/frontend/src/components/features/filters/*`

### Testing
- Frontend tests (Jest/Vitest style):
  - `/IdeaProjects/leaderboard/frontend/src/components/features/filters/SearchInput.test.js`
  - `/IdeaProjects/leaderboard/frontend/src/components/features/filters/DateRangeSelector.test.js`
  - `/IdeaProjects/leaderboard/frontend/src/components/features/charts/TokenTypeBreakdown.test.js`
  - `/IdeaProjects/leaderboard/frontend/src/components/SharedControls.test.js`
  - `/IdeaProjects/leaderboard/frontend/src/helpers/helpers.test.js`
  - `/IdeaProjects/leaderboard/frontend/src/views/ChartsView.test.js`
- Backend tests:
  - `/IdeaProjects/leaderboard/backend/tests/**` – structured per service or functional area.

## Naming Conventions

### Files
- Backend Python:
  - Modules: `snake_case.py` (e.g., `token_aggregation_service.py`, `date_utils.py`)
  - Packages: `lowercase` with `__init__.py`
  - Protocol/solution variants: `SOLUTION_*.py` for reference implementations
- Frontend Vue/JS:
  - Vue components: `PascalCase.vue` (e.g., `LeaderboardTable.vue`, `SharedControls.vue`)
  - Composables: `useCamelCase.js` (e.g., `useFilters.js`, `useTokenData.js`)
  - Helpers: `camelCaseHelpers.js` or generic `helpers.js`
  - Router: `index.js` inside `router/`
  - Tests: Co‑located `*.test.js` next to components or helpers they cover

### Directories
- Backend:
  - Top‑level logical grouping by concern: `api`, `client`, `services`, `utils`.
  - Service modules named `<domain>_service.py`.
- Frontend:
  - Components grouped by role: `layouts`, `ui`, `features`.
  - Feature subdirectories named by domain: `leaderboard`, `filters`, `charts`.
  - Composables under `composables/` named `useXyz.js`.
  - Route‑level components in `views/` named `<RouteName>View.vue`.

## Where to Add New Code

### New Backend Endpoint
- Primary code:
  - Add the route handler to `/IdeaProjects/leaderboard/backend/src/api/server.py`.
  - Implement any non‑trivial logic in a new or existing service under `/IdeaProjects/leaderboard/backend/src/services/` (e.g., `new_feature_service.py`).
  - If the service needs external calls, extend `LiteLLMAPI` in `/IdeaProjects/leaderboard/backend/src/client/api_client.py` and, if necessary, add Pydantic models to `/IdeaProjects/leaderboard/backend/src/client/models.py`.
  - Add corresponding Pydantic request/response models to `/IdeaProjects/leaderboard/backend/src/api/models.py`.
  - Wire the service into DI in `/IdeaProjects/leaderboard/backend/src/utils/dependency_config.py` with a `get_<service_name>` function.
- Tests:
  - Place unit tests under `/IdeaProjects/leaderboard/backend/tests/` mirroring the module path, e.g., `tests/services/test_new_feature_service.py` or `tests/api/test_new_endpoint.py`.

### New Backend Service
- Implementation:
  - Create `/IdeaProjects/leaderboard/backend/src/services/<feature>_service.py`.
  - Define a class encapsulating domain logic and injecting needed protocols (`APIClientProtocol`, `TeamServiceProtocol`, etc.).
- Wiring:
  - Add a `get_<feature>_service` factory in `/IdeaProjects/leaderboard/backend/src/utils/dependency_config.py`.
  - If the service needs a new interface, add a `Protocol` to `/IdeaProjects/leaderboard/backend/src/services/protocols.py`.

### New Frontend View (Page)
- Primary code:
  - Create a new view component in `/IdeaProjects/leaderboard/frontend/src/views/`, e.g., `NewFeatureView.vue`.
  - Register a route in `/IdeaProjects/leaderboard/frontend/src/router/index.js` mapping a path (e.g., `/new-feature`) to the new view.
- Associated components:
  - Place reusable page‑specific components under `/IdeaProjects/leaderboard/frontend/src/components/features/<feature>/`.
- State & data:
  - If the view has cross‑page state or shared fetching logic, add a composable in `/IdeaProjects/leaderboard/frontend/src/composables/useNewFeatureData.js`.

### New Frontend Component/Module
- Implementation:
  - Leaf UI components (e.g., buttons, simple widgets) → `/IdeaProjects/leaderboard/frontend/src/components/ui/` with `PascalCase.vue` names.
  - Layout sections (headers/sidebars) → `/IdeaProjects/leaderboard/frontend/src/components/layouts/`.
  - Feature components bound to a specific domain → `/IdeaProjects/leaderboard/frontend/src/components/features/<domain>/`.
- Expose any shared logic as composables in `/IdeaProjects/leaderboard/frontend/src/composables/`.

### New Utility/Helper Functions
- Frontend:
  - For generic helpers (sorting, formatting, HTTP wrappers) → `/IdeaProjects/leaderboard/frontend/src/helpers/`.
  - For chart‑specific helpers → refine within `/IdeaProjects/leaderboard/frontend/src/helpers/` (e.g., `chartHelpers.js`, `barChartHelpers.js`).
- Backend:
  - Date or formatting utilities → `/IdeaProjects/leaderboard/backend/src/utils/date_utils.py` or a new module under `utils/`.
  - Endpoint patterns or HTTP error translation → extend `/IdeaProjects/leaderboard/backend/src/utils/endpoint_utils.py`.

## Special Directories

### `/IdeaProjects/leaderboard/backend/src/leaderboard.egg-info`
- Purpose: Packaging metadata for the backend Python package.
- Generated: Yes (by packaging tools such as `setuptools`).
- Committed: Yes (currently present in repo).

### `/IdeaProjects/leaderboard/frontend/dist`
- Purpose: Built frontend assets.
- Generated: Yes (by frontend build tooling).
- Committed: Appears present; verify `.gitignore` to decide if it should be committed.

### Tooling Directories
- `/IdeaProjects/leaderboard/.opencode` and `/IdeaProjects/leaderboard/.claude`
  - Purpose: Configuration and agent definitions for AI tooling.
  - Generated/maintained by tooling; not part of core product code.

---

*Structure analysis: 2026-02-22*
