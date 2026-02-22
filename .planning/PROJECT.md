# Leaderboard — Model Usage Endpoint

## What This Is

A small FastAPI backend change to complete the missing “model usage” API feature so the existing Vue leaderboard UI can load model usage data without relying on an incomplete/dummy backend response.

The frontend already calls a model-usage endpoint (`GET /tokens/models`) and expects a JSON response with a `models` array.

## Core Value

The backend provides a stable `/tokens/models` endpoint so the UI can reliably render model usage for a selected date range.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Implement backend endpoint `GET /tokens/models` that returns a `models` list compatible with the existing frontend (`frontend/src/composables/useModelData.js`).
- [ ] Endpoint accepts optional `start_date` and `end_date` query parameters (YYYY-MM-DD), consistent with other `/tokens*` endpoints.
- [ ] Endpoint behavior matches existing backend conventions for date-range endpoints (use shared date-range execution wrapper/pattern).
- [ ] Endpoint passes the existing integration test at `backend/tests/test_tokens_models_endpoint_integration.py`.

### Out of Scope

- Frontend UI changes — UI is already working and out of scope for this work.
- Changes to auth scheme — follow existing endpoint behavior rather than introducing new auth.

## Context

- Repo is a small monorepo with a FastAPI backend (`backend/`) and Vue 3 frontend (`frontend/`).
- Frontend fetches model usage from `${VITE_BACKEND_URL}/tokens/models`, adding an Authorization bearer token only when the backend is not localhost.
- Backend currently exposes several `/tokens*` endpoints and uses a shared date-range wrapper (`execute_date_range_endpoint`) for consistency.
- There are `SOLUTION_*.py` files that appear to be reference implementations; prefer implementing in the non-solution files.

## Constraints

- **Compatibility**: Response must match frontend expectations: JSON object with a `models` array.
- **Testing**: Must satisfy the pre-existing integration test for the endpoint.
- **Conventions**: Follow existing patterns in `backend/src/api/server.py` for date-range endpoints.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep scope backend-only | UI already works; fastest path is to unblock it by completing backend endpoint | — Pending |
| Use `/tokens/models` | Frontend already calls this path | — Pending |

---
*Last updated: 2026-02-22 after initialization*
