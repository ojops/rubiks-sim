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

# Each rotation turns a square from its default XY plane
# so that it faces the required direction
FACE_ROTATIONS = {
    (0, 0, 1): (0, OUT),
    (0, 0, -1): (PI, RIGHT),
    (0, 1, 0): (-PI / 2, RIGHT),
    (0, -1, 0): (PI / 2, RIGHT),
    (1, 0, 0): (PI / 2, UP),
    (-1, 0, 0): (-PI / 2, UP),
}


def create_sticker(position, normal, colour):
    """Create one coloured square at a cube sticker's position"""
    sticker = Square(
        side_length=0.94,
        stroke_color=STICKER_COLOURS[str(colour)],
        stroke_width=1.5,
    )

    sticker.set_fill(STICKER_COLOURS[str(colour)], opacity=1)

    normal_key = tuple(int(value) for value in normal)
    angle, axis = FACE_ROTATIONS[normal_key]

    sticker.rotate(angle, axis=axis)

    # Position the sticker just outside the cube's surface
    sticker.move_to(
        position + (0.5 + (1 - 0.94) / 1.414) * normal
    )

    return sticker


class AnimatedRubiksCube(InteractiveScene):

    def construct(self):
        self.cube = RubiksCube()

        # Set the camera angle
        self.frame.reorient(
            theta_degrees=-45,
            phi_degrees=70,
        )

        # Create the black cube body
        self.body = Cube(side_length=3)
        self.body.set_color(BLACK)
        self.body.set_opacity(1)
        self.body.apply_depth_test()

        # Create the 54 stickers from the logical cube
        self.stickers = [
            create_sticker(position, normal, colour)
            for position, normal, colour in zip(
                self.cube.positions,
                self.cube.normals,
                self.cube.colours,
            )
        ]

        # Add depth testing so stickers on the rear faces
        # are hidden when they should be
        for sticker in self.stickers:
            sticker.apply_depth_test()

        self.add(self.body, *self.stickers)

        self.wait()

        # Demonstrated moves
        self.animate_move("R")
        self.animate_move("U")
        self.animate_move("R'")
        self.animate_move("U'")

        self.wait()

    def animate_move(self, notation):
        """Animate a single move and update the logical cube"""

        # Determine which face is being turned
        face = notation[0]
        axis, sign = self.cube.FACE_AXES[face]

        # Determine how many quarter turns are required
        if notation.endswith("'"):
            turns = 3
        elif notation.endswith("2"):
            turns = 2
        else:
            turns = 1

        # Calculate the direction and angle of rotation
        quarter_turns = -sign * turns
        angle = quarter_turns * PI / 2

        # Find all stickers on the layer being turned
        mask = self.cube.positions[:, axis] == sign

        layer = VGroup(*[
            sticker
            for sticker, selected in zip(self.stickers, mask)
            if selected
        ])

        # Convert the axis number (0, 1, 2) into an x, y or z vector
        rotation_axis = np.eye(3)[axis]

        # Animate the layer rotation
        self.play(
            Rotate(
                layer,
                angle=angle,
                axis=rotation_axis,
                about_point=ORIGIN,
            ),
            run_time=0.6,
        )

        # Update the logical cube to reflect the move
        self.cube.move(notation)

        # Snap the visual stickers to their exact new positions
        # to prevent small floating point errors accumulating
        for i, (sticker, position, normal) in enumerate(zip(
            self.stickers,
            self.cube.positions,
            self.cube.normals,
        )):
            updated_sticker = create_sticker(
                position,
                normal,
                self.cube.colours[i],
            )

            sticker.become(updated_sticker)
            sticker.apply_depth_test()