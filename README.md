# Rubik's Cube Simulator

A Python project for modelling, solving, and visualising Rubik's Cube operations using [ManimGL](https://github.com/3b1b/manim), with the longer term aim of developing an efficient solver.

## Overview

The simulator represents the cube in two ways: a sticker model for geometry and animation, and a compact corner-and-edge model for solving. Development is progressing from reliable moves and shallow searches towards stronger solving algorithms.

## Features

- Exact integer sticker positions and rotations
- Corner and edge representation with physical state validation
- Reproducible random move sequences
- IDA* search with depth, node, and time limits
- Terminal commands for scrambling, solving, and rendering
- Solution verification against the sticker model
- 3D animation using ManimGL

The solver currently handles shallow scrambles. Fast solving of arbitrary cube states is not implemented, and generated scrambles are random move sequences rather than competition-standard random-state scrambles.

## Requirements

- Python 3.10
- [uv](https://docs.astral.sh/uv/)
- For animation: ManimGL's system dependencies and a working graphics backend

The following instructions assume Ubuntu or WSL running Ubuntu.

## Installation

Clone the repository and install its core dependencies:

```bash
git clone https://github.com/ojops/rubiks-sim.git
cd rubiks-sim
uv sync --locked
```

For animation, also install the rendering dependencies:

```bash
uv sync --locked --extra render
```

ManimGL also needs system packages such as `pkg-config`, `libcairo2-dev`, `libpango1.0-dev`, and `ffmpeg`. Headless Linux rendering needs `xvfb`, `xauth`, and suitable Mesa graphics drivers, including Vulkan support where required by the pinned ManimGL revision.

## Usage

Run commands from the repository root. Generate a repeatable scramble:

```bash
uv run rubiks-sim --length 20 --seed 42
```

Solve a short scramble:

```bash
uv run rubiks-sim --scramble "R U F" --solve
```

Output is JSON containing the scramble and, when solving, the solution and search statistics. A found solution is checked against the sticker model before it is marked as verified. The module command also works: `uv run python -m rubiks_sim`.

Adjust the search limits without editing the source:

```bash
uv run rubiks-sim --scramble "R U F" --solve --max-depth 8 --max-nodes 100000 --time-limit 5
```

Use `uv run rubiks-sim --help` to list all options.

### Animation

Render a scramble followed by its verified solution:

```bash
uv run --extra render rubiks-sim --scramble "R U F" --solve --render --low-quality
```

Render the original 20-move demonstration directly:

```bash
uv run --extra render manimgl src/rubiks_sim/sim.py AnimatedRubiksCube -w
```

Videos are saved under `videos/`. The CLI also accepts `--output-dir` and automatically uses `xvfb-run` on Linux when no display is available. Rendering logs accompany the JSON output; omit `--render` when reading stdout as a JSON document.

## Solving assumptions

Supported moves are `U`, `D`, `F`, `B`, `R`, and `L`, optionally followed by `'` or `2`. A half turn counts as one move. Cube conversion assumes fixed face colours and rejects physically unreachable cubie states.

The CLI defaults to a depth limit of 10, 100,000 visited nodes, and five seconds. Reaching a limit means the search stopped without finding a solution; it does not mean the cube is unsolvable. Exit codes are 0 for success, 1 when no solution is found within the limits, and 2 for invalid arguments or handled setup/rendering errors.

See [algorithm notes](docs/ALGORITHMS.md) for the representations, search method, and Python API.

## Development Roadmap

- **Solving:** Develop a stronger heuristic and evaluate deeper searches.
- **Algorithms:** Compare improving optimal IDA* search with a practical two-phase solver.
- **Scrambling:** Explore competition-standard random-state scramble generation.
- **Visualisation:** Improve the appearance and interaction of the cube animation.
- **Evaluation:** Measure search performance and extend checks for the CLI rendering workflow.

## Project Structure

| Path | Purpose |
| --- | --- |
| `src/rubiks_sim/cube.py` | Sticker geometry and face turns |
| `src/rubiks_sim/cubie.py` | Corner and edge states and move tables |
| `src/rubiks_sim/notation.py` | Supported moves and sequence validation |
| `src/rubiks_sim/scramble.py` | Seeded random move generation |
| `src/rubiks_sim/solver.py` | IDA* search and search statistics |
| `src/rubiks_sim/main.py` | Terminal commands and rendering launch |
| `src/rubiks_sim/sim.py` | ManimGL animation |
| `docs/` | Algorithm notes and coding conventions |
| `tests/` | Cube, solver, and input validation tests |
| `benchmarks/solver.py` | Small repeatable search benchmarks |
| `.github/workflows/checks.yml` | Automated code checks, tests, and demo rendering |
| `pyproject.toml` / `uv.lock` | Project configuration and locked dependencies |
| `videos/` | Generated videos; not tracked in Git |

## Development

Run the tests and code checks:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Run the search benchmarks with `uv run python benchmarks/solver.py`. Timings depend on the machine.

Add core dependencies with `uv add package-name`, or rendering dependencies with `uv add --optional render package-name`. Commit both `pyproject.toml` and `uv.lock` when they change. Use the locked uv workflow for rendering: the pinned ManimGL Git source is configured through uv and is not preserved in standard wheel metadata.

GitHub Actions runs the checks on pushes and pull requests. See [coding conventions](docs/STYLE.md).

## License

MIT licensed. See [LICENSE](LICENSE).
