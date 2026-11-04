"""Run with uv run python benchmarks/solver.py, times are machine dependent"""

import json
from dataclasses import asdict

from rubiks_sim.cubie import CubieState
from rubiks_sim.scramble import generate_scramble
from rubiks_sim.solver import solve

for length, seed in ((4, 0), (5, 0), (6, 0), (20, 42)):
    state = CubieState()
    moves = generate_scramble(length, seed)
    state.apply_moves(moves)
    result = solve(state, max_nodes=100_000, time_limit=5)
    print(json.dumps({"scramble": moves, **asdict(result)}))
