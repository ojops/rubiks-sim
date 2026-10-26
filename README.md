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

- **Testing:** Add automated tests for cube state integrity, move operations, and move sequences.
- **State validation:** Implement checks for cube state consistency and move correctness.
- **Scrambling:** Generate random cube scrambles using standard move notation.
- **Visualisation:** Connect the cube representation to ManimGL for 3D rendering and animation.
- **Solving:** Develop and evaluate an efficient cube-solving algorithm.
- **Performance:** Benchmark state manipulation and solving performance as the project develops.


## Project Structure

```text
rubiks-sim/
├── src/
│   └── rubiks_sim/
│       ├── cube.py
│       ├── sim.py
│       ├── solver.py
│       └── custom_config.yml
├── videos/
├── custom_config.yml
├── pyproject.toml
├── uv.lock
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

## License

See [LICENSE](LICENSE) for details.
