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

def test_ida_star_does_not_modify_input_state():
    state = CubieState()
    state.apply_moves(["R", "U", "F"])

    original_state = CubieState(
        corner_permutation=state.corner_permutation,
        corner_orientation=state.corner_orientation,
        edge_permutation=state.edge_permutation,
        edge_orientation=state.edge_orientation,
    )

    ida_star(state, max_depth=8)

    assert state.corner_permutation == original_state.corner_permutation
    assert state.corner_orientation == original_state.corner_orientation
    assert state.edge_permutation == original_state.edge_permutation
    assert state.edge_orientation == original_state.edge_orientation