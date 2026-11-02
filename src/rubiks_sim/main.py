"""Reproducible scramble, bounded solve and optional rendering workflow."""

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from rubiks_sim.cube import RubiksCube
from rubiks_sim.cubie import CubieState
from rubiks_sim.notation import parse_moves
from rubiks_sim.scramble import generate_scramble
from rubiks_sim.solver import solve


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return 0 on success or 1 when search reaches a limit.

    Read arguments from sys.argv when argv is None. Invalid arguments and
    handled setup/rendering errors raise SystemExit with code 2 via argparse.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--scramble", default="", help="Space-separated face turns")
    source.add_argument("--length", type=int, help="Generate this many random moves")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--max-nodes", type=int, default=100_000)
    parser.add_argument("--time-limit", type=float, default=5.0)
    parser.add_argument("--render", action="store_true")
    parser.add_argument(
        "--low-quality", action="store_true", help="Render at Manim's low resolution"
    )
    parser.add_argument("--output-dir", type=Path, default=Path("videos"))
    args = parser.parse_args(argv)
    try:
        moves = (
            generate_scramble(args.length, args.seed)
            if args.length is not None
            else parse_moves(args.scramble)
        )
        cube = RubiksCube()
        cube.apply_singmaster(moves)
        report = {"scramble": moves}
        playback = moves.copy()
        exit_code = 0
        if args.solve:
            result = solve(
                CubieState.from_cube(cube),
                args.max_depth,
                max_nodes=args.max_nodes,
                time_limit=args.time_limit,
            )
            report["search"] = asdict(result)
            if result.solution is not None:
                cube.apply_singmaster(result.solution)
                if not cube.is_solved():
                    raise RuntimeError(
                        "Solution failed independent sticker-model verification"
                    )
                report["verified"] = True
                playback.extend(result.solution)
            else:
                exit_code = 1
        print(json.dumps(report, indent=2))
        if args.render and exit_code == 0:
            render(playback, args.output_dir, low_quality=args.low_quality)
        return exit_code
    except (ValueError, TypeError, OSError, subprocess.CalledProcessError) as error:
        parser.error(str(error))


def render(moves: list[str], output_dir: Path, *, low_quality: bool = False) -> None:
    """Render validated moves to output_dir using a separate ManimGL process.

    Use Xvfb on Linux without a display. Missing setup raises ValueError;
    process launch or rendering failures propagate as subprocess/OS errors.
    """
    if importlib.util.find_spec("manimlib") is None:
        raise ValueError("Rendering requires: uv sync --extra render")
    with tempfile.TemporaryDirectory(prefix="rubiks-scene-") as directory:
        scene = Path(directory) / "scene.py"
        scene.write_text(
            "from rubiks_sim.sim import AnimatedRubiksCube\n"
            f"class UserCube(AnimatedRubiksCube):\n    moves = {moves!r}\n",
            encoding="utf-8",
        )
        command = [
            sys.executable,
            "-m",
            "manimlib",
            str(scene),
            "UserCube",
            "-w",
            "--video_dir",
            str(output_dir.resolve()),
        ]
        if low_quality:
            command.append("-l")
        if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
            if shutil.which("xvfb-run") is None:
                raise ValueError("Headless rendering requires xvfb-run and xauth")
            command = ["xvfb-run", "-a", *command]
        subprocess.run(command, check=True)


if __name__ == "__main__":
    raise SystemExit(main())
