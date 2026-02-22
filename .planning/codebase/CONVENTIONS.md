# Coding Conventions

**Analysis Date:** 2026-02-22

## Naming Patterns

**Files:**
- Frontend: Vue single-file components use `PascalCase` file names like `SharedControls.vue`, feature components are nested by domain, e.g. `frontend/src/components/features/charts/TokenTypeBreakdown.vue`, composables use `camelCase` with `use` prefix such as `frontend/src/composables/useTokenData.js`, helpers and utilities use descriptive `camelCase` names like `frontend/src/helpers/chartHelpers.js`.
- Frontend tests: Co-located `*.test.js` files next to the units under test, e.g. `frontend/src/components/features/filters/DateRangeSelector.test.js`, `frontend/src/helpers/helpers.test.js`.
- Backend: Packages and modules use `snake_case` such as `backend/src/utils/date_utils.py`, `backend/src/services/token_aggregation_service.py`, and `backend/src/client/api_client.py`.
- Backend tests: Module-level tests use `test_*.py` naming under `backend/tests`, e.g. `backend/tests/test_date_utils.py`, `backend/tests/test_tokens_endpoint_integration.py`. Grouped tests sometimes use test classes like `TestTokensEndpointIntegration`.

**Functions:**
- Frontend: Composition API `script setup` uses `camelCase` for functions and refs, e.g. `toggleModel`, `selectAllModels`, `retryCostEfficiency` in `frontend/src/views/ChartsView.vue`. Event handlers follow the same pattern.
- Backend: Public functions and methods use `snake_case` following PEP 8, e.g. `parse_date_range` in `backend/src/utils/date_utils.py`, `execute_date_range_endpoint` in `backend/src/utils/endpoint_utils.py`, `fetch_team_daily_activity` in `backend/src/client/api_client.py`.

**Variables:**
- Frontend: `camelCase` for local variables and refs, e.g. `mockSearchTerm`, `mockEndDate` in `frontend/src/components/SharedControls.test.js` and `selectedModels`, `showModelFilter` in `frontend/src/views/ChartsView.vue`.
- Backend: `snake_case` for locals and attributes, e.g. `start_dt`, `end_dt` in `backend/src/utils/date_utils.py`, `team_ids_param` in `backend/src/client/api_client.py`. Constants are not heavily used but when present should be `UPPER_SNAKE_CASE` following Python norms.

**Types:**
- Backend: Pydantic models use `PascalCase` names such as `TeamOut`, `TeamsOut`, `TimeSeriesOut` in `backend/src/api/models.py`, and `TeamResponse`, `SpendAnalyticsPaginatedResponse` in `backend/src/client/models.py`. Protocol interfaces also use `PascalCase` with `Protocol` suffix, e.g. `APIClientProtocol` in `backend/src/services/protocols.py`.
- Frontend: No TypeScript types are present; Vue props are validated using the Options API-style `defineProps` with `type` and `required`/`default` options as in `frontend/src/components/features/filters/DateRangeSelector.vue`.

## Code Style

**Formatting:**
- Frontend: Uses ESLint flat config via `frontend/eslint.config.ts` with `@eslint/js` and `eslint-plugin-vue`. The config targets `**/*.{js,mjs,cjs,ts,mts,cts,vue}` and uses browser and node globals. There is no explicit Prettier config; formatting follows standard ESLint recommendations and typical Vue single-file component formatting (two-space indentation, single quotes).
- Backend: Uses Ruff for linting as configured in `backend/pyproject.toml` under `[tool.ruff]`, excluding `debug_scripts`. Code follows PEP 8 with 4-space indentation and docstrings using triple double quotes.

**Linting:**
- Frontend: `npm run lint` is configured in `frontend/package.json` as `eslint src/**/*.{js,vue}` and should be used to enforce style and catch common issues. Vue-specific rules come from `pluginVue.configs["flat/essential"]` in `frontend/eslint.config.ts`.
- Backend: Ruff is included as a dev dependency in `backend/pyproject.toml` (`ruff>=0.15.0`) and enforces import order and common Python style constraints across `backend/src` and `backend/tests` (except excluded paths).

## Import Organization

**Order:**
- Frontend:
  1. Vue and core libraries, e.g. `import { computed } from 'vue'` in `frontend/src/components/features/filters/DateRangeSelector.vue`.
  2. Composables and helpers from `../composables/...` or `../helpers/...`, e.g. imports at the top of `frontend/src/views/ChartsView.vue`.
  3. Local components using relative paths, e.g. `import TokenTypeBreakdown from '../components/features/charts/TokenTypeBreakdown.vue'` in `frontend/src/views/ChartsView.vue`.
  4. In tests, mocking is declared after imports, using `vi.mock()` blocks before `describe` blocks.
- Backend:
  1. Standard library imports (`datetime`, `typing`, `os`, `sys`, `traceback`).
  2. Third-party imports (`fastapi`, `pydantic`, `requests`).
  3. Internal imports from `src.api`, `src.services`, `src.utils`, and `src.client`, as in `backend/src/api/server.py` and `backend/src/utils/endpoint_utils.py`.

**Path Aliases:**
- Backend: Uses `src.` as the root package for application code, e.g. `from src.utils.date_utils import parse_date_range` in `backend/src/utils/endpoint_utils.py` and `from src.api.server import create_backend` in multiple tests.
- Frontend: No custom path aliases are configured; imports use relative paths like `../composables/useFilters.js` and `../../ui/BaseBarChart.vue`.

## Error Handling

**Patterns:**
- Backend:
  - Validation and date parsing errors are mapped to HTTP 400 responses via shared utilities. `backend/src/utils/endpoint_utils.py` centralizes this pattern: it constructs `DateRangeParams`, calls `parse_date_range`, and wraps them in `try/except` blocks, converting `ValueError` to `HTTPException(status_code=400, detail=str(e))`.
  - Service-layer operations that depend on external systems catch `RuntimeError` and general `Exception` separately. In `backend/src/utils/endpoint_utils.py`, `RuntimeError` becomes an HTTP 502 with the original message, and any other exception becomes HTTP 500 with a `"Unexpected error: ..."` message.
  - API client methods in `backend/src/client/api_client.py` use `try/except` around `requests.get`, raising `ValueError` for invalid API keys (401) and `RuntimeError` for general request failures. For example, `fetch_teams` raises `RuntimeError(f"Error fetching teams: {e}")` on `requests.RequestException`.
  - Date utilities in `backend/src/utils/date_utils.py` raise `ValueError` with explicit messages tagging the parameter name when parsing fails, e.g. `raise ValueError(f"Invalid end_date format. Expected YYYY-MM-DD: {e}")`. Tests in `backend/tests/test_date_utils.py` assert on these messages.

- Frontend:
  - Asynchronous data-fetching composables (`useTokenData`, `useModelData`, etc.) are not fully shown here, but usage in `frontend/src/views/ChartsView.vue` indicates the pattern: each composable returns `loading`, `error`, and `fetchData`/`retry` functions. Container components pass these to presentational components, which display loading/error states and emit `retry` events.
  - UI-level error display is handled via dedicated components like `ErrorMessage` and `LoadingSpinner` (mocked in tests). For example, `frontend/src/components/features/charts/TokenTypeBreakdown.test.js` asserts that an error message is rendered when `error` prop is non-empty and that loading states show a spinner.

## Logging

**Framework:**
- Backend: No dedicated logging framework is prominently configured in the files inspected. The API client (`backend/src/client/api_client.py`) uses exceptions for error propagation and, in one edge case, prints a traceback via `traceback.print_exc()` before `sys.exit(1)` when encountering unexpected pagination.
- Frontend: No explicit logging patterns (such as `console.log`) are present in the main components and tests shown. Errors are exposed via props and displayed in the UI rather than logged.

**Patterns:**
- Prefer raising exceptions in backend libraries and mapping them to HTTP errors at the boundary (see `backend/src/utils/endpoint_utils.py`).
- Prefer surfacing errors to the UI via `error` props and dedicated components rather than logging in Vue components.

## Comments

**When to Comment:**
- Backend: Docstrings describe module and function responsibilities and arguments, especially in shared utilities and services. Examples:
  - `backend/src/utils/date_utils.py` uses docstrings on each function to document parameters, return values, and exceptions.
  - `backend/src/utils/endpoint_utils.py` explains the endpoint abstraction and its behavior, including error mapping.
  - `backend/src/client/api_client.py` docstrings document methods like `fetch_team_daily_activity`, including parameters, return types, and raised exceptions.
- Frontend: Comments are minimal and focused on clarifying test intent and component behavior.
  - Tests such as `frontend/src/helpers/helpers.test.js` use `// given`, `// when`, `// then` comments to structure test logic.
  - Components sometimes include comments to explain layout or responsiveness, e.g. `/* Responsive adjustments for mobile devices */` in `frontend/src/views/ChartsView.vue`.

**JSDoc/TSDoc:**
- There is no consistent use of JSDoc/TSDoc in the frontend code reviewed. Type information is mostly implicit or enforced by Vue props.

## Function Design

**Size:**
- Functions and methods are kept relatively small and focused on a single responsibility:
  - `parse_date_range` in `backend/src/utils/date_utils.py` handles only parsing and defaulting of date ranges.
  - `execute_date_range_endpoint` in `backend/src/utils/endpoint_utils.py` focuses on validation, parsing, and delegating to services.
  - Vue `script setup` blocks use multiple small functions like `toggleModel`, `selectAllModels`, and `retryModel` in `frontend/src/views/ChartsView.vue` instead of large monoliths.

**Parameters:**
- Backend: Functions use explicit named parameters with type hints, such as `(start_date: str | None, end_date: str | None)` in `parse_date_range` and service methods that accept `start_date` and `end_date` strings formatted for external APIs.
- Frontend: Vue components expose props via `defineProps`, explicitly typing and marking `required` fields, e.g. `teams`, `loading`, `error`, and `searchTerm` in `frontend/src/components/features/charts/TokenTypeBreakdown.vue`.

**Return Values:**
- Backend: Pure functions return concrete types and avoid side effects; for instance `format_date_for_api` returns a string and does not mutate inputs. Service methods return Pydantic model instances or native dict/list structures which are then converted via FastAPI response models.
- Frontend: Computed properties (`computed`) encapsulate derived state, e.g. `barChartData` and `availableModels` in `frontend/src/views/ChartsView.vue`, while functions primarily trigger side-effectful operations (API fetches via composables).

## Module Design

**Exports:**
- Frontend: Vue SFCs export their component definitions implicitly via `<script setup>`. Helpers export named functions from `.js` modules and are imported individually, as seen with `transformToChartData` from `frontend/src/helpers/chartHelpers.js`.
- Backend: Each module defines related functionality (e.g. `backend/src/utils/date_utils.py` for date handling, `backend/src/utils/endpoint_utils.py` for endpoint patterns) and exports functions/classes via normal Python module semantics. Service modules encapsulate domain logic in service classes.

**Barrel Files:**
- No barrel-file pattern is used in either frontend or backend. Modules are imported directly via their full paths, keeping boundaries explicit.

---

*Convention analysis: 2026-02-22*
