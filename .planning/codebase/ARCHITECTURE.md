# Architecture

**Analysis Date:** 2026-02-22

## Pattern Overview

**Overall:** Client–Server dashboard with modular service layer

**Key Characteristics:**
- Vue 3 SPA frontend in `frontend/src` consuming a FastAPI backend in `backend/src`
- Backend organized into clear API, service, client, and utility layers with dependency injection
- Data flow built around date‑range queries into a LiteLLM gateway and aggregation in services

## Layers

### Frontend Application Shell
- Purpose: Bootstrap Vue app, register router, provide overall layout and shared controls
- Location: `/IdeaProjects/leaderboard/frontend/src`
- Contains: Root component, router, global styles
- Depends on: Vue 3, Vue Router, composables, feature components
- Used by: Browser entry at `index.html` (not in repo but implied by Vite/Vue tooling)

Key files:
- `/IdeaProjects/leaderboard/frontend/src/main.js` – creates and mounts the Vue app
- `/IdeaProjects/leaderboard/frontend/src/App.vue` – application shell (header, tabs, router view)
- `/IdeaProjects/leaderboard/frontend/src/router/index.js` – route definitions

### Frontend Views & Features
- Purpose: Encapsulate page‑level views and feature components for leaderboard and charts
- Location: `/IdeaProjects/leaderboard/frontend/src/views`, `/IdeaProjects/leaderboard/frontend/src/components`
- Contains: Route views, feature components (leaderboard, charts, filters), UI primitives
- Depends on: Composables in `/frontend/src/composables`, helper functions in `/frontend/src/helpers`, backend HTTP endpoints
- Used by: Router and root layout

Examples:
- `/IdeaProjects/leaderboard/frontend/src/views/LeaderboardView.vue` – leaderboard page using token data and filters
- `/IdeaProjects/leaderboard/frontend/src/views/ChartsView.vue` – analytics page orchestrating multiple chart components and data sources
- `/IdeaProjects/leaderboard/frontend/src/components/features/leaderboard/LeaderboardTable.vue` – renders token leaderboard with expandable team breakdown rows
- `/IdeaProjects/leaderboard/frontend/src/components/features/charts/TokenTypeBreakdown.vue` – stacked bar chart per team for prompt vs completion tokens
- `/IdeaProjects/leaderboard/frontend/src/components/features/charts/RequestSuccessSummary.vue` – per‑team success rate doughnut charts
- `/IdeaProjects/leaderboard/frontend/src/components/features/charts/CostEfficiencyHeatmap.vue` – bubble chart of cost‑efficiency per team/model
- `/IdeaProjects/leaderboard/frontend/src/components/features/charts/ModelUsageChart.vue` – wrapper around a base bar chart for model usage
- `/IdeaProjects/leaderboard/frontend/src/components/SharedControls.vue` – search + date range controls shared across views
- `/IdeaProjects/leaderboard/frontend/src/components/layouts/AppHeader.vue` – header layout (slots for title, controls, subtitle)
- `/IdeaProjects/leaderboard/frontend/src/components/layouts/NavigationTabs.vue` – tabs that switch between `/leaderboard` and `/chart`
- `/IdeaProjects/leaderboard/frontend/src/components/ui/*.vue` – UI primitives (buttons, inputs, charts, loading, errors)

### Frontend State & Data Layer
- Purpose: Centralize cross‑view state (filters) and API data fetching with caching
- Location: `/IdeaProjects/leaderboard/frontend/src/composables`, `/IdeaProjects/leaderboard/frontend/src/helpers`
- Contains: Composables for filters and data fetching, helper functions for HTTP and chart data transformation
- Depends on: Browser APIs (`localStorage`, `fetch`), `import.meta.env` configuration, backend endpoints
- Used by: Views and feature components

Key abstractions:
- `/IdeaProjects/leaderboard/frontend/src/composables/useFilters.js`
  - Holds shared `searchTerm`, `startDate`, and `endDate` state
  - Syncs with URL query params and `localStorage`
  - Persists last active view name
- `/IdeaProjects/leaderboard/frontend/src/composables/useTokenData.js`
  - Fetches aggregated team tokens and time‑series data (`/tokens` and `/tokens/timeseries`)
  - Provides shared reactive `data`, `timeSeriesData`, `loading`, `error`
  - Implements in‑memory caching keyed by `startDate-endDate`
- `/IdeaProjects/leaderboard/frontend/src/composables/useModelData.js`
  - Fetches model‑level usage from `/tokens/models`, with caching
- `/IdeaProjects/leaderboard/frontend/src/composables/useTeamSuccessRateData.js` (present but not read; mirrors other composables)
- `/IdeaProjects/leaderboard/frontend/src/composables/useCostEfficiencyData.js` (present but not read; mirrors other composables)
- `/IdeaProjects/leaderboard/frontend/src/helpers/helpers.js`
  - `fetchLeaderboard` to call `/tokens` and normalize/sort team data
  - `filterTeamsByName` for comma‑separated search
  - `maskApiKey` for securely displaying API keys
  - `debounce` utility
- `/IdeaProjects/leaderboard/frontend/src/helpers/barChartHelpers.js`
  - `transformToBarChartData` – chart.js bar data assembly
  - `filterModelsByTeam` – filters model usage based on team breakdown and search term

### Backend API Layer
- Purpose: Define HTTP endpoints, HTTP‑level concerns (CORS, errors), and map requests to services
- Location: `/IdeaProjects/leaderboard/backend/src/api`
- Contains: FastAPI app factory, Pydantic response/request models
- Depends on: FastAPI, Pydantic, services, dependency configuration, endpoint utilities
- Used by: ASGI server (uvicorn/gunicorn) entrypoint that imports `create_backend`

Key files:
- `/IdeaProjects/leaderboard/backend/src/api/server.py`
  - `create_backend()` builds a `FastAPI` app
  - Adds CORS middleware with allowed origins built from `VITE_WORKSHOP_USER` and `VITE_LEADERBOARD_FRONTEND_PORT` environment variables
  - Loads environment variables via `dotenv.load_dotenv`
  - Declares endpoints:
    - `GET /tokens` → returns `TeamsOut` built from `TokenAggregationService.fetch_total_tokens_per_team`
    - `GET /tokens/timeseries` → returns `TimeSeriesOut` built from `TimeSeriesService.fetch_daily_timeseries_per_team`
    - `GET /tokens/models` → currently returns dummy `ModelsOut` (no service integration yet)
    - `GET /tokens/success-rate` → returns `SuccessRateSummaryOut` from `SuccessRateService.fetch_team_success_rate_summary`
    - `GET /tokens/cost-efficiency` → returns `CostEfficiencyOut` from `CostEfficiencyService.fetch_cost_efficiency`
    - `GET /tokens/hourly` → returns `HourlyBreakdownOut` from inline synthetic data
  - All date‑range endpoints use `execute_date_range_endpoint` to handle validation, parsing, and error mapping
- `/IdeaProjects/leaderboard/backend/src/api/models.py`
  - Pydantic models for API responses:
    - Aggregated team tokens with nested breakdown (`TeamOut`, `TeamsOut`, `TeamBreakdown`, `ApiKeyBreakdown`, `ModelUsage`)
    - Time series (`DailyTeamTokens`, `DailyTimeSeriesPoint`, `TimeSeriesOut`)
    - Date range validation (`DateRangeParams` with multiple field validators)
    - Success rate and cost efficiency (`TeamSuccessRate`, `SuccessRateSummaryOut`, `CostEfficiencyCell`, `CostEfficiencyOut`)
    - Hourly aggregation (`HourlyBucket`, `HourlyBreakdownOut`)

### Backend Service Layer
- Purpose: Encapsulate domain logic for aggregating LiteLLM gateway data into API‑friendly shapes
- Location: `/IdeaProjects/leaderboard/backend/src/services`
- Contains: Services for teams, token aggregation, time series, success rate, cost efficiency, protocols for loose coupling
- Depends on: `APIClientProtocol`, `TeamServiceProtocol`, client models
- Used by: API endpoints via dependency injection from `dependency_config`

Key services:
- `/IdeaProjects/leaderboard/backend/src/services/team_service.py`
  - Manages team metadata and mappings
  - Fetches teams from API client (`LiteLLMAPI`) and caches:
    - `_teams`: list of `TeamResponse`
    - `_team_ids`: list of team ids
    - `_team_id_to_name`: id → alias
  - Exposes `fetch_teams`, `get_team_ids`, `get_team_name`
- `/IdeaProjects/leaderboard/backend/src/services/team_daily_activity_service.py`
  - Wraps periodic team activity fetch
  - `fetch_daily_activity` → returns JSON‑serializable dict for daily activity across teams
- `/IdeaProjects/leaderboard/backend/src/services/token_aggregation_service.py`
  - `fetch_total_tokens_per_team(start_date, end_date)`
  - Uses `TeamServiceProtocol` to get team ids and names, and `APIClientProtocol.fetch_team_daily_activity` to pull daily breakdown
  - Aggregates `total_tokens` per team and builds `breakdown.api_keys[*].models[*]` structures combining metrics and key aliases
  - Private helpers `_extract_breakdown` and `_merge_breakdown` understand LiteLLM breakdown schema (`entities`, `model_groups`, `api_keys`)
- `/IdeaProjects/leaderboard/backend/src/services/time_series_service.py`
  - `fetch_daily_timeseries_per_team(start_date, end_date)`
  - Converts `SpendAnalyticsPaginatedResponse` into a list of `{date, teams:[{name, tokens, total_requests, successful_requests, failed_requests}]}` suitable for `TimeSeriesOut`
- `/IdeaProjects/leaderboard/backend/src/services/success_rate_service.py`
  - `fetch_team_success_rate_summary(start_date, end_date)`
  - Aggregates `api_requests`, `successful_requests`, `failed_requests` across all daily results per team
  - Computes `success_rate` percentage per team
- `/IdeaProjects/leaderboard/backend/src/services/cost_efficiency_service.py`
  - `fetch_cost_efficiency(start_date, end_date)`
  - Analyzes `breakdown.model_groups[*].api_key_breakdown[*].metrics` for each team’s API keys
  - Builds `cells` of `{team, model, cost_per_1k_tokens, total_cost, total_tokens}`
- `/IdeaProjects/leaderboard/backend/src/services/protocols.py`
  - Structural protocols for `APIClientProtocol`, `TeamServiceProtocol`, `ModelMappingServiceProtocol`, `TeamDailyActivityServiceProtocol`
  - Make services testable and decoupled from `LiteLLMAPI` and concrete team services

### Backend Client Layer
- Purpose: Encapsulate HTTP calls to the external LiteLLM gateway and parse responses into typed models
- Location: `/IdeaProjects/leaderboard/backend/src/client`
- Contains: HTTP client and Pydantic models representing the external API
- Depends on: `requests`, Pydantic
- Used by: Dependency configuration and services via protocols

Key files:
- `/IdeaProjects/leaderboard/backend/src/client/api_client.py` (LiteLLMAPI)
  - Methods:
    - `fetch_teams()` → `/team/list` endpoint, validates into list of `TeamResponse`
    - `fetch_team_daily_activity(team_ids, start_date, end_date, page_size)` → `/team/daily/activity` endpoint, validates into `SpendAnalyticsPaginatedResponse`
    - `fetch_model_info()` → `/model/info` or `/v1/model/info`, validates into `ModelInfoResponse`
  - Handles 401 auth errors distinctively and checks pagination (`metadata.total_pages`)
- `/IdeaProjects/leaderboard/backend/src/client/models.py`
  - Pydantic models for spend metrics, breakdowns, daily results, metadata, team schema, and model info
  - Types mirror LiteLLM’s OpenAPI specification

### Backend Utilities & Configuration
- Purpose: Cross‑cutting utilities and wiring for dependency injection and endpoint patterns
- Location: `/IdeaProjects/leaderboard/backend/src/utils`
- Contains: DI configuration, date utilities, endpoint helper, common config helpers
- Depends on: FastAPI `Depends`, environment configuration, client/services
- Used by: API layer and services

Key files:
- `/IdeaProjects/leaderboard/backend/src/utils/dependency_config.py`
  - Provides DI factories using `functools.lru_cache` and `fastapi.Depends`
  - `get_api_client()` creates singleton `LiteLLMAPI` with `get_base_url()` and `get_api_key()` from `src.utils.common`
  - Provides typed getters for `TeamService`, `TeamDailyActivityService`, and all analytics services
- `/IdeaProjects/leaderboard/backend/src/utils/endpoint_utils.py`
  - `execute_date_range_endpoint(start_date, end_date, service_method)`
    - Wraps date validation (`DateRangeParams`) and parsing (`parse_date_range`)
    - Formats dates for the LiteLLM API (`format_date_for_api`, `format_date_for_api_end`)
    - Catches `RuntimeError` and general `Exception` and maps into `HTTPException` with appropriate status codes (400/502/500)
- `/IdeaProjects/leaderboard/backend/src/utils/date_utils.py`
  - `parse_date_range` – defaulting, validation, and expansion of a date range
  - `format_date_for_api` – `YYYY.MM.DD` format for LiteLLM start date
  - `format_date_for_api_end` – ISO8601 datetime string for end date
- `/IdeaProjects/leaderboard/backend/src/utils/common.py` (not read, inferred from imports) – likely wraps environment access for base URL and API key

## Data Flow

### Token Leaderboard (Aggregated Tokens)

1. User selects date range and search term in `SharedControls` (`/frontend/src/components/SharedControls.vue`).
2. `useFilters` (`/frontend/src/composables/useFilters.js`) updates reactive `startDate`/`endDate`, writes to URL and `localStorage`.
3. `LeaderboardView` (`/frontend/src/views/LeaderboardView.vue`) watches `startDate`/`endDate` and calls `refresh()` → `useTokenData.retry(startDate, endDate)`.
4. `useTokenData.fetchData(startDate, endDate)` (`/frontend/src/composables/useTokenData.js`):
   - Builds cache key and returns cached data if present.
   - Calls `fetchLeaderboard(startDate, endDate)` (`/frontend/src/helpers/helpers.js`).
5. `fetchLeaderboard` issues HTTP GET to `${VITE_BACKEND_URL}/tokens?start_date=...&end_date=...` with optional `Authorization` header.
6. FastAPI app (`create_backend` in `/backend/src/api/server.py`) matches `GET /tokens`:
   - Injects `TokenAggregationService` via `get_token_aggregation_service`.
   - Delegates to `execute_date_range_endpoint(start_date, end_date, service.fetch_total_tokens_per_team)`.
7. `execute_date_range_endpoint` (`/backend/src/utils/endpoint_utils.py`):
   - Validates dates with `DateRangeParams` (`/backend/src/api/models.py`).
   - Parses into datetimes via `parse_date_range` (`/backend/src/utils/date_utils.py`).
   - Formats for LiteLLM API and calls `TokenAggregationService.fetch_total_tokens_per_team`.
8. `TokenAggregationService.fetch_total_tokens_per_team` (`/backend/src/services/token_aggregation_service.py`):
   - Uses `TeamService.get_team_ids` to query teams via `LiteLLMAPI.fetch_teams` if needed.
   - Calls `LiteLLMAPI.fetch_team_daily_activity(team_ids, start, end)` to obtain `SpendAnalyticsPaginatedResponse`.
   - Aggregates `total_tokens` per team and constructs breakdown by API key/model.
9. API endpoint maps service result into `TeamsOut` (`/backend/src/api/models.py`), which Pydantic serializes to JSON.
10. Frontend helper parses response JSON, sorts teams, annotates medals, and returns to composable.
11. `LeaderboardView` computes `filteredTeams` using `filterTeamsByName` and `maxTokens`, and passes into `LeaderboardTable`.
12. `LeaderboardTable` (`/frontend/src/components/features/leaderboard/LeaderboardTable.vue`) and `TeamRow`/`TokenBar` render rows and proportional bars, `TeamBreakdown` shows breakdown per API key/model.

### Time Series & Charts

1. Same filters from `useFilters` drive `ChartsView` (`/frontend/src/views/ChartsView.vue`).
2. `ChartsView` watches `[startDate, endDate]` and, on initialization and change, triggers:
   - `useTokenData.fetchData(startDate, endDate)` → aggregated data + `/tokens/timeseries` for `timeSeriesData`.
   - `useModelData.fetchData(startDate, endDate)` → `/tokens/models`.
   - `useTeamSuccessRateData.fetchData(startDate, endDate)` → `/tokens/success-rate`.
   - `useCostEfficiencyData.fetchData(startDate, endDate)` → `/tokens/cost-efficiency`.
3. Backend endpoints:
   - `/tokens/timeseries` uses `TimeSeriesService.fetch_daily_timeseries_per_team`, which transforms LiteLLM daily results into `TimeSeriesOut.timeseries` by joining entity metrics to team names.
   - `/tokens/models` currently returns `ModelsOut` with default dummy `ModelUsageOut`.
   - `/tokens/success-rate` uses `SuccessRateService.fetch_team_success_rate_summary`, aggregating requests and computing success rates.
   - `/tokens/cost-efficiency` uses `CostEfficiencyService.fetch_cost_efficiency`, aggregating costs/tokens and computing `cost_per_1k_tokens`.
4. Chart components consume the composables’ data:
   - `TokenTypeBreakdown` transforms team breakdowns into stacked bar datasets.
   - `RequestSuccessSummary` renders one doughnut per team from success rate summaries.
   - `CostEfficiencyHeatmap` maps cost efficiency cells into bubble chart points (x = tokens, y = cost per million, r = total cost) grouped by team.
   - `ModelUsageChart` displays bar chart of model usage, with data pre‑filtered and transformed in `ChartsView` using `transformToBarChartData` and `filterModelsByTeam`.

### Filters & URL Persistence

- `useFilters` ensures a consistent filter state across routes and reloads:
  1. On first use, it reads query parameters (`search`, `start`, `end`) from current route.
  2. Fills any missing fields from `localStorage` or defaults to last 24 hours.
  3. If route path is `/`, it redirects to saved view (`/leaderboard` or `/chart`).
  4. Watches `[searchTerm, startDate, endDate]` and updates both `localStorage` and router query.
  5. Watches `route.name` and persists active view name.

## Key Abstractions

### Service Protocols
- Purpose: Allow services to depend on behavior contracts (API client, team data, model mapping) rather than concrete classes.
- Examples: `/IdeaProjects/leaderboard/backend/src/services/protocols.py`
- Pattern: Python typing `Protocol` with method signatures; concrete classes like `LiteLLMAPI` and `TeamService` satisfy them structurally.

### Dependency Configuration
- Purpose: Centralize wiring of concrete implementations into the FastAPI dependency system.
- Examples: `/IdeaProjects/leaderboard/backend/src/utils/dependency_config.py`
- Pattern: `get_*` factory functions returning concrete services, some cached via `@lru_cache()`, used with `Depends(get_*)` in API endpoints.

### Endpoint Utility
- Purpose: DRY pattern for endpoints that take date ranges and call services.
- Examples: `/IdeaProjects/leaderboard/backend/src/utils/endpoint_utils.py`
- Pattern: Function `execute_date_range_endpoint` parameterized by `service_method`, handling:
  - Date validation (Pydantic model)
  - Date range expansion/parsing
  - Format conversion for downstream APIs
  - Exception translation into HTTP status codes

### Frontend Composables
- Purpose: Encapsulate reactive state and side‑effects (HTTP, caching) for reuse across components.
- Examples:
  - `/IdeaProjects/leaderboard/frontend/src/composables/useFilters.js`
  - `/IdeaProjects/leaderboard/frontend/src/composables/useTokenData.js`
  - `/IdeaProjects/leaderboard/frontend/src/composables/useModelData.js`
- Pattern: Module‑level `ref` state shared across all consumers; exported `fetchData`, `retry`, `invalidateCache` functions; watchers internal to composable for persistence.

### UI Shell & Layout Components
- Purpose: Provide reusable layout patterns and page chrome (header, tabs, cards) decoupled from data logic.
- Examples:
  - `/IdeaProjects/leaderboard/frontend/src/components/layouts/AppHeader.vue`
  - `/IdeaProjects/leaderboard/frontend/src/components/layouts/NavigationTabs.vue`
  - `/IdeaProjects/leaderboard/frontend/src/components/ui/BaseBarChart.vue`
  - `/IdeaProjects/leaderboard/frontend/src/components/ui/LoadingSpinner.vue`
  - `/IdeaProjects/leaderboard/frontend/src/components/ui/ErrorMessage.vue`
- Pattern: Dumb components taking props and emitting UI‑level events while deferring data fetching and domain logic to composables and higher‑level views.

## Entry Points

### Backend Entry Point
- Location: `/IdeaProjects/leaderboard/backend/src/api/server.py`
- Triggers: Imported by the ASGI server command (e.g., `uvicorn src.api.server:create_backend`) in deployment tooling (not in repo but implied).
- Responsibilities:
  - Configure `FastAPI` application instance
  - Set up CORS for frontend environments
  - Load environment variables
  - Register all `/tokens*` endpoints and bind them to services via DI

There is also an alternative server definition at `/IdeaProjects/leaderboard/backend/src/api/SOLUTION_server.py` and a parallel DI file `/IdeaProjects/leaderboard/backend/src/utils/SOLUTION_dependency_config.py`; these appear to be reference or exercise solutions and mirror the main entry point.

### Frontend Entry Point
- Location: `/IdeaProjects/leaderboard/frontend/src/main.js`
- Triggers: Referenced by the frontend build tooling (e.g., Vite) as the JS entry loaded in `index.html`.
- Responsibilities:
  - Create Vue application
  - Install router plugin from `/frontend/src/router/index.js`
  - Import global styles from `/frontend/src/styles/global.css`
  - Mount app to DOM element with id `#app`

### Routing Entry
- Location: `/IdeaProjects/leaderboard/frontend/src/router/index.js`
- Triggers: Navigation events from user clicking tabs (`NavigationTabs`) or address bar
- Responsibilities:
  - Define routes `/leaderboard` and `/chart`
  - Redirect `/` to `/leaderboard`
  - Provide history mode config (`createWebHistory()`)

## Error Handling

**Strategy:**
- Backend: Centralize error translation in `execute_date_range_endpoint`; use typed exceptions for external API failures.
- Frontend: Each composable tracks its own `error` string; UI components display `ErrorMessage` with retry actions.

**Patterns:**
- Backend:
  - Services wrap `LiteLLMAPI` calls in `try/except` and rethrow as `RuntimeError` with normalized messages.
  - `execute_date_range_endpoint` catches:
    - Pydantic `ValueError` and date parsing `ValueError` → `HTTPException(status_code=400)`
    - `RuntimeError` → `HTTPException(status_code=502)`
    - Other `Exception` → `HTTPException(status_code=500)`
  - `LiteLLMAPI` distinguishes:
    - 401 → `ValueError("Invalid API key.")`
    - network errors → `RuntimeError` with contextual message
- Frontend:
  - Composables (`useTokenData`, `useModelData`, etc.) set `loading` and `error`, and log errors with context to `console.error`.
  - Chart and table components show loading spinners (`LoadingSpinner`) or error banners (`ErrorMessage`) with `@retry` events.

## Cross-Cutting Concerns

**Logging:**
- Frontend: Errors logged via `console.error` with contextual payloads in composables such as `/frontend/src/composables/useTokenData.js` and `/frontend/src/composables/useModelData.js`.
- Backend: No explicit structured logging; failures surfaced via exceptions and HTTP status codes.

**Validation:**
- Backend:
  - Query validation for dates through `DateRangeParams` (Pydantic) and `parse_date_range` utilities.
  - External response validation through Pydantic models in `/backend/src/client/models.py` and `/backend/src/api/models.py`.
- Frontend:
  - Lightweight client‑side validation through search term parsing (comma‑separated list) where needed.

**Authentication & Authorization:**
- Backend:
  - Outbound API auth: `LiteLLMAPI` uses `Authorization: Bearer <API_KEY>` header built from `src.utils.common.get_api_key()` (not shown).
  - Inbound requests for production backends: not directly enforced in FastAPI; instead, the frontend optionally adds a `SERVER_BASIC_AUTH_TOKEN` header for non‑localhost backend URLs.
- Frontend:
  - Attaches `Authorization: bearer ${import.meta.env.SERVER_BASIC_AUTH_TOKEN}` when backend URL is not localhost (in helpers and composables making HTTP requests).

---

*Architecture analysis: 2026-02-22*
