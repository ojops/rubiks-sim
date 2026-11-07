"""Check that the film's recorded state sequence is a verified solver execution."""

import json

import numpy as np

from rubiks_sim.cube import RubiksCube
from rubiks_sim.cubie import CubieState
from rubiks_sim.demo_data import SCRAMBLE, build_demo
from rubiks_sim.main import main


def test_recorded_playback_matches_each_exact_move():
    report = build_demo()
    cube = RubiksCube()
    assert len(report["states"]) == 1 + len(report["scramble"]) + len(
        report["search"]["solution"]
    )
    for state in report["states"]:
        if state["move"] is not None:
            cube.move(state["move"])
        np.testing.assert_array_equal(cube.positions, state["positions"])
        np.testing.assert_array_equal(cube.normals, state["normals"])
        assert cube.is_solved() == state["solved"]
        CubieState.from_cube(cube).validate()
    assert report["verified"] and cube.is_solved()


def test_recorded_search_agrees_with_cli(capsys):
    report = build_demo()
    assert main(["--scramble", SCRAMBLE, "--solve", "--max-depth", "6"]) == 0
    cli = json.loads(capsys.readouterr().out)
    for key in ("status", "nodes", "bound"):
        assert report["search"][key] == cli["search"][key]
    assert list(report["search"]["solution"]) == cli["search"]["solution"]
