import pytest

from rubiks_sim import cube
from rubiks_sim import scramble


def test_default_scramble_has_25_moves():
    assert len(scramble.generate_scramble()) == 25


def test_custom_scramble_length():
    assert len(scramble.generate_scramble(length=10)) == 10


def test_zero_length_scramble():
    assert scramble.generate_scramble(length=0) == []


def test_same_seed_produces_same_scramble():
    assert scramble.generate_scramble(seed=42) == scramble.generate_scramble(seed=42)


def test_scramble_contains_valid_moves():
    moves = scramble.generate_scramble()

    assert all(move in cube.RubiksCube.VALID_MOVES for move in moves)


def test_no_consecutive_moves_use_same_face():
    moves = scramble.generate_scramble()

    faces = [move[0] for move in moves]

    assert all(
        faces[i] != faces[i - 1]
        for i in range(1, len(faces))
    )


def test_negative_length_is_rejected():
    with pytest.raises(ValueError):
        scramble.generate_scramble(length=-1)