"""Seeded random move sequences for demonstrations and search experiments."""

import random


def generate_scramble(
    length: int = 25, seed: int | float | str | bytes | bytearray | None = None
) -> list[str]:
    """Return random face moves without consecutive turns of the same face.

    Supply a seed for repeatable output. Reject non-integer or negative lengths.
    This produces random move sequences, not uniform random cube states.
    """

    if not isinstance(length, int) or isinstance(length, bool):
        raise TypeError("length must be an integer")

    if length < 0:
        raise ValueError("length must be non-negative")

    rng = random.Random(seed)

    faces = ("U", "D", "F", "B", "R", "L")
    suffixes = ("", "'", "2")

    moves = []
    previous_face = None

    for _ in range(length):
        available_faces = [face for face in faces if face != previous_face]

        face = rng.choice(available_faces)
        suffix = rng.choice(suffixes)

        moves.append(face + suffix)
        previous_face = face

    return moves
