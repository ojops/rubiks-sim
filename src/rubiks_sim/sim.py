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
        #stroke_color=BLACK,
        stroke_color=STICKER_COLOURS[str(colour)],
        stroke_width=1.5,
    )

    sticker.set_fill(STICKER_COLOURS[str(colour)], opacity=1)

    normal_key = tuple(int(value) for value in normal)
    angle, axis = FACE_ROTATIONS[normal_key]

    sticker.rotate(angle, axis=axis)

    # Move the sticker just outside the cube's surface
    sticker.move_to(position + (0.5 + (1 - 0.94) / 1.414) * normal)

    return sticker


class StaticRubiksCube(InteractiveScene):
    def construct(self):
        cube = RubiksCube()

        # Give the camera a side on view of the cube
        self.frame.reorient(
            theta_degrees=-45,
            phi_degrees=70,
        )

        body = Cube(side_length=3)
        body.set_color(BLACK)
        body.set_opacity(1)
        #body.apply_depth_test()

        stickers = [
            create_sticker(position, normal, colour)
            for position, normal, colour in zip(
                cube.positions,
                cube.normals,
                cube.colours,
            )
        ]
        
        for sticker in stickers:
            sticker.apply_depth_test()

        #self.add(body)
        self.add(*stickers)
        self.wait()