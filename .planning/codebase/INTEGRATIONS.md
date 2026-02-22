# External Integrations

**Analysis Date:** 2026-02-22

## APIs & External Services

**LLM Usage Analytics (LiteLLM Gateway):**
- Service: LiteLLM Gateway API (self-hosted or managed instance) providing spend and usage analytics for LLM calls
  - What it's used for:
    - Fetching team lists, daily spend/activity, and model information to power the leaderboard and charts
    - Computing token usage, success rates, cost efficiency, and time-series metrics
  - SDK/Client: Custom client using `requests` in `backend/src/client/api_client.py` with Pydantic models in `backend/src/client/models.py`
  - Key endpoints used (constructed from `LITELLM_BASE_URL`):
    - `GET {base_url}/team/list` via `LiteLLMAPI.fetch_teams()`
    - `GET {base_url}/team/daily/activity` via `LiteLLMAPI.fetch_team_daily_activity()` including query params `team_ids`, `start_date`, `end_date`, `page_size`
    - `GET {base_url}/model/info` (or fallback `GET {base_url}/v1/model/info`) via `LiteLLMAPI.fetch_model_info()`
  - Auth:
    - Bearer API key via `Authorization: Bearer {LITELLM_API_KEY}` header
    - Key sourced from `LITELLM_API_KEY` environment variable in `backend/src/utils/common.py`

**Frontend → Backend API:**
- Service: Internal FastAPI backend exposed at `VITE_BACKEND_URL`
  - What it's used for:
    - Providing aggregate token leaderboard (`/tokens`)
    - Providing time-series tokens per team (`/tokens/timeseries`)
    - Providing success rate summary (`/tokens/success-rate`)
    - Providing cost efficiency metrics (`/tokens/cost-efficiency`)
    - Providing hourly token breakdown (`/tokens/hourly`)
  - SDK/Client: Native `fetch` in the browser
    - Implementation in `frontend/src/helpers/helpers.js` and various composables under `frontend/src/composables` (e.g. `useTokenData.js`, `useTimeseriesData.js`, `useTeamSuccessRateData.js`, `useCostEfficiencyData.js`, `useModelData.js`)
  - Auth:
    - For localhost backends: no auth, headers include only `Accept: application/json`
    - For non-localhost backends: adds `Authorization: bearer {SERVER_BASIC_AUTH_TOKEN}` header, where `SERVER_BASIC_AUTH_TOKEN` is a Vite env var (see `frontend/src/helpers/helpers.js`)

## Data Storage

**Databases:**
- Not detected in application code.
  - There is no direct use of SQL/NoSQL clients (e.g. `psycopg2`, `sqlalchemy`, `redis`, `mongodb`) in the backend.
  - All analytical data appears to be fetched from the external LiteLLM Gateway API and processed in-memory by services in `backend/src/services`.

**File Storage:**
- Local filesystem used only for project artifacts and generated data (e.g. `frontend/dist`, Python egg-info metadata in `backend/src/leaderboard.egg-info`).
- No runtime file upload/download or object storage integration detected in backend or frontend.

**Caching:**
- In-memory caching for model name mapping within `LiteLLMAPI` client in `backend/src/client/api_client.py` via `_model_name_map_cache` fields.
- In-memory caching for frontend data fetching patterns in composables such as `frontend/src/composables/useTokenData.js` (uses local variables to avoid redundant fetches within a session).
- No external cache service (Redis, Memcached, etc.) detected.

## Authentication & Identity

**Auth Provider:**
- LiteLLM Gateway API:
  - Auth: API key authentication using `LITELLM_API_KEY` as Bearer token in the `Authorization` header (see `backend/src/client/api_client.py` and `backend/src/utils/common.py`).
  - API key can be provided via environment or entered interactively in CLI context using `get_api_key()` in `backend/src/utils/common.py`.
- Backend API:
  - Exposed via FastAPI app created in `backend/src/api/server.py` and served by Uvicorn in `backend/app.py`.
  - No user-level authentication built into routes; endpoints are open to any caller able to reach the service.
  - Frontend optionally attaches `SERVER_BASIC_AUTH_TOKEN` header for non-localhost requests in `frontend/src/helpers/helpers.js`, supporting deployments where a reverse proxy or gateway expects a static token.

## Monitoring & Observability

**Error Tracking:**
- Not detected. No integration with Sentry, OpenTelemetry, or similar in backend or frontend.

**Logs:**
- Backend:
  - Relies on FastAPI/Uvicorn default logging; Uvicorn is configured with `log_level="debug"` in `backend/app.py`.
  - Application-specific logging is minimal; most error handling wraps external API calls and raises `RuntimeError` or `ValueError` in `backend/src/client/api_client.py`.
- Frontend:
  - Uses `console.error` for error reporting in composables such as `frontend/src/composables/useModelData.js`, `frontend/src/composables/useTimeseriesData.js`, and `frontend/src/composables/useTokenData.js`.

## CI/CD & Deployment

**Hosting:**
- Intended for container-based workflows and devcontainers:
  - Devcontainer configuration in `.devcontainer/devcontainer.json` and `.devcontainer/devcontainer.env` defines environment and includes `LITELLM_API_KEY` for local use.
  - `devbox.json` and `.devbox` directory configure Nix/devbox-based reproducible dev environment.
- Exact production hosting platform is not specified in application code, but the stack is compatible with any platform supporting Python ASGI services and static file serving.

**CI Pipeline:**
- GitHub Actions workflows defined under `.github/workflows` (not fully inspected here) handle build and publish of container images for multi-arch usage.
- No explicit external CI services (CircleCI, Travis, etc.) detected.

## Environment Configuration

**Required env vars:**
- Backend (used directly in code):
  - `VITE_LEADERBOARD_BACKEND_PORT` - Port for Uvicorn server (`backend/app.py`)
  - `VITE_LEADERBOARD_FRONTEND_PORT` - Port used in CORS allowed origins (`backend/src/api/server.py`)
  - `VITE_WORKSHOP_USER` - Used to construct CORS origin host for workshop deployments (`backend/src/api/server.py`)
  - `LITELLM_API_KEY` - API key for LiteLLM Gateway (read in `backend/src/utils/common.py`)
  - `LITELLM_BASE_URL` - Base URL for LiteLLM Gateway (read in `backend/src/utils/common.py`)
- Frontend (Vite env vars accessed via `import.meta.env`):
  - `VITE_BACKEND_URL` - Backend base URL for API requests; used in `frontend/src/helpers/helpers.js` and composables
  - `SERVER_BASIC_AUTH_TOKEN` - Optional token added as `Authorization` header when backend is not on localhost (`frontend/src/helpers/helpers.js`)
  - `VITE_LEADERBOARD_FRONTEND_PORT` - Vite dev server port (`frontend/vite.config.js`)
  - `VITE_WORKSHOP_USER` - Used in `frontend/vite.config.js` for `allowedHosts` setup

**Secrets location:**
- Secrets such as LiteLLM API keys are expected to be provided via environment variables:
  - `LITELLM_API_KEY` and `LITELLM_BASE_URL` for backend LiteLLM client (`backend/src/utils/common.py`).
- `.devcontainer/devcontainer.env` illustrates how `LITELLM_API_KEY` can be set in local dev containers, but actual values should be treated as secrets and managed securely (e.g., GitHub Actions secrets, environment injection in deployment platform).
- The repository also includes helper script `/IdeaProjects/leaderboard/get_api_key.sh` to provision and export `LITELLM_API_KEY` in a local shell or devcontainer.

## Webhooks & Callbacks

**Incoming:**
- None detected. The FastAPI app in `backend/src/api/server.py` only defines standard GET endpoints for analytical data; no webhook-style POST endpoints or externally triggered callbacks are present.

**Outgoing:**
- Outbound HTTP calls to LiteLLM Gateway API from `backend/src/client/api_client.py` using `requests.get`.
  - Endpoints:
    - `/team/list`
    - `/team/daily/activity`
    - `/model/info` and fallback `/v1/model/info`
  - These are not webhooks but standard polling/HTTP client requests.

---

*Integration audit: 2026-02-22*
