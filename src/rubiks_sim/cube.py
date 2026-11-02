"""Sticker geometry and exact face-turn rotations."""

from collections.abc import Iterable

import numpy as np

from rubiks_sim.notation import VALID_MOVES, parse_moves


class RubiksCube:
    """Represent a 3x3 cube using 54 stickers and exact integer geometry.

    Each sticker has a position, outward normal, and colour identifier.
    Coordinates use x for right, y for up, and z for front.
    """

    FACE_COLOURS = {
        "U": "W",  # White
        "D": "Y",  # Yellow
        "F": "G",  # Green
        "B": "B",  # Blue
        "R": "R",  # Red
        "L": "O",  # Orange
    }

    FACE_NORMALS = {
        "U": (0, 1, 0),
        "D": (0, -1, 0),
        "F": (0, 0, 1),
        "B": (0, 0, -1),
        "R": (1, 0, 0),
        "L": (-1, 0, 0),
    }

    X = 0
    Y = 1
    Z = 2

    FACE_AXES = {
        "R": (X, 1),
        "L": (X, -1),
        "U": (Y, 1),
        "D": (Y, -1),
        "F": (Z, 1),
        "B": (Z, -1),
    }

    VALID_MOVES = VALID_MOVES

    def __init__(self) -> None:
        self._initialise_solved_cube()

    def _initialise_solved_cube(self) -> None:
        """Create the 54 stickers of a solved cube."""

        positions = []
        normals = []
        colours = []

        for face, colour in self.FACE_COLOURS.items():
            for row in range(3):
                for col in range(3):
                    # Rows and columns are viewed from outside each face.

                    if face == "U":
                        position = (col - 1, 1, row - 1)

                    elif face == "D":
                        position = (col - 1, -1, 1 - row)

                    elif face == "F":
                        position = (col - 1, 1 - row, 1)

                    elif face == "B":
                        position = (1 - col, 1 - row, -1)

                    elif face == "R":
                        position = (1, 1 - row, 1 - col)

                    elif face == "L":
                        position = (-1, 1 - row, col - 1)

                    normal = self._face_normal(face)

                    positions.append(position)
                    normals.append(normal)
                    colours.append(colour)

        self.positions = np.array(positions, dtype=np.int8)

        self.normals = np.array(normals, dtype=np.int8)

        self.colours = np.array(colours, dtype="<U1")

    @classmethod
    def _face_normal(cls, face: str) -> tuple[int, int, int]:
        """Return the outward normal of a face."""
        return cls.FACE_NORMALS[face]

    @staticmethod
    def _rotation_matrix(axis: int, quarter_turns: int) -> np.ndarray:
        """Return an integer rotation matrix about the positive coordinate axis.

        Positive quarter turns follow the right-hand rule; two turns give 180°.
        """

        rotations = {
            0: np.array(
                [
                    [1, 0, 0],
                    [0, 0, -1],
                    [0, 1, 0],
                ]
            ),
            1: np.array(
                [
                    [0, 0, 1],
                    [0, 1, 0],
                    [-1, 0, 0],
                ]
            ),
            2: np.array(
                [
                    [0, -1, 0],
                    [1, 0, 0],
                    [0, 0, 1],
                ]
            ),
        }

        matrix = rotations[axis]

        # Powers of a +90° matrix also cover half turns and inverse turns.

        return np.linalg.matrix_power(matrix, quarter_turns % 4)

    def move(self, notation: str) -> None:
        """Apply one Singmaster move, such as R, U', or F2, in place.

        Reject non-string or unsupported notation before changing the cube.
        """

        if not isinstance(notation, str):
            raise TypeError("Move notation must be a string")

        if notation not in self.VALID_MOVES:
            raise ValueError(f"Invalid move: {notation}")

        face = notation[0]

        if notation.endswith("'"):
            turns = -1
        elif notation.endswith("2"):
            turns = 2
        else:
            turns = 1

        axis, sign = self.FACE_AXES[face]

        mask = self.positions[:, axis] == sign

        # Clockwise from outside is negative about the outward normal.

        quarter_turns = -sign * turns

        matrix = self._rotation_matrix(axis, quarter_turns)

        self.positions[mask] = self.positions[mask] @ matrix.T

        self.normals[mask] = self.normals[mask] @ matrix.T

    def is_solved(self) -> bool:
        """Return whether every face has its expected colour."""

        for face, normal in self.FACE_NORMALS.items():
            mask = np.all(self.normals == normal, axis=1)

            if not np.all(self.colours[mask] == self.FACE_COLOURS[face]):
                return False

        return True

    def apply_singmaster(self, singmaster: str | Iterable[str]) -> None:
        """Apply a space-separated string or iterable of Singmaster moves in place.

        Validate the whole sequence before changing the cube.
        """

        for move in parse_moves(singmaster):
            self.move(move)
