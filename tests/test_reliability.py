import random

import numpy as np
import pytest

from rubiks_sim import solver
from rubiks_sim.cube import RubiksCube
from rubiks_sim.cubie import CubieState
from rubiks_sim.main import main
from rubiks_sim.notation import MOVES


def state_key(state):
    return tuple(
        tuple(getattr(state, key))
        for key in (
            "corner_permutation",
            "corner_orientation",
            "edge_permutation",
            "edge_orientation",
        )
    )


def test_solver_exception_preserves_input(monkeypatch):
    state = CubieState()
    state.apply_moves("R U F")
    before = state_key(state)
    original = solver.heuristic
    calls = 0

    def interrupt(private):
        nonlocal calls
        calls += 1
        if calls == 8:
            raise KeyboardInterrupt
        return original(private)

    monkeypatch.setattr(solver, "heuristic", interrupt)
    with pytest.raises(KeyboardInterrupt):
        solver.ida_star(state)
    assert state_key(state) == before


@pytest.mark.parametrize(
    "limits,status",
    [
        ({"max_depth": 0}, "depth_limit"),
        ({"max_nodes": 5}, "node_limit"),
        ({"time_limit": 0}, "time_limit"),
    ],
)
def test_search_limits_preserve_input(limits, status):
    state = CubieState()
    state.apply_moves("R U F")
    before = state_key(state)
    result = solver.solve(state, **limits)
    assert result.status == status and result.solution is None
    assert state_key(state) == before
    assert result.nodes <= limits.get("max_nodes", float("inf"))


@pytest.mark.parametrize(
    "values",
    [
        {"corner_orientation": [1] + [0] * 7},
        {"edge_orientation": [1] + [0] * 11},
        {"edge_permutation": [1, 0] + list(range(2, 12))},
        {"corner_permutation": [0] * 8},
        {"corner_orientation": [0] * 7},
    ],
)
def test_unreachable_or_malformed_states_rejected(values):
    with pytest.raises(ValueError):
        CubieState(**values)


def test_conversion_rejects_changed_centres():
    cube = RubiksCube()
    cube.colours[4], cube.colours[22] = cube.colours[22], cube.colours[4]
    with pytest.raises(ValueError, match="Centre"):
        CubieState.from_cube(cube)


def test_invalid_sequences_are_atomic():
    cubie, cube = CubieState(), RubiksCube()
    for state, method in ((cubie, cubie.apply_moves), (cube, cube.apply_singmaster)):
        with pytest.raises(ValueError):
            method(iter(["R", "X"]))
        assert state.is_solved()


def test_precomputed_moves_match_sticker_geometry():
    rng = random.Random(8)
    cube, state = RubiksCube(), CubieState()
    for _ in range(200):
        move = rng.choice(MOVES)
        cube.move(move)
        state.apply_move(move)
        assert state_key(state) == state_key(CubieState.from_cube(cube))
    assert np.all(np.abs(cube.positions) <= 1)


def test_cli_verifies_solution(capsys):
    import json

    assert main(["--scramble", "R U F", "--solve"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["verified"] is True
    assert result["search"]["status"] == "solved"
