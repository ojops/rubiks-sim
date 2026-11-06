"""Render the project's existing cube geometry and move animation, with checks."""

import json
import os
from pathlib import Path

import numpy as np
from manimlib import UpdateFromAlphaFunc, smooth
from scipy.spatial.transform import Rotation

from rubiks_sim.sim import AnimatedRubiksCube


def orientation(angle):
    view = np.array([6 * np.sin(angle), 3.8, 6 * np.cos(angle)])
    view /= np.linalg.norm(view)
    right = np.cross([0, 1, 0], view)
    right /= np.linalg.norm(right)
    up = np.cross(view, right)
    return Rotation.from_matrix(np.column_stack([right, up, view]))


class PortfolioCube(AnimatedRubiksCube):
    """Play the recorded scramble and search solution over a 32-second timeline."""

    def check_geometry(self, expected: dict) -> None:
        """Check model boundaries and rendered sticker centres and face normals."""
        from rubiks_sim.sim import STICKER_OFFSET

        np.testing.assert_array_equal(self.cube.positions, expected["positions"])
        np.testing.assert_array_equal(self.cube.normals, expected["normals"])
        for cubie in self.cubies:
            for sticker, index in zip(cubie["stickers"], cubie["indices"]):
                centre = (
                    self.cube.positions[index]
                    + STICKER_OFFSET * self.cube.normals[index]
                )
                np.testing.assert_allclose(sticker.get_center(), centre, atol=1e-6)
                # A square's three-dimensional span must be in its model face plane.
                offsets = sticker.get_points() - centre
                np.testing.assert_allclose(
                    offsets @ self.cube.normals[index], 0, atol=1e-6
                )

    def construct(self) -> None:
        report = json.loads(Path(os.environ["RUBIKS_DEMO_DATA"]).read_text())
        self.build_cube()
        self.frame.set_shape(6.7 * 1040 / 720, 6.7)
        self.frame.set_orientation(orientation(np.pi / 4))
        self.check_geometry(report["states"][0])
        self.wait(2)
        boundary = 0
        for move in report["scramble"]:
            self.animate_move(move, run_time=1.0)
            boundary += 1
            self.check_geometry(report["states"][boundary])
        self.wait(7)
        for move in report["search"]["solution"]:
            self.animate_move(move, run_time=1.4)
            boundary += 1
            self.check_geometry(report["states"][boundary])
        if not self.cube.is_solved():
            raise RuntimeError("Rendered playback failed solution verification")
        self.wait(3)
        self.play(
            UpdateFromAlphaFunc(
                self.frame,
                lambda frame, alpha: frame.set_orientation(
                    orientation(np.pi / 4 + alpha * np.pi)
                ),
            ),
            run_time=8,
            rate_func=smooth,
        )
