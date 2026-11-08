# Portfolio video: reproduction and verification

The README embeds an **eight-second looping GIF** (`docs/media/preview.gif`) and links to the complete **32-second, silent 1080p MP4** (`docs/media/demo.mp4`). Both are generated from the project's actual cube model and solver, not hand-animated moves.

## Generate

From the repository root, with Python 3.10 and [uv](https://docs.astral.sh/uv/):

```bash
uv sync --locked --extra render --extra demo
uv run --locked --extra render --extra demo python scripts/render_demo.py
```

Install FFmpeg with H.264 encoding, DejaVu fonts, and the ManimGL system dependencies described in the [README](../README.md). On a headless machine that requires a display, install Xvfb/xauth and prefix the render command with `xvfb-run -a`. The rendering dependencies are optional for normal CLI use.

Use `--output-dir /path/to/output` to change the destination. Temporary ManimGL footage and caches are cleaned up automatically.

## What the film demonstrates

| Time | Content |
| --- | --- |
| 0–8 s | Animate the scramble `R U F2 L` using the real sticker model |
| 8–14 s | Show the bounded IDA* search result and limits |
| 14–24 s | Animate the solver's returned moves |
| 24–32 s | Verify the solved state and rotate the camera |

`rubiks_sim.demo_data.build_demo()` runs the existing solver (depth limit 6, 100,000-node limit, no time limit). The committed recording used the original cubie-count heuristic: it found `L' F2 U' R'` after 551 nodes at search bound 4. This change preserves the existing MP4/GIF/JSON snapshot. Regeneration now uses the default coordinate heuristic and records its actual statistics (55 nodes on the same scramble), replacing files in the chosen output directory. Reproduce the historical search with `uv run rubiks-sim --scramble "R U F2 L" --solve --heuristic basic`. The code verifies the result in both sticker and cubie representations.

`scripts/cube_scene.py` reuses `AnimatedRubiksCube` and checks the model arrays plus all 54 rendered sticker centres and planes at each of the nine move boundaries. A failed check stops rendering. `scripts/render_demo.py` combines the actual ManimGL footage with captions and search data using Pillow and FFmpeg.

`docs/media/demo-data.json` records the search and each sticker state. Search time depends on the machine; animation playback is intentionally slower. The current solver demonstrates **shallow-scramble solving**, not efficient arbitrary-state solving.

## Check the outputs

```bash
uv run --locked --extra render --extra demo pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
ffmpeg -v error -i docs/media/demo.mp4 -f null -
ffmpeg -v error -i docs/media/preview.gif -f null -
```

The full MP4 is encoded at 1920 × 1080/30 FPS; the preview is 768 × 432/10 FPS. Encoded bytes and measured timings can differ between systems.

**When updating the media:** commit the generated MP4, GIF and JSON together. The README's MP4 URLs are pinned to a media commit, so update those links when the MP4 changes. Do not commit temporary frames or caches.
