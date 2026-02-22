# Product Guidelines

## Voice & tone

- Use a **friendly, encouraging** tone.
- Keep copy short and supportive; assume some users are new to metrics/analytics.
- Frame the product as a workshop aid, not a compliance or performance tool.

## UX / UI principles

- **Accessibility + readability first**
  - Prefer high-contrast, legible typography.
  - Ensure charts are understandable with clear titles, axis labels, and consistent colors.
  - Avoid relying solely on color to convey meaning.
- **Workshop-first UX**
  - Minimize clicks to get to the “answer”.
  - Provide sensible defaults so the app is useful immediately.
  - Prefer persistent filters (URL/localStorage) so users can share views and recover state.

## Metrics copy guidelines

- Add **brief labels/tooltips** to explain metrics and reduce misinterpretation.
- Prefer plain language definitions and avoid overloaded terms.
- If a metric can be read multiple ways, clarify the exact definition in the tooltip (e.g., what’s included/excluded).

## Error-state guidelines

- Error states should always include:
  - A **clear message** describing what failed.
  - A **likely cause** (e.g., upstream unavailable, missing configuration).
- Keep wording non-alarming; avoid blaming the user.

## Competition framing

- Use **light-touch** competitive language:
  - Prefer “friendly competition” framing.
  - Avoid shaming language or labels like “worst performer”.
  - When showing rankings, make it easy to interpret without social pressure (e.g., allow filtering to “my team”).
