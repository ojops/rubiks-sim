# Rubik's Cube Simulator

A Python project for modelling and visualising Rubik's Cube operations using [ManimGL](https://github.com/3b1b/manim).

## Overview

This project aims to develop a Rubik's Cube simulator with a reliable representation of cube states, support for cube moves, and a solver designed with efficiency in mind.

## Features

- Rubik's Cube representation and state manipulation
- Cube move operations
- 3D visualisation and animation using ManimGL
- Development of an efficient solving algorithm

## Requirements

- Python 3.10
- [uv](https://docs.astral.sh/uv/)
- System dependencies required by ManimGL

The setup instructions below assume Ubuntu or WSL running Ubuntu.

## Installation

Clone the repository:

```bash
git clone https://github.com/ojops/rubiks-sim.git
cd rubiks-sim
```

Install the project dependencies:

```bash
uv sync --locked
```

## Usage

Render the `RubiksCubeTest` scene from the repository root:

```bash
uv run manimgl src/rubiks_sim/sim.py RubiksCubeTest -w
```

Alternatively, run from the source directory:

```bash
cd src/rubiks_sim
uv run manimgl sim.py RubiksCubeTest -w
```

Rendered videos are saved in the repository's `videos/` directory.


## Development Roadmap

The project is being developed incrementally, with an emphasis on correctness, efficient state representation, and visualisation.

### Planned

- **Testing:** Add automated tests for solver.py.
- **Scrambling:** Alter random scramble generation to produce more official scrambles.
- **Visualisation:** Add terminal actions to interact with cube and improve appearance.
- **Solving:** Develop and evaluate an efficient cube solving algorithm.
- **Performance:** Benchmark state manipulation and solving performance as the project develops.


## Project Structure

```text
rubiks-sim/
├── src/
│   └── rubiks_sim/   # Cube representation, simulation, and solver
├── tests/            # Automated tests
├── videos/           # Generated visualisations
├── pyproject.toml    # Project metadata and dependencies
├── uv.lock           # Locked dependency versions
├── .gitignore
├── LICENSE
└── README.md
```

## Development

Dependencies are managed using `uv`. Add a dependency with:

```bash
uv add package-name
```

Commit changes to both `pyproject.toml` and `uv.lock` when dependencies change.

Run automated tests with:

```bash
uv run pytest
```

## License

See [LICENSE](LICENSE) for details.
