"""Record a bounded search and independently checked sticker states for the film."""

from dataclasses import asdict

from rubiks_sim.cube import RubiksCube
from rubiks_sim.cubie import CubieState
from rubiks_sim.notation import parse_moves
from rubiks_sim.solver import solve

SCRAMBLE = "R U F2 L"


def build_demo() -> dict:
    """Solve the fixed shallow scramble, retain every exact playback boundary."""
    cube = RubiksCube()
    scramble = parse_moves(SCRAMBLE)
    cube.apply_singmaster(scramble)
    result = solve(CubieState.from_cube(cube), max_depth=6, max_nodes=100_000)
    if result.solution is None:
        raise RuntimeError(f"Demonstration search stopped: {result.status}")
    cube.apply_singmaster(result.solution)
    if not cube.is_solved() or not CubieState.from_cube(cube).is_solved():
        raise RuntimeError("Independent solution verification failed.")

    playback = RubiksCube()
    states = []
    for move in [None, *scramble, *result.solution]:
        if move is not None:
            playback.move(move)
        states.append(
            {
                "move": move,
                "positions": playback.positions.tolist(),
                "normals": playback.normals.tolist(),
                "colours": playback.colours.tolist(),
                "solved": playback.is_solved(),
            }
        )
    return {
        "scramble": scramble,
        "search": asdict(result),
        "limits": {"max_depth": 6, "max_nodes": 100_000, "time_limit": None},
        "verified": True,
        "states": states,
        "note": "Shallow scramble, elapsed time is a machine dependent recorded run.",
    }
