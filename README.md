# Rubik's Cube Simulator

Model, solve and animate Rubik's Cube moves in Python with [ManimGL](https://github.com/3b1b/manim).

[![Eight-second preview of the project's cube animation](docs/media/preview.gif)](https://raw.githubusercontent.com/ojops/rubiks-sim/8d14100ea3b86da000c6b40d0c78720cfe7ea9d1/docs/media/demo.mp4)

*Preview: a real four-move scramble. [Watch the complete 32-second solve (MP4)](https://raw.githubusercontent.com/ojops/rubiks-sim/8d14100ea3b86da000c6b40d0c78720cfe7ea9d1/docs/media/demo.mp4) · [How the video is made](docs/DEMO.md).*

## Features

- Exact sticker geometry and physically validated corner/edge states
- Reproducible scrambles and IDA* search with configurable limits
- Solution verification against an independent sticker model
- Command-line scrambling, solving and optional 3D rendering

The solver is intended for **shallow scrambles**; efficient arbitrary-state solving is not yet supported.

## Install

Requires Python 3.10 and [uv](https://docs.astral.sh/uv/). These commands target Ubuntu or WSL:

```bash
git clone https://github.com/ojops/rubiks-sim.git
cd rubiks-sim
uv sync --locked
```

To animate, install the ManimGL system prerequisites (including FFmpeg, Cairo and Pango), then run `uv sync --locked --extra render`. Headless Linux rendering may also require Xvfb and Mesa.

## Run

```bash
uv run rubiks-sim --length 20 --seed 42
uv run rubiks-sim --scramble "R U F" --solve
uv run rubiks-sim --scramble "R U F" --solve --max-depth 8 --max-nodes 100000
```

The CLI returns JSON, including search statistics and solution verification when solving. Run `uv run rubiks-sim --help` for all options.

Render a scramble followed by its computed solution:

```bash
uv run --extra render rubiks-sim --scramble "R U F" --solve --render --low-quality
```

Output videos go to `videos/` by default. The portfolio MP4 and looping preview are generated separately; see [demo instructions](docs/DEMO.md).

## Implementation

`src/rubiks_sim/cube.py` tracks stickers; `cubie.py` tracks corners and edges; `solver.py` performs bounded IDA* search; `sim.py` handles animation. Moves use `U D F B R L`, with optional `'` or `2`. Reaching a search limit **does not** establish that a cube is unsolvable.

See [algorithm details](docs/ALGORITHMS.md) for models, validity checks and search assumptions.

## Planned roadmap

- **Strengthen IDA* search:** investigate coordinate-based heuristics or pattern databases and benchmark deeper scrambles under reproducible depth, node and time limits.
- **Evaluate a two-phase solver:** compare its correctness, search effort and implementation complexity with the current approach before claiming broader solving capability.
- **Expand solver validation:** test a wider range of scramble depths, independently verify returned solutions and report search-limit outcomes separately from invalid or unsolvable states.
- **Demonstrate harder scrambles when supported:** replace the four-move portfolio example with a genuinely computed, more challenging solve and measured search statistics; retain the shallow-scramble limitation until performance improves.
- **Refine animation independently:** improve camera framing, move pacing and explanatory captions without coupling ManimGL rendering to the solver.

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python benchmarks/solver.py
```

GitHub Actions runs code and rendering checks. See [coding conventions](docs/STYLE.md). [MIT licensed](LICENSE).
