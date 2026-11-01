from rubiks_sim.notation import parse_moves


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
            list(range(8)) if corner_permutation is None else list(corner_permutation)
        )

        self.corner_orientation = (
            [0] * 8 if corner_orientation is None else list(corner_orientation)
        )

        self.edge_permutation = (
            list(range(12)) if edge_permutation is None else list(edge_permutation)
        )

        self.edge_orientation = (
            [0] * 12 if edge_orientation is None else list(edge_orientation)
        )
        self.validate()

    def copy(self):
        return type(self)(
            self.corner_permutation,
            self.corner_orientation,
            self.edge_permutation,
            self.edge_orientation,
        )

    def validate(self) -> None:
        """Reject malformed or physically unreachable cubie states."""
        for name, values, size, modulus in (
            ("corner_permutation", self.corner_permutation, 8, None),
            ("edge_permutation", self.edge_permutation, 12, None),
            ("corner_orientation", self.corner_orientation, 8, 3),
            ("edge_orientation", self.edge_orientation, 12, 2),
        ):
            if len(values) != size or any(type(v) is not int for v in values):
                raise ValueError(f"{name} must contain {size} integers")
            if modulus is None:
                if sorted(values) != list(range(size)):
                    raise ValueError(f"{name} must be a permutation of range({size})")
            elif any(v < 0 or v >= modulus for v in values) or sum(values) % modulus:
                raise ValueError(f"Invalid {name}: range or orientation sum")

        def parity(values):
            return sum(a > b for i, a in enumerate(values) for b in values[i + 1 :]) % 2

        if parity(self.corner_permutation) != parity(self.edge_permutation):
            raise ValueError("Corner and edge permutation parity must match")

    @classmethod
    def from_cube(cls, cube):
        """
        Convert the 54 sticker RubiksCube into a CubieState
        """

        if (
            cube.positions.shape != (54, 3)
            or cube.normals.shape != (54, 3)
            or cube.colours.shape != (54,)
        ):
            raise ValueError("Expected 54 stickers with 3D positions and normals")
        # Convert each sticker normal into its face letter
        normal_to_face = {normal: face for face, normal in cls.FACE_NORMALS.items()}

        # Group stickers according to their cubie positions
        stickers_by_position = {}
        seen = set()

        for position, normal, colour in zip(
            cube.positions,
            cube.normals,
            cube.colours,
        ):
            position_key = tuple(position)
            normal_key = tuple(normal)
            if (
                any(v not in (-1, 0, 1) for v in position_key)
                or normal_key not in normal_to_face
                or sum(p * n for p, n in zip(position_key, normal_key)) != 1
                or (position_key, normal_key) in seen
            ):
                raise ValueError("Invalid or duplicate sticker position/normal")
            seen.add((position_key, normal_key))
            face = normal_to_face[normal_key]
            if position_key == normal_key and colour != cls.FACE_COLOURS[face]:
                raise ValueError("Centre colours must match the fixed face convention")

            stickers_by_position.setdefault(position_key, {})[face] = str(colour)

        # Map each combination of corner then edge colours to its piece ID
        corner_piece_ids = {
            frozenset(cls.FACE_COLOURS[face] for face in faces): piece_id
            for piece_id, faces in enumerate(cls.CORNER_FACES)
        }

        edge_piece_ids = {
            frozenset(cls.FACE_COLOURS[face] for face in faces): piece_id
            for piece_id, faces in enumerate(cls.EDGE_FACES)
        }

        corner_permutation = []
        corner_orientation = []

        for position_faces in cls.CORNER_FACES:
            # Find the sticker colours at given corner position
            position = tuple(
                sum(cls.FACE_NORMALS[face][axis] for face in position_faces)
                for axis in range(3)
            )

            observed = stickers_by_position[position]

            # Identify which corner occupies this position
            observed_colours = tuple(observed[face] for face in position_faces)

            piece_id = corner_piece_ids.get(frozenset(observed_colours))
            if piece_id is None:
                raise ValueError("Invalid corner colours")

            corner_permutation.append(piece_id)

            # Find the orientation by comparing cyclic rotations
            piece_faces = cls.CORNER_FACES[piece_id]
            piece_colours = tuple(cls.FACE_COLOURS[face] for face in piece_faces)

            orientation = next(
                (
                    shift
                    for shift in range(3)
                    if tuple(piece_colours[(i - shift) % 3] for i in range(3))
                    == observed_colours
                ),
                None,
            )
            if orientation is None:
                raise ValueError("Invalid corner orientation")

            corner_orientation.append(orientation)

        edge_permutation = []
        edge_orientation = []

        for position_faces in cls.EDGE_FACES:
            position = tuple(
                sum(cls.FACE_NORMALS[face][axis] for face in position_faces)
                for axis in range(3)
            )

            observed = stickers_by_position[position]

            observed_colours = tuple(observed[face] for face in position_faces)

            piece_id = edge_piece_ids.get(frozenset(observed_colours))
            if piece_id is None:
                raise ValueError("Invalid edge colours")

            edge_permutation.append(piece_id)

            piece_faces = cls.EDGE_FACES[piece_id]
            piece_colours = tuple(cls.FACE_COLOURS[face] for face in piece_faces)

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
        self._apply_table(self.MOVE_TABLES[face])

    def _apply_table(self, table):
        corner_perm, corner_delta, edge_perm, edge_delta = table

        old_corner_permutation = self.corner_permutation
        old_corner_orientation = self.corner_orientation

        old_edge_permutation = self.edge_permutation
        old_edge_orientation = self.edge_orientation

        self.corner_permutation = [
            old_corner_permutation[source] for source in corner_perm
        ]

        self.corner_orientation = [
            (old_corner_orientation[source] + delta) % 3
            for source, delta in zip(corner_perm, corner_delta)
        ]

        self.edge_permutation = [old_edge_permutation[source] for source in edge_perm]

        self.edge_orientation = [
            (old_edge_orientation[source] + delta) % 2
            for source, delta in zip(edge_perm, edge_delta)
        ]

    def apply_move(self, move):
        """Apply one singmaster move to the cubie state"""

        if not isinstance(move, str):
            raise TypeError("Move notation must be a string")

        if move not in FULL_MOVE_TABLES:
            raise ValueError(f"Invalid move: {move}")
        self._apply_table(FULL_MOVE_TABLES[move])

    def apply_moves(self, moves):
        """Apply a sequence atomically with respect to invalid notation."""
        for move in parse_moves(moves):
            self.apply_move(move)


def _build_full_move_tables():
    tables = {}
    for face in CubieState.MOVE_TABLES:
        state = CubieState()
        for suffix in ("", "2", "'"):
            state._apply_quarter_turn(face)
            tables[face + suffix] = tuple(
                tuple(values)
                for values in (
                    state.corner_permutation,
                    state.corner_orientation,
                    state.edge_permutation,
                    state.edge_orientation,
                )
            )
    return tables


FULL_MOVE_TABLES = _build_full_move_tables()
