# Initial Concept

This repository is a workshop “leaderboard” UI that visualizes LLM usage analytics from a LiteLLM Gateway.

# Product Guide

## Summary

**Workshop Leaderboard** is a lightweight web app used during an LLM workshop to visualize participants’ usage metrics pulled from a LiteLLM Gateway. It supports friendly competition for attendees and gives facilitators a quick way to monitor aggregate usage and trends.

## Target users

- **Workshop attendees** who want to compare their LLM usage against others.
- **Workshop facilitators** who want visibility into usage across the cohort.

## Core views / capabilities

- **Token usage leaderboard**
  - Rank usage by user/team over a selected time range.
- **Charts over time**
  - Visualize trends (e.g., tokens over time) across the selected filters.
- **Model breakdown**
  - Summarize and compare usage by model.

## Key constraints

- **Secrets management:** no API keys/tokens committed; all sensitive values are provided via environment variables.
- **Clarity first:** prioritize a fast, readable UI and straightforward interactions over advanced customization.

## Definition of done (initial experience)

- The app loads in the workshop environment and shows the default leaderboard and charts without errors.
- Filters (e.g., date range, team/user/model) work and are reflected consistently across views.
- The UI communicates clear error states when the LiteLLM gateway is unavailable or misconfigured.

## Positioning

- The product is positioned primarily as a **Workshop Leaderboard** (lightweight, competitive framing).
