import pytest

from rubiks_sim.cubie import CubieState
from rubiks_sim.solver import ida_star, heuristic


@pytest.mark.parametrize(
    "scramble",
    [
        ["R"],
        ["U", "R"],
        ["F", "U", "R"],
        ["R", "U", "F", "L"],
    ],
)
def test_ida_star_solves_shallow_scrambles(scramble):
    state = CubieState()
    state.apply_moves(scramble)

    solution = ida_star(state, max_depth=8)

    assert solution is not None

    state.apply_moves(solution)

    assert state.is_solved()


def test_ida_star_solved_cube():
    state = CubieState()

    solution = ida_star(state)

    assert solution == []


def test_heuristic_solved_cube():
    state = CubieState()

    assert heuristic(state) == 0


def test_heuristic_does_not_overestimate_one_move():
    for move in ("U", "D", "F", "B", "R", "L"):
        state = CubieState()
        state.apply_move(move)

        assert heuristic(state) <= 1