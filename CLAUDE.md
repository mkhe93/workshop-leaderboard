# Claude instructions (repo root)

This repository is a small monorepo containing a **FastAPI backend** (`backend/`) and a **Vue 3 frontend** (`frontend/`) for a workshop “leaderboard” UI that visualizes LLM usage analytics from a **LiteLLM Gateway**.

## Repository Layout

```
/
├── backend/          # Python FastAPI service
├── frontend/         # Vue 3 SPA
├── conductor/        # Product documentation
├── .devcontainer/    # Dev container config
└── devbox.json       # Devbox environment config
```

## Where to look next

For detailed, scoped instructions (commands, testing, implementation boundaries), prefer:
- `backend/CLAUDE.md`
- `frontend/CLAUDE.md`

## Key directories (high level)

- `backend/` — FastAPI service code.
- `frontend/` — Vue 3 SPA.

## Environment variables (index)

Backend uses:
- `LITELLM_BASE_URL`
- `LITELLM_API_KEY`
- `VITE_LEADERBOARD_BACKEND_PORT`
- `VITE_WORKSHOP_USER`
- `VITE_LEADERBOARD_FRONTEND_PORT`

Frontend uses:
- `VITE_BACKEND_URL`
- `VITE_LEADERBOARD_FRONTEND_PORT`
- `VITE_WORKSHOP_USER`
- `SERVER_BASIC_AUTH_TOKEN` (optional)

Treat API keys and auth tokens as secrets; never commit them.

## Repo-wide conventions

- Keep domain logic in the service layer (backend) / composables (frontend); keep HTTP/UI wiring at the edges.

