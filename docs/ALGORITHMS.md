# Cube models and search

This project uses a 54 sticker model for geometry and a compact cubie model for solving. Both share the same face and colour conventions.

## Cube representations

- **`RubiksCube` (`cube.py`)** stores 54 stickers as integer positions, outward normals, and colours. Face turns use integer rotation matrices, avoiding cumulative floating point drift.
- **`CubieState` (`cubie.py`)** stores the permutations and orientations of eight corners and twelve edges. Precomputed transformations cover all 18 supported face moves.

The axes are U/D = ±Y, F/B = ±Z, and R/L = ±X. Opposite face colours are white/yellow, green/blue, and red/orange.

Conversion checks geometry and fixed centre colours. Cubie validation requires unique pieces, corner twists summing to 0 modulo 3, edge flips summing to 0 modulo 2, and matching corner/edge permutation parity.

## Search algorithm

`solver.py` uses **iterative deepening A*** (IDA*): depth first search with an increasing bound on moves taken plus estimated moves remaining. Quarter turns and half turns each cost one move.

The original `basic` heuristic is the maximum of four lower bounds:

```text
ceil(misplaced corners / 4)
ceil(misplaced edges / 4)
ceil(twisted corners / 4)
ceil(flipped edges / 4)
```

Each face move affects at most four corners and four edges. Taking the maximum, rather than the sum, avoids counting overlapping effects twice.

The default `pattern` heuristic takes the maximum of `basic` and three exact abstract distances, built by breadth first search from solved coordinates using all 18 moves:

| Coordinate | States | Encoding |
| --- | --- | --- |
| Corner orientation | 3^7 = 2,187 | Base 3. Final twist determined by the orientation sum |
| Edge orientation | 2^11 = 2,048 | Base 2. Final flip determined by the orientation sum |
| Corner permutation | 8! = 40,320 | Lexicographic Lehmer rank |

Every real solution projects to a path in each abstract graph, so each shortest abstract distance is a lower bound on the real distance. Their **maximum**, not their sum, is admissible in the face turn metric. Edges and inverse moves have unit cost, so BFS from the goal produces distances to the goal. These bounds are also consistent under one move. Tests check the bound against exact breadth first distances for every full state within three moves, consistency on deeper walks, and independent sticker solutions.

The completed immutable tables retain 44,555 distance bytes plus small Python object overhead. Temporary BFS queues and a corner rank dictionary use more memory during construction and are released afterwards. Tables are built lazily once per process, with no files, graphics imports, or network access. Incomplete tables are never published after an interrupted setup.

Search skips consecutive turns of the same face and redundant orderings of commuting opposite face turns. Both heuristics share move ordering and pruning for controlled comparison.

## Python API

- `ida_star(state, max_depth=10)` returns a list of moves, or `None` if no solution is found within the depth limit.
- `solve(state, max_depth=10, max_nodes=None, time_limit=None, heuristic_name="pattern")` returns a `SearchResult` with the solution, status, visited nodes, elapsed seconds, search bound, heuristic name, and setup seconds. Select `heuristic_name="basic"` for the original bound.

Both search a validated copy, preserving the caller's state.

- Library node and time budgets default to unlimited. CLI defaults are 100,000 nodes and five seconds.
- Node counts include bound cutoffs but exclude table construction states.
- Elapsed time excludes the initial validated copy and includes table setup, reported separately as `setup_seconds`.
- Time checks run before each search node and every 256 expanded BFS coordinates. Limits are cooperative, so they can overshoot.
- Zero node or time budgets skip table construction. Completed tables are reused within the process.

Statuses are `solved`, `depth_limit`, `node_limit`, and `time_limit`. Reaching a limit **does not imply an unsolvable state**. The reported bound is the current search threshold, not necessarily a proven distance when interrupted. The CLI independently checks returned solutions against the sticker model.

## Limitations

The pattern bound ignores joint coordinate interactions and most edge permutation information. Search remains exponential, and each pattern evaluation costs more than the original count bound. Cold setup can dominate shallow solves. Stronger bounds do not guarantee faster bounded failures. See [benchmarks](BENCHMARKS.md) for measured gains, setup cost, and remaining failures. A two-phase or efficient arbitrary-state solver is not implemented.
