"""ManimGL scenes driven by the exact sticker model."""

from collections.abc import Iterable

import numpy as np
from manimlib import (
    BLACK,
    BLUE,
    GREEN,
    ORANGE,
    ORIGIN,
    OUT,
    PI,
    RED,
    RIGHT,
    UP,
    WHITE,
    YELLOW,
    Cube,
    Group,
    InteractiveScene,
    Rotate,
    Square,
    smooth,
)

from rubiks_sim.cube import RubiksCube
from rubiks_sim.notation import parse_moves
from rubiks_sim.scramble import generate_scramble

STICKER_COLOURS = {
    "W": WHITE,
    "Y": YELLOW,
    "G": GREEN,
    "B": BLUE,
    "R": RED,
    "O": ORANGE,
}

# Map outward normals to the rotations of a square initially facing +Z.
FACE_ROTATIONS = {
    (0, 0, 1): (0, OUT),
    (0, 0, -1): (PI, RIGHT),
    (0, 1, 0): (-PI / 2, RIGHT),
    (0, -1, 0): (PI / 2, RIGHT),
    (1, 0, 0): (PI / 2, UP),
    (-1, 0, 0): (-PI / 2, UP),
}

CUBIE_SIZE = 0.96
STICKER_SIZE = 0.88
STICKER_OFFSET = CUBIE_SIZE / 2 + 0.01


def create_sticker(position: np.ndarray, normal: np.ndarray, colour: str) -> Square:
    """Return a coloured square aligned with a cubie's outward normal."""

    sticker = Square(
        side_length=STICKER_SIZE,
        stroke_color=BLACK,
        stroke_width=1.5,
    )

    sticker.set_fill(STICKER_COLOURS[str(colour)], opacity=1)

    normal_key = tuple(int(value) for value in normal)
    angle, axis = FACE_ROTATIONS[normal_key]

    sticker.rotate(angle, axis=axis)

    # Offset from the body to prevent overlapping surfaces.
    sticker.move_to(position + STICKER_OFFSET * normal)

    return sticker


class AnimatedRubiksCube(InteractiveScene):
    """Animate supplied moves, or a seeded 20-move demonstration by default."""

    moves: str | Iterable[str] | None = None

    def construct(self) -> None:
        """Build a solved cube and play the selected move sequence."""
        self.cube = RubiksCube()

        self.frame.reorient(
            theta_degrees=-45,
            phi_degrees=70,
        )

        self.cubies = []

        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                for z in (-1, 0, 1):
                    position = np.array([x, y, z])

                    sticker_indices = np.flatnonzero(
                        np.all(self.cube.positions == position, axis=1)
                    )

                    body = Cube(side_length=CUBIE_SIZE)
                    body.set_color(BLACK)
                    body.set_opacity(1)
                    body.move_to(position)
                    body.apply_depth_test()

                    stickers = []

                    for i in sticker_indices:
                        sticker = create_sticker(
                            position,
                            self.cube.normals[i],
                            self.cube.colours[i],
                        )

                        sticker.apply_depth_test()
                        stickers.append(sticker)

                    cubie_group = Group(body, *stickers)

                    self.cubies.append(
                        {
                            "position": position,
                            "indices": sticker_indices,
                            "body": body,
                            "stickers": stickers,
                            "group": cubie_group,
                        }
                    )

        self.add(*[cubie["group"] for cubie in self.cubies])

        self.wait()

        scramble = (
            parse_moves(self.moves)
            if self.moves is not None
            else generate_scramble(length=20, seed=42)
        )

        print("Scramble:", " ".join(scramble))

        self.animate_moves(scramble, run_time=0.3)

        self.wait()

    def animate_move(self, notation: str, run_time: float = 0.6) -> None:
        """Animate one Singmaster move and update the sticker model.

        run_time is seconds per quarter turn; half turns take twice as long.
        Reject invalid notation before playback starts.
        """

        parse_moves([notation])
        face = notation[0]
        axis, sign = self.cube.FACE_AXES[face]

        if notation.endswith("'"):
            turns = -1
        elif notation.endswith("2"):
            turns = 2
        else:
            turns = 1

        quarter_turns = -sign * turns
        angle = quarter_turns * PI / 2

        layer_cubies = []

        for cubie in self.cubies:
            # The central core has no stickers and never moves.
            if len(cubie["indices"]) == 0:
                continue

            # All stickers on a cubie share the same position.
            sticker_index = cubie["indices"][0]
            position = self.cube.positions[sticker_index]

            if position[axis] == sign:
                layer_cubies.append(cubie["group"])

        layer = Group(*layer_cubies)

        rotation_axis = np.eye(3)[axis]

        self.play(
            Rotate(
                layer,
                angle=angle,
                axis=rotation_axis,
                about_point=ORIGIN,
            ),
            run_time=run_time * abs(turns),
            rate_func=smooth,
        )

        self.cube.move(notation)

        # Rebuild sticker geometry from exact coordinates to avoid visual drift.
        for cubie in self.cubies:
            indices = cubie["indices"]

            if len(indices) == 0:
                continue

            # Sticker identities stay attached to cubies after every turn.
            new_position = self.cube.positions[indices[0]].astype(float)

            cubie["body"].move_to(new_position)

            for sticker, i in zip(cubie["stickers"], indices):
                updated_sticker = create_sticker(
                    new_position,
                    self.cube.normals[i],
                    self.cube.colours[i],
                )

                sticker.become(updated_sticker)
                sticker.apply_depth_test()

    def animate_moves(self, moves: str | Iterable[str], run_time: float = 0.6) -> None:
        """Validate the whole sequence, then animate each move in order.

        run_time is seconds per quarter turn, as in animate_move().
        """

        for move in parse_moves(moves):
            self.animate_move(move, run_time=run_time)
