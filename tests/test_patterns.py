"""Admissibility, optimal depth, resource limits, and independent verification."""

import random
from collections import deque
from itertools import permutations

import pytest

from rubiks_sim import patterns, solver
from rubiks_sim.cube import RubiksCube
from rubiks_sim.cubie import CubieState
from rubiks_sim.notation import MOVES
from rubiks_sim.patterns import permutation_index, prepare_patterns
from rubiks_sim.solver import basic_heuristic, heuristic, solve


def key(state):
    return tuple(
        tuple(values)
        for values in (
            state.corner_permutation,
            state.corner_orientation,
            state.edge_permutation,
            state.edge_orientation,
        )
    )


def test_complete_dense_tables_and_permutation_ranks():
    tables = prepare_patterns()
    assert tuple(map(len, tables)) == (2187, 2048, 40320)
    assert all(table[0] == 0 and 255 not in table for table in tables)
    assert all(
        permutation_index(state) == rank
        for rank, state in enumerate(permutations(range(8)))
    )


def test_admissible_on_every_state_within_three_moves():
    initial = CubieState()
    queue = deque([(initial, 0)])
    seen = {key(initial)}
    while queue:
        state, distance = queue.popleft()
        assert basic_heuristic(state) <= heuristic(state) <= distance
        if distance == 3:
            continue
        for move in MOVES:
            child = state.copy()
            child.apply_move(move)
            identity = key(child)
            if identity not in seen:
                seen.add(identity)
                queue.append((child, distance + 1))
    assert len(seen) > 3000


def test_consistency_on_deep_random_walks():
    rng, state = random.Random(731), CubieState()
    for _ in range(200):
        before = heuristic(state)
        state.apply_move(rng.choice(MOVES))
        assert abs(heuristic(state) - before) <= 1


@pytest.mark.parametrize("scramble", ["R U F2 L", "U2 D2 F2 R2 B2", "R U F L B D"])
def test_stronger_search_preserves_optimal_depth_and_sticker_solution(scramble):
    cube = RubiksCube()
    cube.apply_singmaster(scramble)
    state = CubieState.from_cube(cube)
    old = solve(state, max_depth=6, max_nodes=300_000, heuristic_name="basic")
    new = solve(state, max_depth=6, max_nodes=300_000)
    assert new.status == "solved"
    if old.solution is not None:
        assert len(new.solution) == len(old.solution)
    assert new.nodes < old.nodes
    cube.apply_singmaster(new.solution)
    assert cube.is_solved()
    assert solve(state, max_depth=len(new.solution) - 1).status == "depth_limit"


def test_zero_budgets_do_not_build_tables(monkeypatch):
    monkeypatch.setattr(patterns, "_TABLES", None)
    state = CubieState()
    state.apply_moves("R U F")
    assert solve(state, max_nodes=0).status == "node_limit"
    assert solve(state, time_limit=0).status == "time_limit"
    assert patterns._TABLES is None


def test_time_limit_covers_cold_pattern_generation(monkeypatch):
    monkeypatch.setattr(patterns, "_TABLES", None)
    ticks = iter(range(100))
    monkeypatch.setattr(solver, "perf_counter", lambda: next(ticks))
    state = CubieState()
    state.apply_moves("R U F")
    before = key(state)
    result = solve(state, time_limit=7)
    assert result.status == "time_limit" and result.nodes == 0
    assert result.setup_seconds > 0
    assert patterns._TABLES is None
    assert key(state) == before


def test_invalid_mutated_state_rejected_before_search():
    state = CubieState()
    state.corner_orientation[0] = 1
    with pytest.raises(ValueError):
        solve(state)
