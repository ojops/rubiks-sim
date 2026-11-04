# Cube models and solving

## Representations

`RubiksCube` (`cube.py`) stores 54 stickers with integer positions, outward normals, and colours. Face turns rotate one layer using integer matrices, avoiding floating point drift. Animation follows this model.

`CubieState` (`cubie.py`) stores the positions and orientations of eight corners and twelve edges. Precomputed tables apply each of the 18 supported moves in one transformation.

Both models use U/D = ±Y, F/B = ±Z, and R/L = ±X, with white/yellow, green/blue, and red/orange face colours. Conversion checks sticker geometry and fixed centres. Cubie validation checks unique pieces, corner twists summing to 0 modulo 3, edge flips summing to 0 modulo 2, and matching permutation parity.

## Search

`solver.py` uses Iterative Deepening A* (IDA*): depth first search with an increasing bound on moves used plus estimated moves remaining. Half turns count as one move.

The estimate takes the maximum of four counts divided by four and rounded up: misplaced corners, misplaced edges, twisted corners, and flipped edges. One move affects at most four corners and four edges, making this a lower bound. Consecutive same face turns and duplicate orderings of commuting opposite face turns are skipped without losing shortest solutions.

## API and limits

- `ida_star(state, max_depth=10)` returns a solution list or `None`.
- `solve(state, max_depth=10, max_nodes=None, time_limit=None)` returns a `SearchResult` with the solution, status, visited nodes, elapsed seconds, and search bound.

Both preserve the input by searching a validated copy. Library node/time budgets default to unlimited (the CLI uses 100,000 nodes and five seconds). Nodes include bound cutoffs. Time is measured after copying and checked before each node.

Statuses are `solved`, `depth_limit`, `node_limit`, and `time_limit`. A limit does not mean unsolvability. The reported bound is a search threshold, not a proven distance on interruption. The CLI verifies solutions against the sticker model.

## Limitations

The heuristic never exceeds three, so deep searches remain expensive. Stronger coordinate based heuristics or a two phase solver are future work. The current solver is intended for shallow scrambles.
