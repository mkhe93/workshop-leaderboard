# Product Guidelines

## Voice & tone
- Clear and practical.
- Workshop-friendly: prefer short labels and plain language over jargon.
- Avoid exposing secrets in UI/logs (API keys, auth tokens).

## UX principles
- Default to sensible date ranges and filters.
- Make loading and error states explicit and non-confusing.
- Prefer consistent formatting for numbers (tokens, cost, percentages).

## Data integrity principles
- Treat backend as the source of truth for aggregation/transformation.
- Validate date range inputs consistently across endpoints.
- Keep response shapes stable; version/extend intentionally.

## Security & privacy
- Never log or display API keys/tokens.
- If user identifiers are shown, keep to workshop-safe identifiers (e.g., names provided by attendees) and avoid leaking internal IDs.
