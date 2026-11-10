"""Run a reproducible multi-seed comparison in isolated worker processes."""

import argparse
import hashlib
import json
import platform
import resource
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from rubiks_sim.cube import RubiksCube
from rubiks_sim.cubie import CubieState
from rubiks_sim.patterns import prepare_patterns
from rubiks_sim.scramble import generate_scramble
from rubiks_sim.solver import solve

ROOT = Path(__file__).resolve().parents[1]


def worker(args):
    length, seed, name = args.worker
    length, seed = int(length), int(seed)
    moves = generate_scramble(length, seed)
    cube = RubiksCube()
    cube.apply_singmaster(moves)
    state = CubieState.from_cube(cube)
    started = perf_counter()
    tables = prepare_patterns() if name == "pattern" else ()
    setup = perf_counter() - started
    records = []
    for repeat in range(args.repeats):
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
                raise RuntimeError("Independent sticker verification failed")
        # Linux reports KiB; macOS reports bytes. Includes interpreter, imports,
        # cold setup and previous repetitions: not incremental search memory.
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        records.append(
            {
                "length": length,
                "seed": seed,
                "scramble": moves,
                "repeat": repeat + 1,
                **asdict(result),
                "verified": verified,
                "solution_depth": len(result.solution) if verified else None,
                "cold_setup_seconds": setup,
                "distance_table_bytes": sum(map(len, tables)),
                "process_peak_rss_bytes": int(
                    rss * (1 if sys.platform == "darwin" else 1024)
                ),
            }
        )
    return records


def summarize(records):
    """Keep failures in coverage; ratios use only pairs solved in every repeat."""
    if not records:
        raise ValueError("Benchmark records must not be empty")
    cases = defaultdict(lambda: defaultdict(list))
    for row in records:
        if row["heuristic_name"] not in ("basic", "pattern"):
            raise ValueError("Unknown heuristic in benchmark records")
        cases[row["length"], row["seed"]][row["heuristic_name"]].append(row)
    for groups in cases.values():
        if set(groups) != {"basic", "pattern"}:
            raise ValueError("Every case requires both heuristics")
        repeats = [[r["repeat"] for r in groups[name]] for name in ("basic", "pattern")]
        if any(len(set(ids)) != len(ids) for ids in repeats) or set(repeats[0]) != set(
            repeats[1]
        ):
            raise ValueError("Every case requires matching, unique repetitions")
    summary = {}
    for name in ("basic", "pattern"):
        rows = [r for r in records if r["heuristic_name"] == name]
        solved = [r for r in rows if r["status"] == "solved"]
        summary[name] = {
            "cases": len(cases),
            "cases_solved_every_repeat": sum(
                all(r["status"] == "solved" for r in groups[name])
                for groups in cases.values()
            ),
            "attempts": len(rows),
            "statuses": dict(Counter(r["status"] for r in rows)),
            "median_seconds_all_attempts": statistics.median(
                r["elapsed_seconds"] for r in rows
            ),
            "median_seconds_solved": statistics.median(
                r["elapsed_seconds"] for r in solved
            )
            if solved
            else None,
            "max_process_peak_rss_bytes": max(
                r["process_peak_rss_bytes"] for r in rows
            ),
        }
    pairs = []
    for length, seed in sorted({(r["length"], r["seed"]) for r in records}):
        rows = [r for r in records if (r["length"], r["seed"]) == (length, seed)]
        if any(r["status"] != "solved" for r in rows):
            continue
        if len({r["solution_depth"] for r in rows}) != 1:
            raise ValueError("Solved heuristics disagree on optimal depth")
        medians = {
            name: {
                metric: statistics.median(
                    r[metric] for r in rows if r["heuristic_name"] == name
                )
                for metric in ("nodes", "elapsed_seconds")
            }
            for name in ("basic", "pattern")
        }
        pairs.append(
            {
                "length": length,
                "seed": seed,
                "node_ratio_basic_over_pattern": medians["basic"]["nodes"]
                / medians["pattern"]["nodes"],
                "warm_time_ratio_basic_over_pattern": medians["basic"][
                    "elapsed_seconds"
                ]
                / medians["pattern"]["elapsed_seconds"],
            }
        )
    summary["both_solved_cases"] = pairs
    ratios = [p["node_ratio_basic_over_pattern"] for p in pairs]
    summary["paired_node_ratio"] = {
        "count": len(ratios),
        "median": statistics.median(ratios) if ratios else None,
        "min": min(ratios) if ratios else None,
        "max": max(ratios) if ratios else None,
    }
    return summary


def markdown(report):
    lines = [
        "# Multi-seed solver benchmark",
        "",
        "Generated by `benchmarks/suite.py`; all attempted cases are retained.",
        "",
        "Basic = original misplaced/oriented-cubie lower bound. Pattern = basic plus exact coordinate-distance bounds.",
        "",
        "Each case/heuristic runs in a fresh process; repeated warm solves reuse its tables. Cold construction is recorded separately.",
        "",
        "| Length / seed | Basic statuses | Pattern statuses | Basic median nodes | Pattern median nodes | Basic / pattern warm seconds | Basic / pattern peak RSS MiB |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for length, seed in sorted({(r["length"], r["seed"]) for r in report["records"]}):
        groups = [
            [
                r
                for r in report["records"]
                if (r["length"], r["seed"], r["heuristic_name"]) == (length, seed, name)
            ]
            for name in ("basic", "pattern")
        ]
        statuses = [
            ", ".join(
                f"{k}: {v}" for k, v in Counter(r["status"] for r in rows).items()
            )
            for rows in groups
        ]
        nodes = [statistics.median(r["nodes"] for r in rows) for rows in groups]
        times = [
            statistics.median(r["elapsed_seconds"] for r in rows) for rows in groups
        ]
        memory = [
            max(r["process_peak_rss_bytes"] for r in rows) / 2**20 for rows in groups
        ]
        lines.append(
            f"| {length} / {seed} | {statuses[0]} | {statuses[1]} | {nodes[0]:,.0f} | {nodes[1]:,.0f} | {times[0]:.4f} / {times[1]:.4f} | {memory[0]:.1f} / {memory[1]:.1f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "| Heuristic | Cases solved in every repetition | Attempt outcomes |",
        "|---|---:|---|",
        *[
            f"| {name} | {item['cases_solved_every_repeat']}/{item['cases']} | {item['statuses']} |"
            for name, item in report["summary"].items()
            if name in ("basic", "pattern")
        ],
        "",
        f"Paired node ratios (basic / pattern): {report['summary']['paired_node_ratio']}. Full per-case ratios remain in the JSON report.",
        "",
        "Ratios exclude any case with a failed repetition: they describe the jointly solved subset, not overall speedup. Failures are censored by the declared budgets, not evidence of unsolvability. Runtime medians over all attempts mix successes and budget exhaustion.",
        "",
        "RSS is each isolated process's high-water memory including Python, NumPy, cold table construction and all repeats. It is not incremental search allocation. The 44,555 distance-table bytes are not total process memory. Repeated RSS samples within a process are not independent.",
        "",
        "Generated move count is not proven optimal depth; sequences are not uniformly sampled cube states. Every solution is independently replayed on the sticker model. Hardware, interpreter and load affect timings and time-limit outcomes. No new solving algorithm is introduced.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lengths", type=int, nargs="+", default=[4, 6, 8, 10, 20])
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(5)))
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--max-nodes", type=int, default=100_000)
    parser.add_argument("--time-limit", type=float, default=2.0)
    parser.add_argument(
        "--output", type=Path, default=Path("benchmarks/results/multi-seed.json")
    )
    parser.add_argument("--worker", nargs=3, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if (
        args.repeats < 1
        or args.max_nodes < 1
        or args.max_depth < 0
        or not 0 < args.time_limit < float("inf")
    ):
        parser.error(
            "repeats/nodes/time must be positive and finite; depth nonnegative"
        )
    if (
        any(n < 0 for n in args.lengths)
        or len(set(args.lengths)) != len(args.lengths)
        or len(set(args.seeds)) != len(args.seeds)
    ):
        parser.error("lengths must be nonnegative; lengths and seeds must be unique")
    if args.worker:
        print(json.dumps(worker(args)))
        return
    records = []
    for index, (length, seed) in enumerate(
        (n, s) for n in args.lengths for s in args.seeds
    ):
        names = ("basic", "pattern") if index % 2 == 0 else ("pattern", "basic")
        for name in names:
            command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                str(length),
                str(seed),
                name,
                "--repeats",
                str(args.repeats),
                "--max-depth",
                str(args.max_depth),
                "--max-nodes",
                str(args.max_nodes),
                "--time-limit",
                str(args.time_limit),
            ]
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            records.extend(json.loads(result.stdout))
        print(f"Completed length={length}, seed={seed}", file=sys.stderr, flush=True)
    sources = [Path(__file__), *sorted((ROOT / "src/rubiks_sim").glob("*.py"))]
    report = {
        "schema_version": 1,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "configuration": {
            k: v for k, v in vars(args).items() if k not in ("worker", "output")
        },
        "implementation_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sources
        },
        "records": records,
        "summary": summarize(records),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    args.output.with_suffix(".md").write_text(markdown(report))


if __name__ == "__main__":
    main()
