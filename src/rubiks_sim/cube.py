import numpy as np

class RubiksCube:
    """
    A 3x3 Rubik's Cube represented by 54 stickers

    Coordinates:
        x: left/right
        y: up/down
        z: front/back

    Each sticker has:
        position: 3D position
        normal: 3D direction
        colour: colour identifier
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

    VALID_MOVES = frozenset({
        "U", "U'", "U2",
        "D", "D'", "D2",
        "F", "F'", "F2",
        "B", "B'", "B2",
        "R", "R'", "R2",
        "L", "L'", "L2",
    })


    def __init__(self):
        self._initialise_solved_cube()


    def _initialise_solved_cube(self):
        """Create the 54 stickers of a solved cube"""

        positions = []
        normals = []
        colours = []

        # Each face is defined by its normal and the position of its nine stickers

        for face, colour in self.FACE_COLOURS.items():

            for row in range(3):
                for col in range(3):

                    # row = 0 is the top
                    # col = 0 is the left

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

        # Convert to numpy arrays

        self.positions = np.array(
            positions, dtype=np.int8
        )

        self.normals = np.array(
            normals, dtype=np.int8
        )

        self.colours = np.array(
            colours, dtype="<U1"
        )


    @classmethod
    def _face_normal(cls, face):
        """Return the outward normal of a face"""
        return cls.FACE_NORMALS[face]


    @staticmethod
    def _rotation_matrix(axis, quarter_turns):
        """
        Return an integer rotation matrix.

        quarter_turns:
            +1 = 90 degrees counterclockwise
            -1 = 90 degrees clockwise
             2 = 180 degrees
        """

        rotations = {
            0: np.array([
                [1, 0, 0],
                [0, 0, -1],
                [0, 1, 0],
            ]),

            1: np.array([
                [0, 0, 1],
                [0, 1, 0],
                [-1, 0, 0],
            ]),

            2: np.array([
                [0, -1, 0],
                [1, 0, 0],
                [0, 0, 1],
            ]),
        }

        matrix = rotations[axis]

        # Each matrix represents +90 degrees
        # Use powers for 180 and 270 degree rotations

        return np.linalg.matrix_power(
            matrix, quarter_turns % 4
        )


    def move(self, notation):
        """
        Apply one Singmaster move.

        Examples:
            cube.move("R")
            cube.move("U'")
            cube.move("F2")
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

        # Select stickers on the layer being turned
        # R: x = +1
        # L: x = -1
        # U: y = +1
        # D: y = -1
        # F: z = +1
        # B: z = -1

        mask = self.positions[:, axis] == sign

        # Clockwise when viewed from outside the face is a negative rotation around its outward normal

        quarter_turns = -sign * turns

        matrix = self._rotation_matrix(
            axis, quarter_turns
        )

        # Rotate the selected sticker positions
        self.positions[mask] = (
            self.positions[mask] @ matrix.T
        )

        # Rotate their normals as well
        self.normals[mask] = (
            self.normals[mask] @ matrix.T
        )


    def is_solved(self):
        """Return whether the cube is in its solved state"""
        
        for face, normal in self.FACE_NORMALS.items():
            mask = np.all(self.normals == normal, axis=1)

            if not np.all(self.colours[mask] == self.FACE_COLOURS[face]):
                return False

        return True


    def apply_singmaster(self, singmaster):
        """
        Apply a sequence of Singmaster moves
        Accepts a string or a list of moves
        """

        if isinstance(singmaster, str):
            moves = singmaster.split()
        else:
            moves = list(singmaster)

        invalid_moves = [
            move for move in moves
            if move not in self.VALID_MOVES
        ]

        if invalid_moves:
            raise ValueError(f"Invalid moves: {invalid_moves}")

        for move in moves:
            self.move(move)