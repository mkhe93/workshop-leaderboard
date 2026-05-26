# Tech Stack

This document captures the **current** technology choices in the codebase (brownfield documentation). It is descriptive, not a proposal to change technologies.

## Architecture

- **Monorepo** with two primary services:
  - `backend/` — FastAPI service that aggregates LiteLLM usage analytics into frontend-friendly JSON.
  - `frontend/` — Vue 3 SPA that visualizes the aggregated data (leaderboard + charts).

## Backend

- **Language/runtime:** Python **3.13+**
- **Web framework:** FastAPI
- **ASGI server:** Uvicorn
- **HTTP client:** requests
- **Configuration/env:** python-dotenv
- **Data modeling/validation:** Pydantic (v2)

### Backend tooling

- **Dependency management / execution:** uv
- **Testing:** pytest (+ httpx for HTTP testing/mocking)
- **Lint/format:** ruff
- **Type checking:** ty

## Frontend

- **Framework:** Vue 3
- **Build tool / dev server:** Vite
- **Routing:** Vue Router
- **Charts:** Chart.js + vue-chartjs

### Frontend tooling

- **Unit tests:** Vitest (+ jsdom, Vue Test Utils)
- **Linting:** ESLint (eslint-plugin-vue)

## External integration

- **LiteLLM Gateway**
  - The backend fetches usage/metrics from a LiteLLM Gateway API (base URL + API key supplied via environment variables).
