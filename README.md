# Rubik's Cube Simulator

A Python simulator for Rubik's Cube moves, bounded solving and 3D visualisation with [ManimGL](https://github.com/3b1b/manim).

[![Eight-second loop of the actual animated cube scramble](docs/media/preview.gif)](https://raw.githubusercontent.com/ojops/rubiks-sim/8d14100ea3b86da000c6b40d0c78720cfe7ea9d1/docs/media/demo.mp4)

*Eight-second preview of the real cube animation. [Watch the full 32-second solve and verification (MP4)](https://raw.githubusercontent.com/ojops/rubiks-sim/8d14100ea3b86da000c6b40d0c78720cfe7ea9d1/docs/media/demo.mp4) · [Reproduce the demonstration](docs/DEMO.md).*

## Features

- Exact sticker geometry and physically validated corner/edge states
- Reproducible scrambles and bounded IDA* search with solution verification
- CLI for scrambling, solving and ManimGL rendering
- Automated tests and repeatable solver benchmarks

The solver handles **shallow scrambles**; efficient solving of arbitrary states is not yet implemented.

## Requirements and installation

Python 3.10 and [uv](https://docs.astral.sh/uv/); commands below target Ubuntu/WSL.

```bash
git clone https://github.com/ojops/rubiks-sim.git
cd rubiks-sim
uv sync --locked
```

For animation, install ManimGL's system prerequisites (including FFmpeg, Cairo and Pango) and run `uv sync --locked --extra render`. Headless rendering may require Xvfb and Mesa graphics drivers.

## Usage

```bash
uv run rubiks-sim --length 20 --seed 42
uv run rubiks-sim --scramble "R U F" --solve
uv run rubiks-sim --scramble "R U F" --solve --max-depth 8 --max-nodes 100000
```

Commands return JSON with search results and verification. Run `uv run rubiks-sim --help` for all options.

Render a scramble and verified solution:

```bash
uv run --extra render rubiks-sim --scramble "R U F" --solve --render --low-quality
```

The optional rendering workflow saves videos under `videos/`. The portfolio film and its shorter looping preview can be regenerated as described in [docs/DEMO.md](docs/DEMO.md).

## How it works

`src/rubiks_sim/cube.py` holds the exact sticker model; `cubie.py` stores permutations and orientations; `solver.py` performs bounded IDA* search; and `sim.py` animates the resulting states. [Algorithm notes](docs/ALGORITHMS.md) explain the representations and search limits.

Moves use standard `U D F B R L` notation with optional `'` or `2`. Hitting a search limit does **not** mean a state is unsolvable.

## Roadmap

Improve search heuristics and deeper solves, evaluate a two-phase solver, and refine cube visualisation.

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python benchmarks/solver.py
```

GitHub Actions checks the code and rendering workflow. See [coding conventions](docs/STYLE.md). Licensed under [MIT](LICENSE).
