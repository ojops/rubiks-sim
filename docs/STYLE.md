# Coding conventions

These conventions keep the simulator readable without imposing unnecessary tooling.

## Python

- Target Python 3.10; use four-space indentation and Ruff's 88-character formatting.
- Name functions and variables `snake_case`, classes `CapWords`, and constants `UPPER_CASE`.
- Let Ruff sort imports and format code. Add type annotations to public interfaces where practical.

## Comments and behaviour

- Use concise docstrings to describe purpose, non-obvious effects, return values and errors.
- Explain **why** coordinate, orientation, search-pruning or animation-sync decisions are necessary; do not narrate obvious assignments.
- Validate complete move sequences before changing state. Keep solving separate from printing and graphics.
- Treat a search limit as an incomplete search, never as proof that a state is unsolvable.

## Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Keep formatting-only changes separate from algorithm changes where practical. Type checking and docstring linting are not mandatory CI gates.
