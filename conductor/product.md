# Product Guide

## Product summary
A workshop "leaderboard" web app that visualizes LLM usage analytics pulled from a LiteLLM Gateway. It provides a leaderboard and charts over a selected date range so workshop participants can see usage patterns and compare activity.

## Target users
- **Primary:** Workshop attendees using the LiteLLM Gateway during the workshop.
- **Secondary (optional):** Workshop facilitators monitoring aggregate activity.

## Problems it solves
- Makes LiteLLM Gateway usage data **easy to understand at a glance** (leaderboard + charts).
- Helps participants and facilitators **verify that usage is being tracked correctly**.
- Enables quick comparisons across users/models over a selected time range.

## Key workflows
1. Start the devcontainer and configure environment (LiteLLM base URL + API key).
2. Open the UI and select date range / filters.
3. View:
   - Leaderboard ranking by usage metrics (e.g., tokens).
   - Charts for trends and breakdowns.

## Key features
- FastAPI backend that aggregates and transforms LiteLLM analytics into frontend-friendly JSON.
- Vue 3 + Vite SPA that displays:
  - Leaderboard view
  - Charts view
- Shared date-range filtering.

## Success metrics
- **Accuracy:** Leaderboard and charts reliably match LiteLLM Gateway usage analytics for the chosen date range.
- Backend responses are consistent and stable (schemas don’t unexpectedly change).
- Workshop participants can load the UI without manual debugging or ad-hoc data fixes.
