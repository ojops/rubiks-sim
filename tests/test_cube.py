import numpy as np
import pytest

from rubiks_sim.cube import RubiksCube


@pytest.fixture
def cube():
    """Return a newly initialised Rubik's Cube"""
    return RubiksCube()


def test_cube_has_54_stickers(cube):
    """The cube should have 54 stickers"""
    assert cube.positions.shape == (54, 3)
    assert cube.normals.shape == (54, 3)
    assert cube.colours.shape == (54,)


def test_cube_has_six_colours(cube):
    """A solved cube should have six colour identifiers"""
    assert set(cube.colours) == {"W", "Y", "G", "B", "R", "O"}


def test_stickers_have_unique_position_and_normal_pairs(cube):
    """Each sticker should have a unique (position, normal) pair"""

    stickers = {
        (tuple(position), tuple(normal))
        for position, normal in zip(
            cube.positions,
            cube.normals,
        )
    }

    assert len(stickers) == 54


def test_stickers_are_on_cube_surface(cube):
    """Every sticker should lie on the surface of the cube"""

    assert np.all(
        np.max(np.abs(cube.positions), axis=1) == 1
    )


def test_r_move_only_affects_right_layer(cube):
    """An R move should only affect stickers initially on x = 1"""

    original_positions = cube.positions.copy()
    original_normals = cube.normals.copy()

    cube.move("R")

    # Stickers outside the right layer must be unchanged
    outside_right_layer = original_positions[:, 0] != 1

    np.testing.assert_array_equal(
        cube.positions[outside_right_layer],
        original_positions[outside_right_layer],
    )

    np.testing.assert_array_equal(
        cube.normals[outside_right_layer],
        original_normals[outside_right_layer],
    )


def test_r_move_changes_right_layer_stickers(cube):
    """An R move should change the positions of non-centre stickers on x = 1"""

    original_positions = cube.positions.copy()

    cube.move("R")

    right_layer = original_positions[:, 0] == 1

    # Exclude the centre sticker of the R face
    right_face_centre = (
        (original_positions[:, 0] == 1)
        & (original_positions[:, 1] == 0)
        & (original_positions[:, 2] == 0)
    )

    expected_to_change = right_layer & ~right_face_centre

    changed = np.any(
        cube.positions != original_positions,
        axis=1,
    )

    np.testing.assert_array_equal(
        changed,
        expected_to_change,
    )


@pytest.mark.parametrize(
    "move",
    ["U", "D", "F", "B", "R", "L"],
)
def test_four_quarter_turns_restore_cube(cube, move):
    """Four quarter turns of a face should restore the cube"""
    original_positions = cube.positions.copy()
    original_normals = cube.normals.copy()

    for _ in range(4):
        cube.move(move)

    np.testing.assert_array_equal(
        cube.positions,
        original_positions,
    )

    np.testing.assert_array_equal(
        cube.normals,
        original_normals,
    )


@pytest.mark.parametrize(
    ("move", "inverse"),
    [
        ("U", "U'"),
        ("D", "D'"),
        ("F", "F'"),
        ("B", "B'"),
        ("R", "R'"),
        ("L", "L'"),
    ],
)
def test_move_and_inverse_restore_cube(cube, move, inverse):
    """A move followed by its inverse should restore the cube"""
    original_positions = cube.positions.copy()
    original_normals = cube.normals.copy()

    cube.move(move)
    cube.move(inverse)

    np.testing.assert_array_equal(
        cube.positions,
        original_positions,
    )

    np.testing.assert_array_equal(
        cube.normals,
        original_normals,
    )


@pytest.mark.parametrize(
    "move",
    ["U", "D", "F", "B", "R", "L"],
)
def test_half_turn_equals_two_quarter_turns(move):
    """A half turn should equal two quarter turns"""
    cube_half = RubiksCube()
    cube_double = RubiksCube()

    cube_half.move(move + "2")

    cube_double.move(move)
    cube_double.move(move)

    np.testing.assert_array_equal(
        cube_half.positions,
        cube_double.positions,
    )

    np.testing.assert_array_equal(
        cube_half.normals,
        cube_double.normals,
    )


def test_move_preserves_colours(cube):
    """Moving the cube should not change sticker colours"""
    original_colours = cube.colours.copy()

    cube.apply_singmaster("R U F' L2 D B")

    np.testing.assert_array_equal(
        cube.colours,
        original_colours,
    )


def test_apply_singmaster_string(cube):
    """A string of moves should be accepted"""
    cube.apply_singmaster("R U R' U'")

    assert not np.array_equal(
        cube.positions,
        RubiksCube().positions,
    )


def test_apply_singmaster_list(cube):
    """A list of moves should be accepted"""
    cube.apply_singmaster(["R", "U", "R'", "U'"])

    assert not np.array_equal(
        cube.positions,
        RubiksCube().positions,
    )


def test_apply_singmaster_string_and_list_are_equivalent():
    string_cube = RubiksCube()
    list_cube = RubiksCube()

    string_cube.apply_singmaster("R U R' U'")
    list_cube.apply_singmaster(["R", "U", "R'", "U'"])

    np.testing.assert_array_equal(
        string_cube.positions,
        list_cube.positions,
    )
    np.testing.assert_array_equal(
        string_cube.normals,
        list_cube.normals,
    )
    np.testing.assert_array_equal(
        string_cube.colours,
        list_cube.colours,
    )


@pytest.mark.parametrize(
    "move",
    ["X", "R3", "U4", "", "RR"],
)
def test_invalid_move_raises_value_error(cube, move):
    """Unsupported move notation should raise ValueError"""
    with pytest.raises(ValueError):
        cube.move(move)


def test_non_string_move_raises_type_error(cube):
    """Non string move notation should raise TypeError"""
    with pytest.raises(TypeError):
        cube.move(123)

def test_is_solved():
    """A newly initialised cube should be solved"""
    cube = RubiksCube()

    assert cube.is_solved()

    cube.apply_singmaster("R U R' U'")

    assert not cube.is_solved()
