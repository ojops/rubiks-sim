import random


def generate_scramble(length=25, seed=None):
    """Generate a reproducible sequence of random face moves"""

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
        available_faces = [
            face for face in faces
            if face != previous_face
        ]

        face = rng.choice(available_faces)
        suffix = rng.choice(suffixes)

        moves.append(face + suffix)
        previous_face = face

    return moves