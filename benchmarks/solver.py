"""Compare admissible heuristics on identical deterministic scrambles and budgets."""

import argparse
import json
import platform
from dataclasses import asdict
from time import perf_counter

from rubiks_sim.cube import RubiksCube
from rubiks_sim.cubie import CubieState
from rubiks_sim.patterns import prepare_patterns
from rubiks_sim.scramble import generate_scramble
from rubiks_sim.solver import solve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--max-nodes", type=int, default=100_000)
    parser.add_argument("--time-limit", type=float, default=5)
    parser.add_argument("--repeats", type=int, default=1)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    started = perf_counter()
    tables = prepare_patterns()
    print(
        json.dumps(
            {
                "phase": "cold_pattern_setup",
                "elapsed_seconds": perf_counter() - started,
                "distance_bytes": sum(map(len, tables)),
                "python": platform.python_version(),
                "platform": platform.platform(),
                "note": "Following solves reuse tables and normal CLI time limits include cold setup.",
            }
        )
    )
    for length, seed in (
        (4, 0),
        (5, 0),
        (6, 0),
        (7, 0),
        (8, 0),
        (8, 1),
        (8, 2),
        (10, 0),
        (10, 1),
        (20, 42),
    ):
        moves = generate_scramble(length, seed)
        cube = RubiksCube()
        cube.apply_singmaster(moves)
        state = CubieState.from_cube(cube)
        for repeat in range(args.repeats):
            # Alternate order to reduce systematic timing order effects
            names = ("basic", "pattern") if repeat % 2 == 0 else ("pattern", "basic")
            for name in names:
                result = solve(
                    state,
                    args.max_depth,
                    max_nodes=args.max_nodes,
                    time_limit=args.time_limit,
                    heuristic_name=name,
                )
                verified = None
                if result.solution is not None:
                    playback = RubiksCube()
                    playback.apply_singmaster([*moves, *result.solution])
                    verified = playback.is_solved()
                    if not verified:
                        raise RuntimeError(
                            "Benchmark solution failed sticker verification."
                        )
                print(
                    json.dumps(
                        {
                            "phase": "warm_search",
                            "scramble": moves,
                            "length": length,
                            "seed": seed,
                            "repeat": repeat + 1,
                            "limits": {
                                "max_depth": args.max_depth,
                                "max_nodes": args.max_nodes,
                                "time_limit": args.time_limit,
                            },
                            **asdict(result),
                            "solution_depth": len(result.solution)
                            if result.solution is not None
                            else None,
                            "verified": verified,
                        }
                    )
                )


if __name__ == "__main__":
    main()
