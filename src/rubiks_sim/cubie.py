
class CubieState:
    """
    Represents a rubik's cube using corner and edge pieces
    Corner and edge positions follow a fixed ordering
    Permutation identifies which piece occupies each position
    Orientation describes how each piece is rotated
    """

    # Face convention
    # U = +Y, D = -Y
    # F = +Z, B = -Z
    # R = +X, L = -X

    CORNER_FACES = (
        ("U", "R", "F"),  # URF
        ("U", "F", "L"),  # UFL
        ("U", "L", "B"),  # ULB
        ("U", "B", "R"),  # UBR
        ("D", "F", "R"),  # DFR
        ("D", "L", "F"),  # DLF
        ("D", "B", "L"),  # DBL
        ("D", "R", "B"),  # DRB
    )

    EDGE_FACES = (
        ("U", "R"),  # UR
        ("U", "F"),  # UF
        ("U", "L"),  # UL
        ("U", "B"),  # UB
        ("D", "R"),  # DR
        ("D", "F"),  # DF
        ("D", "L"),  # DL
        ("D", "B"),  # DB
        ("F", "R"),  # FR
        ("F", "L"),  # FL
        ("B", "L"),  # BL
        ("B", "R"),  # BR
    )

    FACE_NORMALS = {
        "U": (0, 1, 0),
        "D": (0, -1, 0),
        "F": (0, 0, 1),
        "B": (0, 0, -1),
        "R": (1, 0, 0),
        "L": (-1, 0, 0),
    }

    # Colours used by existing cube.py
    FACE_COLOURS = {
        "U": "W",
        "D": "Y",
        "F": "G",
        "B": "B",
        "R": "R",
        "L": "O",
    }

    MOVE_TABLES = {
        # Each entry:
        # corner permutation, corner orientation, edge permutation, and edge orientation
        # Permutation tells us which old position supplies each new position
        # Orientation gives the change at each new position

        "U": (
            (3, 0, 1, 2, 4, 5, 6, 7),
            (0, 0, 0, 0, 0, 0, 0, 0),
            (3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ),

        "D": (
            (0, 1, 2, 3, 5, 6, 7, 4),
            (0, 0, 0, 0, 0, 0, 0, 0),
            (0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ),

        "F": (
            (1, 5, 2, 3, 0, 4, 6, 7),
            (1, 2, 0, 0, 2, 1, 0, 0),
            (0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11),
            (0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0),
        ),

        "B": (
            (0, 1, 3, 7, 4, 5, 2, 6),
            (0, 0, 1, 2, 0, 0, 2, 1),
            (0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7),
            (0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1),
        ),

        "R": (
            (4, 1, 2, 0, 7, 5, 6, 3),
            (2, 0, 0, 1, 1, 0, 0, 2),
            (8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ),

        "L": (
            (0, 2, 6, 3, 4, 1, 5, 7),
            (0, 1, 2, 0, 0, 2, 1, 0),
            (0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ),
    }

    def __init__(
        self,
        corner_permutation=None,
        corner_orientation=None,
        edge_permutation=None,
        edge_orientation=None,
    ):
        self.corner_permutation = (
            list(range(8))
            if corner_permutation is None
            else list(corner_permutation)
        )

        self.corner_orientation = (
            [0] * 8
            if corner_orientation is None
            else list(corner_orientation)
        )

        self.edge_permutation = (
            list(range(12))
            if edge_permutation is None
            else list(edge_permutation)
        )

        self.edge_orientation = (
            [0] * 12
            if edge_orientation is None
            else list(edge_orientation)
        )

    @classmethod
    def from_cube(cls, cube):
        """
        Convert the 54 sticker RubiksCube into a CubieState
        """

        # Convert each sticker normal into its face letter
        normal_to_face = {
            normal: face
            for face, normal in cls.FACE_NORMALS.items()
        }

        # Group stickers according to their cubie positions
        stickers_by_position = {}

        for position, normal, colour in zip(
            cube.positions,
            cube.normals,
            cube.colours,
        ):
            position_key = tuple(int(value) for value in position)
            face = normal_to_face[
                tuple(int(value) for value in normal)
            ]

            stickers_by_position.setdefault(
                position_key, {}
            )[face] = str(colour)

        # Map each combination of corner then edge colours to its piece ID
        corner_piece_ids = {
            frozenset(
                cls.FACE_COLOURS[face]
                for face in faces
            ): piece_id
            for piece_id, faces in enumerate(cls.CORNER_FACES)
        }

        edge_piece_ids = {
            frozenset(
                cls.FACE_COLOURS[face]
                for face in faces
            ): piece_id
            for piece_id, faces in enumerate(cls.EDGE_FACES)
        }

        corner_permutation = []
        corner_orientation = []

        for position_faces in cls.CORNER_FACES:
            # Find the sticker colours at given corner position
            position = tuple(
                sum(cls.FACE_NORMALS[face][axis]
                    for face in position_faces)
                for axis in range(3)
            )

            observed = stickers_by_position[position]

            # Identify which corner occupies this position
            observed_colours = tuple(
                observed[face]
                for face in position_faces
            )

            piece_id = corner_piece_ids[
                frozenset(observed_colours)
            ]

            corner_permutation.append(piece_id)

            # Find the orientation by comparing cyclic rotations
            piece_faces = cls.CORNER_FACES[piece_id]
            piece_colours = tuple(
                cls.FACE_COLOURS[face]
                for face in piece_faces
            )

            orientation = next(
                shift
                for shift in range(3)
                if tuple(
                    piece_colours[(i - shift) % 3]
                    for i in range(3)
                ) == observed_colours
            )

            corner_orientation.append(orientation)

        edge_permutation = []
        edge_orientation = []

        for position_faces in cls.EDGE_FACES:
            position = tuple(
                sum(cls.FACE_NORMALS[face][axis]
                    for face in position_faces)
                for axis in range(3)
            )

            observed = stickers_by_position[position]

            observed_colours = tuple(
                observed[face]
                for face in position_faces
            )

            piece_id = edge_piece_ids[
                frozenset(observed_colours)
            ]

            edge_permutation.append(piece_id)

            piece_faces = cls.EDGE_FACES[piece_id]
            piece_colours = tuple(
                cls.FACE_COLOURS[face]
                for face in piece_faces
            )

            if observed_colours == piece_colours:
                orientation = 0
            elif observed_colours == piece_colours[::-1]:
                orientation = 1
            else:
                raise ValueError("Invalid edge orientation")

            edge_orientation.append(orientation)

        return cls(
            corner_permutation=corner_permutation,
            corner_orientation=corner_orientation,
            edge_permutation=edge_permutation,
            edge_orientation=edge_orientation,
        )

    def is_solved(self):
        """Return True if the cube is in its solved state"""

        return (
            self.corner_permutation == list(range(8))
            and self.corner_orientation == [0] * 8
            and self.edge_permutation == list(range(12))
            and self.edge_orientation == [0] * 12
        )

    def __repr__(self):
        return (
            f"CubieState("
            f"corner_permutation={self.corner_permutation}, "
            f"corner_orientation={self.corner_orientation}, "
            f"edge_permutation={self.edge_permutation}, "
            f"edge_orientation={self.edge_orientation})"
        )

    def _apply_quarter_turn(self, face):
        corner_perm, corner_delta, edge_perm, edge_delta = (
            self.MOVE_TABLES[face]
        )

        old_corner_permutation = self.corner_permutation
        old_corner_orientation = self.corner_orientation

        old_edge_permutation = self.edge_permutation
        old_edge_orientation = self.edge_orientation

        self.corner_permutation = [
            old_corner_permutation[source]
            for source in corner_perm
        ]

        self.corner_orientation = [
            (old_corner_orientation[source] + delta) % 3
            for source, delta in zip(corner_perm, corner_delta)
        ]

        self.edge_permutation = [
            old_edge_permutation[source]
            for source in edge_perm
        ]

        self.edge_orientation = [
            (old_edge_orientation[source] + delta) % 2
            for source, delta in zip(edge_perm, edge_delta)
        ]

    def apply_move(self, move):
        """Apply one singmaster move to the cubie state"""

        if not isinstance(move, str):
            raise TypeError("Move notation must be a string")

        if move not in {
            f + suffix
            for f in self.MOVE_TABLES
            for suffix in ("", "'", "2")
        }:
            raise ValueError(f"Invalid move: {move}")

        face = move[0]

        if move.endswith("2"):
            turns = 2
        elif move.endswith("'"):
            turns = 3
        else:
            turns = 1

        for _ in range(turns):
            self._apply_quarter_turn(face)

    def apply_moves(self, moves):
        """Apply a sequence of singmaster moves"""

        if isinstance(moves, str):
            moves = moves.split()

        for move in moves:
            self.apply_move(move)