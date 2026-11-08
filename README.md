# Rubik's Cube Simulator

A Python project for modelling, solving and animating Rubik's Cube moves, with 3D visualisation using [ManimGL](https://github.com/3b1b/manim).

[![Eight-second preview of the project's cube animation](docs/media/preview.gif)](https://raw.githubusercontent.com/ojops/rubiks-sim/8d14100ea3b86da000c6b40d0c78720cfe7ea9d1/docs/media/demo.mp4)

*Preview: a real four-move scramble. [Watch the complete 32-second solve (MP4)](https://raw.githubusercontent.com/ojops/rubiks-sim/8d14100ea3b86da000c6b40d0c78720cfe7ea9d1/docs/media/demo.mp4) · [How the video is made](docs/DEMO.md).*

## Overview

This project explores how a Rubik's Cube can be represented, manipulated, solved and visualised. You can enter your own moves or generate a reproducible scramble, search for a solution within configurable limits, and optionally animate the result. It combines a detailed sticker model with a compact corner-and-edge representation to keep visualisation and search separate.

The bounded solver now uses exact-distance coordinate heuristics, with measured improvements on deterministic scrambles including an eight-move optimal solution. It still does not provide efficient arbitrary-state solving. The video above shows a real computed solution, verified against the cube model.

## Features

- Exact sticker geometry and physically validated corner/edge states
- Reproducible scrambles and IDA* search with configurable limits
- Admissible corner/edge coordinate heuristics and a selectable original baseline
- Controlled benchmarks reporting nodes, setup/search time and termination status
- Solution verification against an independent sticker model
- Command-line scrambling, solving and optional 3D rendering

Solving remains bounded: some ten-move sequences and the benchmark twenty-move sequence still exhaust the node limit. Scramble length is not necessarily optimal solution depth.

## Requirements and Installation

Requires Python 3.10 and [uv](https://docs.astral.sh/uv/). These commands target Ubuntu or WSL:

```bash
git clone https://github.com/ojops/rubiks-sim.git
cd rubiks-sim
uv sync --locked
```

To animate, install the ManimGL system prerequisites (including FFmpeg, Cairo and Pango), then run `uv sync --locked --extra render`. Headless Linux rendering may also require Xvfb and Mesa.

## Usage

```bash
uv run rubiks-sim --length 20 --seed 42
uv run rubiks-sim --scramble "R U F" --solve
uv run rubiks-sim --scramble "R U F" --solve --max-depth 8 --max-nodes 100000
```

Compare the original heuristic with the default coordinate heuristic:

```bash
uv run rubiks-sim --scramble "R U F2 L" --solve --heuristic basic
uv run rubiks-sim --scramble "R U F2 L" --solve --heuristic pattern
uv run python benchmarks/solver.py --repeats 2
```

The default builds 44,555 bytes of distance tables once per process. CLI elapsed time and time limits include that setup; `setup_seconds` identifies it separately. Warm benchmark searches reuse the tables. See [measured comparisons](docs/BENCHMARKS.md), including cases that still reach limits.

The CLI returns JSON, including search statistics and solution verification when solving. Run `uv run rubiks-sim --help` for all options.

Render a scramble followed by its computed solution:

```bash
uv run --extra render rubiks-sim --scramble "R U F" --solve --render --low-quality
```

Output videos go to `videos/` by default. The portfolio MP4 and looping preview are generated separately; see [demo instructions](docs/DEMO.md).

## Implementation

`src/rubiks_sim/cube.py` tracks stickers; `cubie.py` tracks corners and edges; `solver.py` performs bounded IDA* search; `sim.py` handles animation. Moves use `U D F B R L`, with optional `'` or `2`. Reaching a search limit **does not** establish that a cube is unsolvable.

See [algorithm details](docs/ALGORITHMS.md) for models, validity checks and search assumptions.

## Development Roadmap

Development is incremental, with an emphasis on correct cube states, robust search and measured performance before more demanding demonstrations.

### Planned

- **Extend measured search coverage:** use the implemented coordinate heuristic and baseline comparison to evaluate more seeds and deeper states; measure successor-generation cost before adding larger edge pattern databases.
- **Evaluate a two-phase solver:** compare practical solving coverage, correctness and complexity against the measured bounded IDA* baseline. Optimal face-turn search and practical arbitrary-state solving have different goals.
- **Demonstrate harder scrambles when supported:** select a consistently solvable case, independently verify it and genuinely render replacement media before changing the current portfolio film.
- **Refine animation independently:** improve camera framing, move pacing and captions without coupling ManimGL rendering to search.

## Project Structure

```text
rubiks-sim/
├── src/rubiks_sim/
│   ├── cube.py          # Sticker geometry and face turns
│   ├── cubie.py         # Corner/edge states and validation
│   ├── solver.py        # Bounded IDA* solver
│   ├── patterns.py      # Exact coordinate distances and admissible bounds
│   ├── sim.py           # ManimGL visualisation
│   └── main.py          # Command-line interface
├── scripts/             # Portfolio video and scene rendering
├── benchmarks/          # Controlled comparisons and recorded JSONL results
├── tests/               # Cube, solver and rendering tests
├── docs/                # Algorithms, demo and style notes
│   └── media/           # Preview GIF, MP4 and recorded data
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Locked dependencies
└── README.md
```

The `videos/` directory is created by rendering and is not tracked in Git.

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python benchmarks/solver.py
```

Dependencies are managed with `uv`; when changing them, commit both `pyproject.toml` and `uv.lock`. GitHub Actions runs code and rendering checks. See [coding conventions](docs/STYLE.md).

## License

[MIT licensed](LICENSE).
