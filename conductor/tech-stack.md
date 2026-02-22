# Tech Stack

## Overview
This is a small monorepo with:
- **Backend:** Python **FastAPI** service that queries LiteLLM Gateway analytics and aggregates them for the UI.
- **Frontend:** **Vue 3** SPA built with **Vite**.

## Backend
- Language/runtime: **Python >= 3.13**
- Web framework: **FastAPI**
- Server: **Uvicorn**
- HTTP client: **requests**
- Data modeling/validation: **Pydantic v2**
- Dependency management: **uv** (using `pyproject.toml`)
- Tooling:
  - Lint/format: **ruff**
  - Type check: **ty**
  - Tests: **pytest** (and **httpx** for test HTTP)

## Frontend
- Language: **JavaScript**
- Framework: **Vue 3**
- Build/dev: **Vite**
- Tests: **Vitest** + **Vue Test Utils**
- Charts: `vue-chartjs` (mocked in unit tests per repo guidance)

## External dependency
- **LiteLLM Gateway**
  - Configured via `LITELLM_BASE_URL` + `LITELLM_API_KEY`
  - Backend encapsulates LiteLLM-specific API and schemas in `backend/src/client/`
