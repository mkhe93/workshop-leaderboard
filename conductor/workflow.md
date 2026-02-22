# Workflow

## Development loop
- Prefer small, reviewable changes.
- Keep domain logic in backend services / frontend composables, with HTTP/UI wiring at the edges.

### Vertical-slice delivery (preferred)
When implementing features, prefer **vertical slices** over horizontal layers.

A vertical slice is a small, end-to-end increment that is:
- **Executable and testable** on its own.
- **Backend + frontend complete** (API/service change + UI wiring) so it can be validated in the running app.
- Small enough to review and revert if needed.

Practical guidance:
- Each subtask should end with a visible outcome (UI change) backed by real backend behavior.
- Prefer adding one API shape/endpoints + one UI surface at a time, rather than building all backend pieces first.
- Keep slices narrow: one metric, one chart, one filter, one endpoint, etc.

## Testing
- Target coverage: **80%** (guideline, not a hard gate unless CI enforces it).
- Backend: pytest; prefer FastAPI dependency overrides to avoid real network calls.
- Frontend: Vitest; prefer mocking remote-fetching composables and chart components.

### Slice-level validation
Each vertical slice should include a validation step that exercises the full path:
- Backend endpoint/service returns expected JSON for the slice.
- Frontend renders the slice using that data.

Additionally, after completing **each subtask/slice**, you must validate your own work by running:
- **Tests** (backend + frontend as applicable)
- **Linting/format**
- **Type checking**

Finally, after each slice you must provide the user a **manual test guide** for the produced outcome. The guide should be concrete and step-by-step, tailored to the slice, for example:
1. Run the backend (and frontend if relevant).
2. Execute a specific `curl` command.
3. State what response fields/values to verify.
4. If there is a UI change, describe exactly what to click/see.

This does not require full browser automation; a lightweight check is acceptable (e.g., run backend+frontend and verify with curl + page load), but the slice should be runnable end-to-end.

## TDD cadence (when implementing features)
1. Write/adjust a failing test (Red)
2. Implement minimal code to pass (Green)
3. Refactor while keeping tests green (Refactor)

### Track kickoff: user-authored integration test
For each **new track**, start by asking the user to provide (or pair-program) an **integration test** that validates the end-to-end behavior of the feature.

Guidelines:
- Encourage the user to write the initial test (or drive while pairing). Do **not** write the entire integration test on your own.
- Only proceed to implementation once an end-to-end acceptance test exists (even if minimal).
- If the user already provided an integration test, use it as the primary acceptance signal for the track.

## Commits
- Commit granularity: **per task** (or per small coherent unit of work).
- Do not commit secrets.

## Notes
- Use git notes: **yes** (optional) for storing investigation context.
