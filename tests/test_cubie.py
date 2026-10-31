import pytest

from rubiks_sim.cube import RubiksCube
from rubiks_sim.cubie import CubieState


@pytest.mark.parametrize(
    "move",
    [
        "U", "D", "F", "B", "R", "L",
        "U'", "D'", "F'", "B'", "R'", "L'",
        "U2", "D2", "F2", "B2", "R2", "L2",
    ],
)
def test_move_conversion(move):
    cube = RubiksCube()
    cube.move(move)

    state = CubieState.from_cube(cube)

    assert not state.is_solved()


def test_four_quarter_turns():
    cube = RubiksCube()

    for _ in range(4):
        cube.move("R")

    state = CubieState.from_cube(cube)

    assert state.is_solved()


def test_move_and_inverse():
    cube = RubiksCube()

    cube.move("U")
    cube.move("U'")

    state = CubieState.from_cube(cube)

    assert state.is_solved()


def invert_move(move):
    if move.endswith("2"):
        return move
    if move.endswith("'"):
        return move[0]
    return move + "'"


def test_scramble_and_inverse():
    cube = RubiksCube()

    moves = ["R", "U", "F'", "L2", "D", "B'"]
    inverse_moves = [
        invert_move(move)
        for move in reversed(moves)
    ]

    cube.apply_singmaster(moves)
    cube.apply_singmaster(inverse_moves)

    state = CubieState.from_cube(cube)

    assert state.is_solved()


def permutation_parity(permutation):
    inversions = 0

    for i in range(len(permutation)):
        for j in range(i + 1, len(permutation)):
            if permutation[i] > permutation[j]:
                inversions += 1

    return inversions % 2


def assert_valid_cubie_state(state):
    assert sorted(state.corner_permutation) == list(range(8))
    assert sorted(state.edge_permutation) == list(range(12))

    assert all(
        orientation in (0, 1, 2)
        for orientation in state.corner_orientation
    )

    assert all(
        orientation in (0, 1)
        for orientation in state.edge_orientation
    )

    assert sum(state.corner_orientation) % 3 == 0
    assert sum(state.edge_orientation) % 2 == 0

    assert (
        permutation_parity(state.corner_permutation)
        == permutation_parity(state.edge_permutation)
    )


def test_scrambled_cube_invariants():
    cube = RubiksCube()

    moves = ["R", "U", "F'", "L2", "D", "B'"]
    cube.apply_singmaster(moves)

    state = CubieState.from_cube(cube)

    assert_valid_cubie_state(state)

@pytest.mark.parametrize(
    "move",
    [
        "U", "D", "F", "B", "R", "L",
        "U'", "D'", "F'", "B'", "R'", "L'",
        "U2", "D2", "F2", "B2", "R2", "L2",
    ],
)
def test_cubie_move_matches_sticker_cube(move):
    cube = RubiksCube()
    state = CubieState()

    cube.move(move)
    state.apply_move(move)

    expected = CubieState.from_cube(cube)

    assert state.corner_permutation == expected.corner_permutation
    assert state.corner_orientation == expected.corner_orientation
    assert state.edge_permutation == expected.edge_permutation
    assert state.edge_orientation == expected.edge_orientation

def test_cubie_move_sequence_matches_sticker_cube():
    cube = RubiksCube()
    state = CubieState()

    moves = [
        "R", "U", "F'", "L2", "D", "B'",
        "U2", "R'", "F", "D2", "L", "B",
    ]

    for move in moves:
        cube.move(move)
        state.apply_move(move)

        expected = CubieState.from_cube(cube)

        assert state.corner_permutation == expected.corner_permutation
        assert state.corner_orientation == expected.corner_orientation
        assert state.edge_permutation == expected.edge_permutation
        assert state.edge_orientation == expected.edge_orientation