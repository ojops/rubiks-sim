# Rubik's Cube Simulator

A Python 3.10 project with an exact integer sticker model, a compact cubie model,
bounded IDA* solving, and optional ManimGL animation. The solver is an educational
shallow-search baseline, not a fast general solver for random cube states.

## Install and check

```bash
uv sync --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Core use needs NumPy, not graphics libraries. Python remains pinned to 3.10.
The lockfile preserves the existing dependency versions; Ruff is pinned to 0.14.3.

## Scramble and solve

```bash
uv run rubiks-sim --length 20 --seed 42
uv run rubiks-sim --scramble "R U F" --solve --max-depth 8 --max-nodes 100000 --time-limit 5
uv run python -m rubiks_sim --scramble "R U F" --solve
```

Output is JSON containing the scramble and, when requested, a solution, node
count, elapsed seconds, search bound and termination reason. A found solution is
independently applied to the sticker model and checked before it is reported as
verified. Exit codes: 0 success, 1 search budget exhausted, 2 invalid arguments.
`depth_limit` means no solution found within the bound, not an unsolvable cube.
Half turns count as one move. Clock time and elapsed output vary between runs;
seeded scrambles and node-limited search order are deterministic.

The library retains `ida_star(state, max_depth=10)` returning a list or `None`.
`solve(state, max_depth=10, max_nodes=None, time_limit=None)` additionally returns
statistics. Both search a private copy; exceptions and interruption preserve the
input. Library limits default to unlimited except depth; the CLI defaults to
100,000 nodes and five seconds.

## Optional rendering

Ubuntu prerequisites (install through your system package manager):
`pkg-config`, `libcairo2-dev`, `libpango1.0-dev`, `ffmpeg`, and a functioning graphics
backend. For headless machines, also install `xvfb`, `xauth` and Mesa software
rendering drivers, including Vulkan where required by the pinned Manim revision.

```bash
uv sync --locked --extra render
uv run --extra render rubiks-sim --scramble "R U F" --solve --render --low-quality
# Existing demonstration:
uv run --extra render manimgl src/rubiks_sim/sim.py AnimatedRubiksCube -w
# Headless small smoke render:
xvfb-run -a uv run --extra render manimgl src/rubiks_sim/sim.py AnimatedRubiksCube -w -r 320x180 --fps 10
```

The CLI renders the scramble followed by its verified solution. Use
`--output-dir` to select the destination. Without a display it uses `xvfb-run` on
Linux. The existing scene still defaults to the reproducible 20-move demo.
Rendering starts a subprocess; its log output accompanies the CLI JSON, so omit
`--render` when consuming stdout as a JSON document.

The rendering extra uses a pinned Manim Git revision through uv. Wheel metadata
does not preserve `[tool.uv.sources]`; use this locked uv workflow for supported
rendering reproducibility. Arbitrary pip-installed Manim versions are unverified.

## Representation and development

`cube.py` rotates 54 stickers using integer matrices. `cubie.py` tracks the eight
corners and twelve edges, using precomputed transformations for all 18 moves.
`from_cube` enforces fixed centres and physical parity/orientation constraints.
`solver.py` handles bounded search; `sim.py` handles graphics only.

See [algorithm notes](docs/ALGORITHMS.md) and [coding standard](docs/STYLE.md).
Next: stronger coordinate pruning, then a separately designed two-phase solver.
MIT licensed; see [LICENSE](LICENSE).
