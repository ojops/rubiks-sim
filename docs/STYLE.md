# Coding conventions

## Formatting

Use Python 3.10, four space indentation, `snake_case` functions and variables, `CapWords` classes, and `UPPER_CASE` constants. Let Ruff handle imports, 88 column wrapping, and spacing between definitions.

## Documentation

Start docstrings with a short action sentence and a full stop. Explain mutation, returns, units, and errors where useful. Spell `Singmaster`, `NumPy`, and `ManimGL` consistently.

Annotate public function parameters and return types. Move sequences use `str | Iterable[str]`. Internal helpers and tests need extra documentation only when it clarifies behaviour.

Keep comments focused on coordinate conventions, orientations, search pruning, and graphics synchronisation. Avoid narrating obvious assignments.

## Behaviour and checks

Validate whole move sequences before mutation or playback. Keep solving independent of printing and graphics. Treat search limits as incomplete searches, not unsolvable cubes.

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Keep documentation and formatting separate from algorithm changes where practical. There is no mandatory type checking or docstring linting gate.
