# Claude instructions (backend)

Backend is a **FastAPI** service that aggregates LiteLLM gateway usage analytics into frontend-friendly JSON.

## Architecture map

- Entry point / app factory: `backend/src/api/server.py` (`create_backend()`)
- Response/request models: `backend/src/api/models.py`
- External API client: `backend/src/client/api_client.py` (`LiteLLMAPI`)
- External API models: `backend/src/client/models.py` (Pydantic)
- Domain services:
  - `backend/src/services/token_aggregation_service.py`
  - `backend/src/services/time_series_service.py`
  - `backend/src/services/success_rate_service.py`
  - `backend/src/services/cost_efficiency_service.py`
  - `backend/src/services/team_service.py`
- Dependency injection wiring: `backend/src/utils/dependency_config.py`
- Shared endpoint wrapper: `backend/src/utils/endpoint_utils.py` (`execute_date_range_endpoint`)
- Date parsing/formatting: `backend/src/utils/date_utils.py`

## Commands

From `backend/`:

```bash
# dependencies
uv sync

# tests
uv run pytest test/

# linting
uv run ruff check

# formatting
uv run ruff format

# type checking
uv run ty check
```

## Environment variables

Used by backend code:
- `LITELLM_BASE_URL` — LiteLLM gateway base URL (read in `backend/src/utils/common.py`)
- `LITELLM_API_KEY` — LiteLLM gateway API key (read in `backend/src/utils/common.py`)
- `VITE_LEADERBOARD_BACKEND_PORT` — port for Uvicorn (`backend/app.py`)
- `VITE_WORKSHOP_USER`, `VITE_LEADERBOARD_FRONTEND_PORT` — used to build allowed CORS origins (`backend/src/api/server.py`)

## Implementation guidance

- Keep HTTP concerns in `backend/src/api/server.py` (routing, status codes, DI).
- Put aggregation/transformation logic in `backend/src/services/`.
- Keep LiteLLM-specific HTTP and schema handling inside `backend/src/client/`.
- Prefer using protocols in `backend/src/services/protocols.py` so services are testable.
- For date-range endpoints, follow existing pattern:
  - accept `start_date`, `end_date` query params
  - call `execute_date_range_endpoint(start_date, end_date, service_method)`

## Testing guidance

- Tests live in `backend/tests/`.
- Prefer FastAPI `TestClient` + dependency overrides to avoid real network calls:
  - override `get_api_client` (from `backend/src/utils/dependency_config.py`) with a mock.
- Assert on error mapping behavior (400 for validation, 502 for upstream failures, 500 for unexpected).

## Safety / secrets

Never print or commit real API keys. If you must reference keys in docs or logs, redact them.
