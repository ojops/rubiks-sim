"""Render a seeded ManimGL solve and the recorded multi-seed comparison."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from statistics import median

from demo_style import (
    AMBER,
    BG,
    BLUE,
    FPS,
    GRID,
    INK,
    MUTED,
    TEAL,
    base,
    encode,
    label,
    metric,
    panel,
    preview,
    save_data,
    text,
)
from PIL import Image

from rubiks_sim.demo_data import build_demo

CHAPTERS = [
    (0, "Scramble"),
    (10, "Search"),
    (21, "Replay"),
    (32, "Verify"),
    (40, "Benchmark"),
    (52, "Read the result"),
]
DURATION = 65


def recording(root):
    report = build_demo()
    turns = []
    for start, sequence, quarter in [
        (1, report["scramble"], 1),
        (CHAPTERS[2][0], report["search"]["solution"], 1.4),
    ]:
        at = start
        for move in sequence:
            end = round(at + quarter * (2 if move.endswith("2") else 1), 3)
            turns.append(dict(move=move, start=at, end=end, quarter_seconds=quarter))
            at = end
    report["playback"] = {
        "turns": turns,
        "orbit_start": CHAPTERS[3][0],
        "end": CHAPTERS[4][0],
    }
    path = root / "benchmarks/results/multi-seed.json"
    raw = path.read_bytes()
    suite = json.loads(raw)
    sample = [r for r in suite["records"] if r["scramble"] == report["scramble"]]
    counts = {}
    for name in ("basic", "pattern"):
        records = [r for r in sample if r["heuristic_name"] == name]
        if len(records) != suite["configuration"]["repeats"] or not all(
            r["verified"] for r in records
        ):
            raise ValueError(
                "The filmed comparison needs a verified pair from the saved suite."
            )
        counts[name] = median(r["nodes"] for r in records)
    report["benchmark"] = {
        "source": str(path.relative_to(root)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "configuration": suite["configuration"],
        "summary": suite["summary"],
        "example_nodes": counts,
    }
    return report


def benchmark_frame(draw, report, section):
    bench = report["benchmark"]
    summary = bench["summary"]
    config = bench["configuration"]
    panel(draw, (80, 250, 1140, 917))
    panel(draw, (1180, 250, 1840, 917))
    if section == 4:
        label(draw, 125, 295, "Cases solved in every repetition")
        for y, name, colour in [(400, "basic", BLUE), (575, "pattern", TEAL)]:
            total = summary[name]["cases"]
            solved = summary[name]["cases_solved_every_repeat"]
            text(draw, (125, y), name.title(), 35, colour, bold=True)
            text(
                draw, (1090, y), f"{solved} / {total}", 38, INK, mono=True, anchor="rt"
            )
            for i in range(total):
                left = 125 + i * 38
                draw.rounded_rectangle(
                    (left, y + 62, left + 31, y + 106),
                    radius=5,
                    fill=colour if i < solved else GRID,
                )
        text(draw, (125, 794), "Each block is one scramble.", 29)
        text(
            draw,
            (125, 849),
            "Dim blocks reached a search limit in the recorded suite.",
            25,
            MUTED,
        )
        label(draw, 1220, 295, "Published warm-search budgets", AMBER)
        metric(draw, 1220, 365, f"{config['max_nodes']:,}", "nodes per search", AMBER)
        metric(
            draw,
            1220,
            512,
            f"{config['time_limit']:g} seconds",
            "per search after table setup",
            AMBER,
            size=45,
        )
        text(draw, (1220, 665), f"Maximum depth {config['max_depth']} face turns", 28)
        text(
            draw,
            (1220, 732),
            f"{len(config['lengths'])} lengths × {len(config['seeds'])} seeds",
            28,
        )
        text(
            draw,
            (1220, 795),
            f"{config['repeats']} runs per heuristic and case",
            26,
            MUTED,
        )
    else:
        label(draw, 125, 295, "Visited nodes · the filmed six-move scramble")
        for i, (name, colour) in enumerate([("basic", BLUE), ("pattern", TEAL)]):
            y = 386 + i * 145
            metric(
                draw,
                125,
                y,
                f"{bench['example_nodes'][name]:,.0f}",
                f"nodes with the {name} bound",
                colour,
                size=53,
            )
        ratios = summary["paired_node_ratio"]
        text(draw, (125, 720), f"Across the {ratios['count']} cases both solved,", 33)
        text(
            draw,
            (125, 784),
            f"the median basic/pattern node ratio was {ratios['median']:.2f}×.",
            31,
            TEAL,
        )
        text(
            draw,
            (125, 852),
            "Timing also depends on setup, hardware, and load.",
            24,
            MUTED,
        )
        label(draw, 1220, 295, "Try the same case")
        text(draw, (1220, 383), "uv run rubiks-sim", 33, INK, mono=True)
        text(draw, (1220, 449), "  --length 6 --seed 0", 32, BLUE, mono=True)
        text(draw, (1220, 513), "  --solve --max-depth 6", 32, BLUE, mono=True)
        text(draw, (1220, 626), "Run the command on one line.", 25, MUTED)
        text(draw, (1220, 717), "Read the full comparison in", 29)
        text(draw, (1220, 782), "benchmarks/results/multi-seed.md", 24, TEAL, mono=True)


def annotations(t, report, cube_image=None):
    section = max(i for i, (start, _) in enumerate(CHAPTERS) if t >= start)
    titles = [
        "Scramble a cube you can reproduce.",
        "Search for the fewest face turns.",
        "Play the moves the solver found.",
        "Check that every sticker comes home.",
        "How often did each search finish?",
        "How much search did this case take?",
    ]
    notes = [
        "A prime (′) turns a face anticlockwise as you look at it. A 2 marks a half turn.",
        "IDA* raises the move bound when a search finishes without a solution.",
        "Playback is slowed so you can follow each turn.",
        "The renderer checks all 54 sticker centres and face planes after each move.",
        "The suite records cold table setup separately. Each case uses an isolated process.",
        "Only jointly solved cases enter the node ratio. The report also retains every unfinished search.",
    ]
    image, draw = base(
        "rubiks-sim",
        1,
        titles[section],
        "Seeded moves  /  bounded IDA* search  /  independent sticker verification",
        CHAPTERS,
        t,
        DURATION,
        BLUE,
        notes[section],
    )
    if section >= 4:
        benchmark_frame(draw, report, section)
        return image
    image.paste(cube_image, (80, 225))
    label(
        draw,
        110,
        255,
        ["Scramble", "Scrambled state", "Applying solution", "Verified cube"][section],
        BLUE,
    )
    panel(draw, (1150, 250, 1840, 917))
    x = 1190
    result = report["search"]
    if section == 0:
        label(
            draw,
            x,
            290,
            f"Seed {report['seed']} · {len(report['scramble'])} generated moves",
        )
        text(
            draw,
            (x, 359),
            "  ".join(report["scramble"]),
            42,
            BLUE,
            mono=True,
            bold=True,
        )
        text(draw, (x, 464), "B = back    U = up    L = left    R = right", 24)
        metric(draw, x, 558, "54", "stickers with exact positions and colours", BLUE)
        text(draw, (x, 755), "The same length and seed produce", 28, MUTED)
        text(draw, (x, 799), "the same scramble.", 28, MUTED)
    elif section == 1:
        label(draw, x, 290, f"Default heuristic · {result['heuristic_name']}")
        metric(draw, x, 360, f"{result['nodes']:,}", "search nodes visited", BLUE)
        metric(
            draw,
            x,
            512,
            str(result["bound"]),
            "face turns at the successful bound",
            TEAL,
            size=47,
        )
        text(draw, (x, 670), "The compact model tracks corners and edges.", 24)
        text(draw, (x, 736), "Distance tables give a lower bound on moves", 24, MUTED)
        text(draw, (x, 778), "left. Branches above the bound are skipped.", 24, MUTED)
        text(draw, (x, 848), "Film budget  ·  depth 6  /  100,000 nodes", 24, AMBER)
    elif section == 2:
        label(draw, x, 290, "Solver output")
        text(
            draw,
            (x, 360),
            "  ".join(result["solution"]),
            42,
            TEAL,
            mono=True,
            bold=True,
        )
        metric(
            draw,
            x,
            510,
            str(len(result["solution"])),
            "face turns to solve this state",
            TEAL,
        )
        text(draw, (x, 697), "The animation applies the returned moves", 27)
        text(draw, (x, 746), "in order to the scrambled sticker model.", 27)
        text(draw, (x, 839), "One quarter turn or half turn costs one move.", 23, MUTED)
    else:
        label(draw, x, 290, "Independent checks", TEAL)
        text(draw, (x, 365), "Solved", 66, TEAL, bold=True)
        for i, caption in enumerate(
            [
                "Every sticker matches its face colour.",
                "Every corner and edge is home and oriented.",
                "Rendered stickers match the exact geometry.",
            ]
        ):
            text(draw, (x, 527 + i * 85), "✓", 28, TEAL)
            text(draw, (x + 38, 528 + i * 85), caption, 24)
        text(draw, (x, 839), "CLI result", 24, MUTED)
        text(draw, (x + 155, 834), '"verified": true', 30, TEAL, mono=True)
    current = next(
        (
            turn["move"]
            for turn in report["playback"]["turns"]
            if turn["start"] <= t < turn["end"]
        ),
        None,
    )
    if current:
        text(
            draw,
            (990, 280),
            current,
            48,
            TEAL if section == 2 else BLUE,
            mono=True,
            bold=True,
            anchor="rt",
        )
    draw.line((110, 886, 1070, 886), fill=GRID)
    text(draw, (110, 905), "ManimGL playback of the sticker model", 23, MUTED)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/media"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = recording(Path(__file__).resolve().parents[1])
    report_path = args.output_dir / "demo-data.json"
    save_data(report_path, report)
    with tempfile.TemporaryDirectory(prefix="rubiks-film-") as temporary:
        work = Path(temporary)
        config = work / "config.yml"
        config.write_text(f'camera:\n  background_color: "{BG}"\n')
        environment = dict(
            os.environ,
            RUBIKS_DEMO_DATA=str(report_path.resolve()),
            MPLCONFIGDIR=str(work / "matplotlib"),
            XDG_CACHE_HOME=str(work / "cache"),
            XDG_RUNTIME_DIR=str(work),
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "manimlib",
                str(Path(__file__).with_name("cube_scene.py")),
                "PortfolioCube",
                "-w",
                "-r",
                "2080x1440",
                "--fps",
                str(FPS),
                "--video_dir",
                str(work),
                "--config_file",
                str(config),
            ],
            check=True,
            env=environment,
        )
        command = [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(work / "PortfolioCube.mp4"),
            "-vf",
            "scale=1040:720:flags=lanczos",
            "-frames:v",
            str(report["playback"]["end"] * FPS),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
        with subprocess.Popen(command, stdout=subprocess.PIPE) as reader:

            def frame(t):
                if t >= report["playback"]["end"]:
                    return annotations(t, report)
                pixels = reader.stdout.read(1040 * 720 * 3)
                if len(pixels) != 1040 * 720 * 3:
                    raise RuntimeError("Cube clip ended before the annotated timeline")
                return annotations(
                    t, report, Image.frombytes("RGB", (1040, 720), pixels)
                )

            encode(frame, args.output_dir / "demo.mp4", DURATION, CHAPTERS)
            reader.stdout.close()
            if reader.wait() != 0:
                raise RuntimeError("Cube clip decoding failed")
    preview(args.output_dir / "demo.mp4", args.output_dir / "preview.gif", 0, 8)


if __name__ == "__main__":
    main()
