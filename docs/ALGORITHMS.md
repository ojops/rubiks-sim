# Cube models and search

This project uses a sticker model for geometry and a compact cubie model for solving. Both share the same face and colour conventions.

## Cube representations

- **`RubiksCube` (`cube.py`)** stores 54 stickers as integer positions, outward normals and colours. Face turns use integer rotation matrices, avoiding cumulative floating-point drift.
- **`CubieState` (`cubie.py`)** stores the permutations and orientations of eight corners and twelve edges. Precomputed transformations cover all 18 supported face moves.

The axes are U/D = ±Y, F/B = ±Z and R/L = ±X; opposite-face colours are white/yellow, green/blue and red/orange.

Conversion checks geometry and fixed-centre colours. Cubie validation requires unique pieces, corner twists summing to 0 modulo 3, edge flips summing to 0 modulo 2, and matching corner/edge permutation parity.

## Search algorithm

`solver.py` uses **iterative deepening A*** (IDA*): depth-first search with an increasing bound on moves taken plus estimated moves remaining. Quarter turns and half turns each cost one move.

The admissible heuristic is the maximum of four lower bounds:

```text
ceil(misplaced corners / 4)
ceil(misplaced edges / 4)
ceil(twisted corners / 4)
ceil(flipped edges / 4)
```

Each face move affects at most four corners and four edges. Taking the maximum, rather than the sum, avoids counting overlapping effects twice. Search also skips consecutive turns of the same face and redundant orderings of commuting opposite-face turns.

## Python API

- `ida_star(state, max_depth=10)` returns a list of moves, or `None` if no solution is found within the depth limit.
- `solve(state, max_depth=10, max_nodes=None, time_limit=None)` returns a `SearchResult` with the solution, status, visited nodes, elapsed seconds and search bound.

Both search a validated copy, preserving the caller's state. Library node and time budgets default to unlimited; CLI defaults are 100,000 nodes and five seconds. Node counts include bound cutoffs. Measured time excludes the initial state copy.

Statuses are `solved`, `depth_limit`, `node_limit` and `time_limit`. Reaching a limit **does not imply an unsolvable state**. The reported bound is the current search threshold, not necessarily a proven distance when interrupted. The CLI independently checks returned solutions against the sticker model.

## Limitations

The current heuristic is weak (at most three moves), so search becomes expensive on deeper scrambles. Stronger coordinate heuristics or a two-phase solver are future work.
