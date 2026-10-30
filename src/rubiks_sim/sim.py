import numpy as np
from manimlib import *

from rubiks_sim.cube import RubiksCube


STICKER_COLOURS = {
    "W": WHITE,
    "Y": YELLOW,
    "G": GREEN,
    "B": BLUE,
    "R": RED,
    "O": ORANGE,
}

# Rotate each square so it faces the correct direction
FACE_ROTATIONS = {
    (0, 0, 1): (0, OUT),
    (0, 0, -1): (PI, RIGHT),
    (0, 1, 0): (-PI / 2, RIGHT),
    (0, -1, 0): (PI / 2, RIGHT),
    (1, 0, 0): (PI / 2, UP),
    (-1, 0, 0): (-PI / 2, UP),
}

CUBIE_SIZE = 0.96
STICKER_SIZE = 0.86
STICKER_OFFSET = CUBIE_SIZE / 2 + 0.01


def create_sticker(position, normal, colour):
    """Create a coloured square on one face of a cubie"""

    sticker = Square(
        side_length=STICKER_SIZE,
        stroke_color=BLACK,
        stroke_width=1.5,
    )

    sticker.set_fill(STICKER_COLOURS[str(colour)], opacity=1)

    normal_key = tuple(int(value) for value in normal)
    angle, axis = FACE_ROTATIONS[normal_key]

    sticker.rotate(angle, axis=axis)

    # Position the sticker just outside the cubie
    sticker.move_to(position + STICKER_OFFSET * normal)

    return sticker


class AnimatedRubiksCube(InteractiveScene):

    def construct(self):
        self.cube = RubiksCube()

        self.frame.reorient(
            theta_degrees=-45,
            phi_degrees=70,
        )

        self.cubies = []

        # Create all 27 cubies
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                for z in (-1, 0, 1):

                    position = np.array([x, y, z])

                    # Find all stickers belonging to this cubie
                    sticker_indices = np.flatnonzero(
                        np.all(self.cube.positions == position, axis=1)
                    )

                    # Create the black body of the cubie
                    body = Cube(side_length=CUBIE_SIZE)
                    body.set_color(BLACK)
                    body.set_opacity(1)
                    body.move_to(position)
                    body.apply_depth_test()

                    # Create its coloured stickers
                    stickers = []

                    for i in sticker_indices:
                        sticker = create_sticker(
                            position,
                            self.cube.normals[i],
                            self.cube.colours[i],
                        )

                        sticker.apply_depth_test()
                        stickers.append(sticker)

                    # Group the body and its stickers together
                    cubie_group = Group(body, *stickers)

                    self.cubies.append({
                        "position": position,
                        "indices": sticker_indices,
                        "body": body,
                        "stickers": stickers,
                        "group": cubie_group,
                    })

        # Add all 27 cubies to the scene
        self.add(*[
            cubie["group"]
            for cubie in self.cubies
        ])

        self.wait()

        # Demonstrate some moves
        self.animate_move("R")
        self.animate_move("U")
        self.animate_move("R'")
        self.animate_move("U'")

        self.wait()

    def animate_move(self, notation):
        """Animate a single move of the Rubik's Cube"""

        face = notation[0]
        axis, sign = self.cube.FACE_AXES[face]

        # Determine the number and direction of quarter turns
        if notation.endswith("'"):
            turns = -1
        elif notation.endswith("2"):
            turns = 2
        else:
            turns = 1

        quarter_turns = -sign * turns
        angle = quarter_turns * PI / 2

        # Select the nine cubies belonging to the relevant layer
        layer_cubies = []

        for cubie in self.cubies:

            # The central core has no stickers and never moves
            if len(cubie["indices"]) == 0:
                continue

            # All stickers on a cubie share the same position
            sticker_index = cubie["indices"][0]
            position = self.cube.positions[sticker_index]

            if position[axis] == sign:
                layer_cubies.append(cubie["group"])

        layer = Group(*layer_cubies)

        # Convert the axis index into an x, y or z vector
        rotation_axis = np.eye(3)[axis]

        # Animate the nine cubies together
        self.play(
            Rotate(
                layer,
                angle=angle,
                axis=rotation_axis,
                about_point=ORIGIN,
            ),
            run_time=0.6,
        )

        # Update the mathematical cube
        self.cube.move(notation)

        # Synchronise the visual cubies with the mathematical model
        for cubie in self.cubies:

            indices = cubie["indices"]

            if len(indices) == 0:
                continue

            # All stickers belonging to this cubie have the same
            # updated position, so we only need the first one
            new_position = self.cube.positions[indices[0]].astype(float)

            # Move the cubie's black body to its new position
            cubie["body"].move_to(new_position)

            # Reposition and reorient each coloured sticker
            for sticker, i in zip(cubie["stickers"], indices):

                updated_sticker = create_sticker(
                    new_position,
                    self.cube.normals[i],
                    self.cube.colours[i],
                )

                sticker.become(updated_sticker)
                sticker.apply_depth_test()