# Reproducing the portfolio demonstration

`media/demo.mp4` is a 32-second silent film, 1920 × 1080 at 30 FPS,
encoded as H.264/yuv420p with fast-start metadata. `media/preview.gif` loops the opening eight seconds at 768 × 432 and 10 FPS.
The linked MP4 contains the complete film.

Both media files are tracked in Git. The animation uses a relative link;
the MP4 link uses a raw GitHub URL pinned to its media commit to avoid
branch-dependent redirects. When regenerating and committing a new MP4,
update the pinned README links to that commit. The link opens or downloads
the MP4 depending on the browser; the README animation itself has no
play/pause controls. No external hosting service is required.

From the repository root, with Python 3.10 and uv:

```bash
uv sync --locked --extra demo --extra render
uv run --locked --extra demo --extra render python scripts/render_demo.py
```

Install FFmpeg (with libx264), DejaVu Sans/Mono (`fonts-dejavu-core` on Ubuntu),
and the ManimGL system dependencies described in the README. The film was
successfully rendered with the pinned ManimGL revision using a surfaceless
graphics backend, without Xvfb. On a machine that requires a display, run the
generation command under `xvfb-run -a` after installing Xvfb and xauth. Pillow
12.3.0 is the only new optional dependency; the existing `render` extra supplies
ManimGL, NumPy/SciPy and its other graphics dependencies. Core installations do
not install the demo extra.

Use `--output-dir /path/to/output` to render elsewhere. Intermediate ManimGL
video, configuration and writable caches are created in a temporary directory
and removed automatically. Only the full MP4, short preview GIF and JSON
recording are tracked. The script sets local cache locations for ManimGL and
Matplotlib; it does not need a writable home directory.

## What actually runs

1. `rubiks_sim.demo_data.build_demo()` applies `R U F2 L` through
   `RubiksCube.apply_singmaster`, converts to `CubieState`, and calls `solve`
   with depth 6, 100,000 nodes and no wall-clock cutoff.
2. The solver returns `L' F2 U' R'`, visiting 551 nodes at bound 4 on the
   recorded source. Both sticker and cubie representations verify the result.
3. `scripts/cube_scene.py` subclasses the existing `AnimatedRubiksCube`, reusing
   its cube construction and `animate_move` implementation. The new
   `build_cube` method only extracts the existing construction for reuse; the
   original scene and CLI keep their behaviour.
4. At all nine state boundaries (initial, four scramble, four solution), the
   scene checks exact model arrays and all 54 rendered sticker centres and
   planes. A failed check aborts rendering.
5. The cube is rendered at twice its presentation resolution and downsampled
   with Lanczos filtering for smoother edges. Pillow composes the typography
   and recorded statistics over that actual ManimGL output. FFmpeg encodes the
   finished film and the preview.

`media/demo-data.json` contains the search result, limits and every sticker
state. The reported elapsed time is measured during that run; it is not the
length of the search chapter. Playback is deliberately slowed. Timings and
encoded bytes can vary by machine; the moves, search counts and verified state
sequence are deterministic. The solver's weak heuristic is suitable for shallow
scrambles; the film makes no arbitrary-state speed claim.

| Time | Demonstration |
| --- | --- |
| 0–8 s | Exact scramble with the current turn labelled |
| 8–14 s | Recorded IDA* result and explicit search limits |
| 14–24 s | Execute the returned solution |
| 24–32 s | Verified solved cube with a changing camera angle |

## Validation

```bash
uv run --locked --extra demo --extra render pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
ffmpeg -v error -i docs/media/demo.mp4 -f null -
ffmpeg -v error -i docs/media/preview.gif -f null -
ffprobe -v error -show_streams -show_format docs/media/demo.mp4
```

The completed run passed 108 tests, including the optional rendering-boundary
tests, Ruff lint and formatting. If home is read-only, set `XDG_CACHE_HOME` and
`MPLCONFIGDIR` to writable temporary locations before running the render tests.
The new recording tests replay every boundary and compare the solver report
with the CLI. Representative encoded frames were inspected for geometry,
clipping, notation and legibility, including turns in progress and the final
state. The original scene was also smoke-rendered after the extraction.

The README animation is an eight-second loop of the opening scramble. The linked MP4 provides
the full-resolution version. Rendered media is committed intentionally; do not
commit scratch frames or temporary graphics caches.
