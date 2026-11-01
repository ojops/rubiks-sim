# Cube and search notes

A sticker has an integer position, outward normal and immutable colour. Face
turns apply a signed 90-degree rotation to positions and normals in one layer.
Integer matrices avoid accumulated floating-point error in the logical model.
Visual geometry is synchronised from that exact model after animation.

The compact state stores permutations of eight corners and twelve edges, plus
corner orientation modulo three and edge orientation modulo two. A reachable
state requires distinct pieces, corner twists summing to 0 mod 3, edge flips
summing to 0 mod 2, and equal corner/edge permutation parity. These conditions
are sufficient for the standard fixed-centre 3x3 cubie convention. Sticker
conversion additionally checks geometry, unique sticker slots and centre colours.

For a move, `new_permutation[i] = old_permutation[source[i]]` and
`new_orientation[i] = (old_orientation[source[i]] + delta[i]) % modulus`.
The 18 full transformations are derived once from six quarter-turn tables.
This replaces repeated validation-set construction and two/three transformations
for half/inverse turns. Regression checks compare against independent sticker
geometry along seeded trajectories.

IDA* searches successively larger f=g+h bounds using depth-first search. The
heuristic is the maximum of ceilings of four misplaced/twisted/flipped piece
counts divided by four. A move affects at most four corners and four edges,
so this is admissible; the components overlap, so they must not be added.
Consecutive same-face turns can be combined. Opposite faces commute, allowing
one ordering to be pruned. Together these preserve optimality in the face-turn
metric for completed searches, but do not make deep searches cheap.

Search owns a copy. Before every node it checks the optional node/time budgets;
all visited nodes, including f-bound cutoffs, count toward the budget. Elapsed
seconds describe search after copying/validation. `bound` reports the current
or next IDA* bound; it is not a solved-distance guarantee on interrupted search.
KeyboardInterrupt propagates. Search limits return explicit status and no path.

## Before considering a general solver

The heuristic never exceeds three on valid states. Small move optimisations
help constant factors but cannot remove exponential search growth. Next assess
coordinate pruning: corner orientation has 3^7=2187 states, edge orientation
2^11=2048, and the middle-slice choice C(12,4)=495. Individual coordinates are
small; combined tables are larger (e.g. 2187*495=1,082,565). A byte per pruning
distance would be roughly 1 MiB for that combination, before metadata and move
tables. Python objects have much greater overhead than packed bytes/arrays.

A two-phase design also needs coordinate encoders, subgroup transition tables,
phase-two permutation search, table persistence/versioning and independent
solution verification. That is a separate algorithmic milestone, not a minor
extension. Choose between studying optimal IDA* and practical near-optimal
two-phase solving before implementing the tables. No general-solver speed or
optimality claim is made for random scrambles here.
