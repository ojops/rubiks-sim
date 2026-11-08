"""Render a verified ManimGL cube film and a GitHub compatible preview."""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from demo_style import (
    AMBER,
    BG,
    BLUE,
    FPS,
    GRID,
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

DURATION = 32
CHAPTERS = [
    (0, "Exact moves"),
    (8, "Bounded search"),
    (14, "Solution playback"),
    (24, "Independent verification"),
]


def annotations(t, report, cube_image):
    section = 0 if t < 8 else 1 if t < 14 else 2 if t < 24 else 3
    titles = [
        "Every turn has an exact state.",
        "A shallow scramble. A real search.",
        "The computed solution, in motion.",
        "Solved. Checked in two models.",
    ]
    image, draw = base(
        "rubiks-sim",
        1,
        titles[section],
        "Integer sticker geometry  /  compact cubie search  /  ManimGL playback",
        CHAPTERS,
        t,
        DURATION,
        BLUE,
        "Shallow scramble demonstration. Playback is slowed, search time is a recorded measurement.",
    )
    image.paste(cube_image, (80, 225))
    label(
        draw,
        110,
        255,
        ["Scramble", "Scrambled state", "Applying solution", "Verified solved state"][
            section
        ],
        BLUE,
    )
    panel(draw, (1150, 250, 1840, 917))
    x = 1190
    if section == 0:
        label(draw, x, 290, "Reproducible input")
        text(draw, (x, 345), "R   U   F2   L", 46, BLUE, mono=True, bold=True)
        text(draw, (x, 430), "4 moves · half-turn metric", 27, MUTED)
        metric(draw, x, 510, "54", "stickers with integer coordinates", BLUE)
        text(draw, (x, 660), "Quarter turns: exact 90° matrices", 25)
        text(draw, (x, 705), "F2: one move, a 180° rotation", 25)
        text(draw, (x, 805), "Each animation ends at the model state.", 23, MUTED)
        starts = [(2, 3, "R"), (3, 4, "U"), (4, 6, "F2"), (6, 7, "L")]
    elif section == 1:
        result = report["search"]
        label(draw, x, 290, "Recorded IDA* result")
        metric(
            draw,
            x,
            350,
            str(result["nodes"]),
            "visited nodes, including bound cutoffs",
            BLUE,
        )
        metric(draw, x, 495, str(result["bound"]), "final search bound", TEAL)
        metric(
            draw,
            x + 260,
            495,
            f"{result['elapsed_seconds'] * 1000:.1f} ms",
            "this machine / run",
            TEAL,
            size=42,
        )
        text(draw, (x, 650), "Depth budget 6 · node budget 100,000", 24)
        text(draw, (x, 710), "Heuristic: a lower bound on moves left", 24, MUTED)
        text(draw, (x, 780), "Current capability: shallow scrambles.", 24, AMBER)
        text(draw, (x, 824), "Fast arbitrary-state solving is future work.", 23, MUTED)
        starts = []
    elif section == 2:
        label(draw, x, 290, "Returned by solver.solve")
        solution = report["search"]["solution"]
        text(draw, (x, 350), "  ".join(solution), 44, TEAL, mono=True, bold=True)
        metric(draw, x, 455, str(len(solution)), "solution moves", TEAL)
        text(draw, (x, 620), "The renderer executes this result.", 28)
        text(draw, (x, 680), "Sticker identities stay attached to cubies.", 24, MUTED)
        text(draw, (x, 725), "Geometry snaps to exact coordinates", 24, MUTED)
        text(draw, (x, 764), "after each completed turn.", 24, MUTED)
        starts = []
        at = 14.0
        for move in solution:
            end = at + 1.4 * (2 if move.endswith("2") else 1)
            starts.append((at, end, move))
            at = end
    else:
        label(draw, x, 290, "Verification passed", TEAL)
        text(draw, (x, 350), "SOLVED", 64, TEAL, bold=True)
        for i, caption in enumerate(
            [
                "Sticker model: every face has its colour",
                "Cubie model: solved permutation / orientation",
                "54 rendered sticker centres checked",
                "Rendered sticker planes match model normals",
            ]
        ):
            text(draw, (x, 485 + i * 77), "✓", 28, TEAL)
            text(draw, (x + 38, 488 + i * 77), caption, 22)
        text(draw, (x, 835), "Reproduce: scripts/render_demo.py", 23, MUTED, mono=True)
        starts = []
    current = next((move for start, end, move in starts if start <= t < end), None)
    if current:
        text(
            draw,
            (970, 280),
            current,
            48,
            BLUE if section == 0 else TEAL,
            mono=True,
            bold=True,
            anchor="rt",
        )
    draw.line((110, 886, 1070, 886), fill=GRID, width=1)
    text(
        draw,
        (110, 905),
        "RubiksCube.move → AnimatedRubiksCube.animate_move",
        22,
        MUTED,
        mono=True,
    )
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/media"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = build_demo()
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
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
        with subprocess.Popen(command, stdout=subprocess.PIPE) as reader:

            def frame(t):
                pixels = reader.stdout.read(1040 * 720 * 3)
                if len(pixels) != 1040 * 720 * 3:
                    raise RuntimeError("Cube clip ended before the annotated timeline")
                return annotations(
                    t, report, Image.frombytes("RGB", (1040, 720), pixels)
                )

            encode(frame, args.output_dir / "demo.mp4", DURATION)
            reader.stdout.close()
            if reader.wait() != 0:
                raise RuntimeError("Cube clip decoding failed")
    preview(args.output_dir / "demo.mp4", args.output_dir / "preview.gif", 0, 8)


if __name__ == "__main__":
    main()
