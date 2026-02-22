# Claude instructions (backend)

Backend is a **FastAPI** service that aggregates LiteLLM gateway usage analytics into frontend-friendly JSON.

## Architecture map

```
backend/
├── app.py                    # Entry point (Uvicorn server)
├── pyproject.toml            # Dependencies and tooling config
├── src/
│   ├── api/
│   │   ├── server.py         # FastAPI app factory, routes
│   │   └── models.py         # Request/response models
│   ├── client/
│   │   ├── api_client.py     # LiteLLM API client
│   │   └── models.py         # External API models
│   ├── services/             # Domain logic
│   │   ├── protocols.py      # Service interfaces
│   │   ├── token_aggregation_service.py
│   │   ├── time_series_service.py
│   │   ├── success_rate_service.py
│   │   ├── cost_efficiency_service.py
│   │   └── team_service.py
│   └── utils/
│       ├── dependency_config.py    # DI wiring
│       ├── endpoint_utils.py       # Shared endpoint wrapper
│       ├── date_utils.py           # Date parsing/formatting
│       └── common.py               # Shared utilities
└── tests/                    # pytest tests
```

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
