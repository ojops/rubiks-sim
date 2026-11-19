# Portfolio video: reproduction and verification

The eight-second README preview animates the six-move, seed-0 scramble from the published benchmark. The 1 minute 5 second silent MP4 follows the search, replays its answer, and places this one case in the full 25-case comparison. The MP4 includes chapter markers. The table below is a text companion.

## Generate

From the repository root, use Python 3.10 and uv.

```bash
uv sync --locked --extra render --extra demo
uv run --locked --extra render --extra demo python scripts/render_demo.py
```

Install FFmpeg with H.264 support, DejaVu fonts, and the ManimGL system dependencies. On headless Linux, prefix the rendering command with `xvfb-run -a` and install Xvfb, xauth, and Mesa’s software graphics drivers. Use `--output-dir /path/to/output` for another destination. The renderer cleans up temporary ManimGL footage and caches. [Installation](../README.md#requirements-and-installation)

## What the film demonstrates

| Time | Follow the example |
| --- | --- |
| 0:00–0:10 | **Scramble.** Length 6 and seed 0 produce `B' U' L' B' R' L`. A letter names a face. A prime turns it anticlockwise as you look at it. Each quarter turn or half turn costs one move. |
| 0:10–0:21 | **Search.** The default `pattern` heuristic uses coordinate distances to bound the moves left. IDA* visits 1,777 nodes, counting bound cutoffs, and finds a solution at depth 6. |
| 0:21–0:32 | **Replay.** ManimGL applies the returned sequence `R L' B L U B` to the scrambled cube. |
| 0:32–0:40 | **Verify.** The sticker and cubie models both reach their solved state. The rendering checks all 54 sticker centres and face planes at the initial state and after each of the twelve turns. |
| 0:40–0:52 | **Benchmark.** Across five lengths and five seeds, `basic` solves 11/25 cases in both repeats and `pattern` solves 15/25. Each warm search has a depth-10, 100,000-node, two-second budget. The suite records cold setup separately. |
| 0:52–1:05 | **Read the result.** The filmed case takes 81,213 nodes with `basic` and 1,777 with `pattern`. Across the 11 jointly solved cases, the median basic/pattern node ratio is 4.77×. Wall-clock time also depends on table setup, hardware, and load. |

Reproduce just the filmed search without installing graphics packages.

```bash
uv run rubiks-sim --length 6 --seed 0 --solve --max-depth 6
```

Look for `search.solution`, `search.nodes`, and `"verified": true` in the JSON. Add `--heuristic basic` to try the same scramble with the original lower bound. The normal CLI includes table setup in its wall-clock limit. Add `--time-limit 60` if a cold run on your machine needs longer.

`rubiks_sim.demo_data.build_demo()` runs the default solver with depth 6, 100,000 nodes, and no wall-clock cutoff. It independently verifies the returned moves and records every sticker state. The ManimGL scene uses the project’s `AnimatedRubiksCube.animate_move` and checks the rendered geometry at every boundary. The final two chapters read the published benchmark JSON. The recording stores its checksum, configuration, and counts alongside the newly filmed solve. [Full benchmark](../benchmarks/results/multi-seed.md) · [Algorithms](ALGORITHMS.md)

## Check the outputs

```bash
uv run --locked --extra render --extra demo pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
ffprobe -v error -show_chapters docs/media/demo.mp4
ffmpeg -v error -i docs/media/demo.mp4 -f null -
ffmpeg -v error -i docs/media/preview.gif -f null -
```

The MP4 is 1920 × 1080 at 30 fps. The looping GIF is 768 × 432 at 10 fps. When replacing the media, commit the MP4, GIF, and JSON together. Pin both README video links to that media commit. Encoded bytes and measured search times can vary between machines.
