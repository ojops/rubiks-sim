# Rubik's Cube Simulator

A Python project for modelling, solving, and animating Rubik's Cube moves, with optional 3D visualisation using [ManimGL](https://github.com/3b1b/manim).

[![Six seeded turns animate the same scramble used in the solver benchmark](docs/media/preview.gif)](https://raw.githubusercontent.com/ojops/rubiks-sim/a213fb717badee4ff2daedff9c231fdfc2eefbc9/docs/media/demo.mp4)

*Watch the [1:05 cube walkthrough (MP4)](https://raw.githubusercontent.com/ojops/rubiks-sim/a213fb717badee4ff2daedff9c231fdfc2eefbc9/docs/media/demo.mp4). Follow a seeded scramble through search and verified 3D playback, then see how both heuristics performed across 25 cases. [Chapters and reproduction](docs/DEMO.md).*

## Overview

Enter moves or generate a reproducible scramble, search for a solution within configurable limits, and animate the result. A sticker model handles geometry, while a compact corner and edge model supports search.

The bounded IDA* solver searches in increasing move counts. Distance tables tell it the fewest moves a simplified state could need, so it can skip branches that already exceed the current bound. [Recorded successes](docs/BENCHMARKS.md) reach an optimal depth of eight moves, but it does not efficiently solve arbitrary states. The video shows a computed solution verified against the cube model.

## Reproducible benchmark evidence

The [25-case multi-seed benchmark](benchmarks/results/multi-seed.md) compares the original `basic` bound with the `pattern` bound over lengths 4/6/8/10/20 and seeds 0–4, with two repetitions each. Under depth 10, 100,000-node, and two-second **warm-search** budgets:

- Basic solved **11/25** cases in both repetitions; pattern solved **15/25**.
- Across the **11 cases solved by both**, the median basic/pattern node ratio was **4.77×**, ranging from **1.00× to 183.42×**. This is a conditional node-count comparison, not an overall runtime speedup.
- The original six-move seed-0 result reproduced: **81,213 vs 1,777 nodes (45.7×)**. It is one case, not a typical improvement claim.
- Every returned solution passed independent sticker-model verification. Unfinished searches remain in the report; a time/node limit is not proof of unsolvability.

Reproduce after installation:

```bash
uv run python benchmarks/suite.py
```

This takes a few minutes and writes JSON plus a Markdown report to `benchmarks/results/multi-seed.*`. Each case/heuristic uses an isolated process, reporting cold table setup separately, warm runtime, nodes, termination status, and peak process RSS. RSS includes Python, NumPy, table construction, and repeated searches; it is not incremental search memory. Timings and time-limit outcomes vary by machine. This runner uses Unix `resource` and targets Linux/macOS.

For a quick smoke run without overwriting the committed report:

```bash
uv run python benchmarks/suite.py --lengths 4 --seeds 0 --repeats 1 --output /tmp/cube-smoke.json
```

### What to inspect

- `cube.py` / `cubie.py`: independent sticker geometry and compact search state, including physical validity constraints.
- `solver.py` / `patterns.py`: bounded IDA*, the original baseline, and admissible coordinate heuristics.
- `benchmarks/suite.py`: fixed seed grid, isolated workers, explicit budgets, and failure-aware summaries.
- `tests/test_benchmark_suite.py`: failure censoring and agreement of returned optimal depths; existing model/search tests check move correctness and heuristics.

The new suite measures the existing solver; it does not introduce a new heuristic or claim efficient arbitrary-state solving. The older [10-case report](docs/BENCHMARKS.md) uses a five-second budget and should not be mixed with the new two-second measurements.

## Features

- Exact sticker geometry and physically validated corner/edge states
- Reproducible scrambles and IDA* search with configurable limits
- Admissible corner/edge coordinate heuristics and a selectable original baseline
- Controlled benchmarks reporting nodes, setup/search time, and termination status
- Solution verification against an independent sticker model
- Command line scrambling, solving, and optional 3D rendering

Solving remains bounded: some ten move sequences and the benchmark twenty move sequence still exhaust the node limit. The scramble length is not necessarily optimal solution depth.

## Requirements and Installation

Requires Python 3.10 and [uv](https://docs.astral.sh/uv/). These commands target Ubuntu or WSL:

```bash
git clone https://github.com/ojops/rubiks-sim.git
cd rubiks-sim
uv sync --locked
```

To animate, install the ManimGL system prerequisites (including FFmpeg, Cairo, and Pango), then run `uv sync --locked --extra render`. Headless Linux rendering may also require Xvfb, xauth, and Mesa.

## Usage

To follow the film, generate its six-move scramble and solve it with the default heuristic.

```bash
uv run rubiks-sim --length 6 --seed 0 --solve --max-depth 6
```

The JSON lists the scramble `B' U' L' B' R' L` and the returned moves `R L' B L U B` in `search.solution`. Read the moves from left to right. The independent sticker model replays them and reports `"verified": true` when the cube is solved. If a cold run reaches the time limit, add `--time-limit 60`.

Generate a longer scramble, enter your own moves, or set a search budget with

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

The default heuristic builds tables once per process. Setup counts towards CLI elapsed time and time limits, and is reported as `setup_seconds`. See [benchmarks](docs/BENCHMARKS.md) for cold setup, warm searches, memory use, and cases that still reach limits.

The CLI returns JSON, including search statistics and solution verification when solving. Run `uv run rubiks-sim --help` for all options.

Render a scramble followed by its computed solution:

```bash
uv run --extra render rubiks-sim --scramble "R U F" --solve --render --low-quality
```

To save the JSON report alongside a render, append `> solve.json` to the command. Render progress goes to standard error. Output videos go to `videos/` by default. See [demo instructions](docs/DEMO.md) to generate the portfolio MP4 and looping preview.

## Implementation

`src/rubiks_sim/cube.py` tracks stickers, `cubie.py` tracks corners and edges, `solver.py` performs bounded IDA* search, and `sim.py` handles animation. Moves use `U D F B R L` for up, down, front, back, right, and left. Look directly at the named face. A plain letter turns it clockwise, a prime (`'`) turns it anticlockwise, and `2` makes a half turn. Reaching a search limit **does not** mean a cube is unsolvable.

See [algorithm details](docs/ALGORITHMS.md) for models, validity checks, API behavior, and search assumptions.

## Development Roadmap

Development is incremental, with an emphasis on correct cube states, robust search, and measured performance before more demanding demonstrations. The next solver milestone is a cross on a chosen face.

### Planned

- **Add cross solving:** solve the four cross edges on a chosen face, with side colours aligned to their centres. Add a cross-specific heuristic and CLI option, verify returned moves using the sticker model, and check shortest paths against exhaustive search on shallow cases. Benchmark seeded scrambles, including 20-move sequences, and report search limits and failures.
- **Add colour-neutral cross comparisons:** evaluate all six faces using the same move metric and report the shortest cross, including ties. Explore execution difficulty and the transition into the first F2L pair later. (long term, but I can dream)
- **Improve startup performance:** measure cold table setup separately from warm search. If persistent caching helps, validate the cache against the move-table version and rebuild corrupt or incompatible tables safely.
- **Extend measured search coverage beyond the completed 25-case suite:** test more seeds and deeper states while retaining unsuccessful searches. Measure successor generation cost before adding larger edge pattern databases.
- **Evaluate a two-phase solver:** compare coverage, correctness, and complexity with bounded IDA*. Optimal face-turn search and practical arbitrary-state solving have different goals.
- **Demonstrate harder scrambles when supported:** the film now shows the verified six-move, seed-0 case. For a deeper case, establish a reliable search budget and independently verify the solution before filming it.
- **Add random-state scrambling:** extend the seeded random-move generator with reproducible legal-state sampling. Aim for competition-worthy scrambles, with official compliance assessed separately.
- **Refine animation independently:** improve framing, pacing, and descriptive captions without coupling rendering to search.

Cross solving is planned, not yet implemented. Its output will identify a completed cross separately from a full-cube solution; benchmark claims will state the move metric and search budgets.

## Project Structure

```text
rubiks-sim/
├── src/rubiks_sim/
│   ├── cube.py          # Sticker geometry and face turns
│   ├── cubie.py         # Corner/edge states and validation
│   ├── solver.py        # Bounded IDA* solver
│   ├── patterns.py      # Exact coordinate distances and admissible bounds
│   ├── sim.py           # ManimGL visualisation
│   └── main.py          # Command line interface
├── scripts/             # Portfolio video and scene rendering
├── benchmarks/          # Legacy comparison, multi-seed suite, and recorded results
├── tests/               # Cube, solver, and rendering tests
├── docs/                # Algorithms, benchmarks, demo, and style notes
│   └── media/           # Preview GIF, MP4, and recorded data
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

When changing dependencies, commit both `pyproject.toml` and `uv.lock`. GitHub Actions runs code and rendering checks. See [coding conventions](docs/STYLE.md).

## License

[MIT licensed](LICENSE).
