"""Optional rendering-boundary checks without creating a graphics context."""

import pytest

pytest.importorskip("manimlib")
from rubiks_sim.sim import AnimatedRubiksCube


def test_bad_animation_never_starts_playback():
    class Probe:
        def play(self, *args, **kwargs):
            pytest.fail("Invalid move reached playback")

    with pytest.raises(ValueError, match="Invalid move"):
        AnimatedRubiksCube.animate_move(Probe(), "R3")


def test_bad_sequence_never_starts_playback():
    class Probe:
        def animate_move(self, *args, **kwargs):
            pytest.fail("Invalid sequence reached playback")

    with pytest.raises(ValueError, match="Invalid move"):
        AnimatedRubiksCube.animate_moves(Probe(), ["R", "X"])
