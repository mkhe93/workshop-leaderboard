# Technology Stack

**Analysis Date:** 2026-02-22

## Languages

**Primary:**
- Python >=3.13 - Backend API service in `backend/src` and `backend/app.py`
- JavaScript (ESNext) - Frontend Vue SPA in `frontend/src`

**Secondary:**
- TypeScript (type support via tooling) - Frontend tooling/types (no `.ts` source, but configured in `frontend/package.json` and `vite`/`vitest`)

## Runtime

**Environment:**
- Python (CPython) >=3.13 - Defined in `backend/pyproject.toml`
- Node.js (version not pinned, implied by devbox/devcontainer) - Used for Vite/Vitest/Playwright in `frontend`

**Package Manager:**
- Python: `uv` / PEP 621 project metadata
  - Manifest: `backend/pyproject.toml`
  - Lockfile: `backend/uv.lock` (present)
- Node.js: npm
  - Manifest: `frontend/package.json`
  - Lockfile: `frontend/package-lock.json` (present)

## Frameworks

**Core:**
- FastAPI ^0.121.0 - Backend web framework for REST API in `backend/src/api/server.py`
- Uvicorn ^0.38.0 - ASGI server for running FastAPI app in `backend/app.py`
- Vue 3 ^3.4.0 - Frontend UI framework in `frontend/src` (SFC components under `frontend/src/components` and `frontend/src/views`)
- Vue Router ^5.0.2 - SPA routing in `frontend/src/router`

**Testing:**
- Pytest ^8.4.2 - Python test framework for backend in `backend/tests`
- HTTPX ^0.28.1 - HTTP client for backend tests (declared dev dependency in `backend/pyproject.toml`)
- Ruff ^0.15.0 - Python linter/formatter (configured via `[tool.ruff]` in `backend/pyproject.toml`)
- Vitest ^4.0.6 - Unit test runner for frontend in `frontend` with config `frontend/vitest.config.js`
- @vue/test-utils ^2.4.6 - Vue component testing utilities used in frontend tests under `frontend/src` (e.g. `frontend/src/views/ChartsView.test.js`)
- Playwright ^1.56.1 (@playwright/test) - E2E/browser testing for frontend, driven by scripts in `frontend/package.json`

**Build/Dev:**
- Vite ^4.0.0 - Frontend dev server and bundler; config in `frontend/vite.config.js`
- @vitejs/plugin-vue ^4.0.0 - Vue SFC support for Vite in `frontend/vite.config.js`

## Key Dependencies

**Critical:**
- `fastapi` (>=0.121.0,<0.122.0) - Defines API routes, request/response models, dependency injection in `backend/src/api/server.py`
- `pydantic` (>=2.12.3,<3.0.0) - Data validation and serialization for backend models in `backend/src/api/models.py` and `backend/src/client/models.py`
- `uvicorn` (>=0.38.0,<0.39.0) - ASGI server used to run the FastAPI app in `backend/app.py`
- `requests` (>=2.32.5,<3.0.0) - HTTP client used to talk to external LiteLLM gateway in `backend/src/client/api_client.py`
- `dotenv` (>=0.9.9,<0.10.0) - Loads environment variables from `.env` files in `backend/src/api/server.py`
- `vue` (^3.4.0) - Core frontend framework for reactive UI components in `frontend/src`
- `vue-router` (^5.0.2) - Client-side routing for the SPA in `frontend/src/router`

**Infrastructure:**
- `chart.js` (^4.5.1) - Chart rendering library used via Vue wrapper for visualizing metrics
- `vue-chartjs` (^5.3.3) - Vue integration for Chart.js in `frontend/src/components`
- Tooling libraries for frontend build & lint:
  - `vite` (^4.0.0) - Dev/build tool, config at `frontend/vite.config.js`
  - `eslint` (^9.39.2), `@eslint/js`, `eslint-plugin-vue`, `globals` - Linting setup for JS/Vue in `frontend/eslint.config.ts`
  - `vitest` (^4.0.6) - Test runner, config at `frontend/vitest.config.js`
  - `@types/node`, `typescript-eslint`, `jiti`, `jsdom` - Type and test environment support

## Configuration

**Environment:**
- Backend environment variables are loaded with `python-dotenv` via `load_dotenv()` in `backend/src/api/server.py`.
- Key backend env vars (non-exhaustive):
  - `VITE_LEADERBOARD_BACKEND_PORT` - Port FastAPI/Uvicorn listens on (used in `backend/app.py`)
  - `VITE_LEADERBOARD_FRONTEND_PORT` - Allowed CORS origin port for frontend (used in `backend/src/api/server.py`)
  - `VITE_WORKSHOP_USER` - Used to construct hosted frontend origin for CORS in `backend/src/api/server.py`
  - `LITELLM_API_KEY` - LiteLLM gateway API key, read in `backend/src/utils/common.py`
  - `LITELLM_BASE_URL` - LiteLLM gateway base URL, read in `backend/src/utils/common.py`
- Frontend environment variables (Vite-style):
  - `VITE_LEADERBOARD_FRONTEND_PORT` - Used by Vite dev server in `frontend/vite.config.js`
  - `VITE_WORKSHOP_USER` - Used to construct `allowedHosts` in `frontend/vite.config.js`
  - `VITE_BACKEND_URL` - Backend base URL for API calls in `frontend/src/helpers/helpers.js`
  - `SERVER_BASIC_AUTH_TOKEN` - Optional auth token added to backend requests in `frontend/src/helpers/helpers.js`
- `.env`-style files may exist but are not read directly here; `load_dotenv()` is responsible for loading them.

**Build:**
- Backend:
  - Python project metadata and dependencies are defined in `backend/pyproject.toml`.
  - Build backend is `setuptools.build_meta` specified in `[build-system]` of `backend/pyproject.toml`.
- Frontend:
  - Vite configuration in `frontend/vite.config.js` defines dev server host/port and allowed hosts as well as Vue plugin.
  - Vitest configuration in `frontend/vitest.config.js` sets `environment: 'jsdom'` and enables Vue plugin.
  - NPM scripts in `frontend/package.json` control lifecycle:
    - `dev`, `dev:prep` - Start Vite dev server (normal/prep modes)
    - `build` - Production build via Vite
    - `preview` - Preview built app
    - `lint` - Run ESLint on `src/**/*.{js,vue}`
    - `test`, `coverage` - Run Vitest and coverage
    - `e2e`, `e2e:report` - Run and view Playwright E2E tests

## Platform Requirements

**Development:**
- Python >=3.13 installed with ability to create virtual environments for backend (`backend/.venv` used locally)
- Node.js (version compatible with Vite 4 and Vitest 4) with npm for frontend
- Recommended tools:
  - `uv` for Python dependency management (lockfile `backend/uv.lock`)
  - Dev containers/devbox as configured under `.devcontainer` and `devbox.json`

**Production:**
- Backend: Any environment capable of running a Uvicorn-served FastAPI app (ASGI) with Python >=3.13
- Frontend: Static hosting for Vite build output from `frontend/dist` (e.g. object storage or static web server)
- Deployment specifics (containerization, orchestration) are driven by `.devcontainer` and `.github/workflows` but not fully specified in application code.

---

*Stack analysis: 2026-02-22*
