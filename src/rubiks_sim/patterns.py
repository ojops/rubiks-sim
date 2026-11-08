"""Small exact-distance abstractions for admissible face-turn lower bounds."""

from collections import deque
from collections.abc import Callable
from itertools import permutations
from math import factorial

from rubiks_sim.cubie import FULL_MOVE_TABLES, CubieState

_TABLES: tuple[bytes, bytes, bytes] | None = None
_FACTORIALS = tuple(factorial(i) for i in range(8))


def orientation_index(values, base: int) -> int:
    """Encode all but the final orientation, fixed by the orientation sum."""
    index = 0
    for value in values[:-1]:
        index = index * base + value
    return index


def permutation_index(values) -> int:
    """Rank an eight-corner permutation lexicographically (Lehmer code)."""
    return sum(
        sum(other < value for other in values[i + 1 :]) * _FACTORIALS[7 - i]
        for i, value in enumerate(values)
    )


def _distances(goal, size, successors, encode, check):
    distances = bytearray([255]) * size
    distances[encode(goal)] = 0
    queue = deque([(goal, 0)])
    visited = 0
    while queue:
        if visited % 256 == 0:
            check()
        state, distance = queue.popleft()
        visited += 1
        for child in successors(state):
            index = encode(child)
            if distances[index] == 255:
                distances[index] = distance + 1
                queue.append((child, distance + 1))
    if 255 in distances:
        raise RuntimeError("Pattern database contains unreachable coordinates")
    return bytes(distances)


def prepare_patterns(
    check: Callable[[], None] | None = None,
) -> tuple[bytes, bytes, bytes]:
    """Build 44,555 distance bytes once per process, with cooperative budget checks.

    Tables are published only when complete. Temporary BFS queues and rank maps
    are released afterwards. No rendering imports, files or network are needed.
    """
    global _TABLES
    if _TABLES is not None:
        return _TABLES
    if check is None:

        def check():
            pass

    check()
    moves = tuple(FULL_MOVE_TABLES.values())

    def orientation_table(size, base, permutation_slot):
        def successors(state):
            for move in moves:
                yield tuple(
                    (state[source] + delta) % base
                    for source, delta in zip(
                        move[permutation_slot], move[permutation_slot + 1]
                    )
                )

        return _distances(
            (0,) * size,
            base ** (size - 1),
            successors,
            lambda state: orientation_index(state, base),
            check,
        )

    corners = orientation_table(8, 3, 0)
    edges = orientation_table(12, 2, 2)
    # A temporary lookup makes BFS cheaper; only the dense byte table is retained.
    ranks = {state: rank for rank, state in enumerate(permutations(range(8)))}

    def corner_successors(state):
        for move in moves:
            yield tuple(state[source] for source in move[0])

    permutation = _distances(
        tuple(range(8)), factorial(8), corner_successors, ranks.__getitem__, check
    )
    check()
    _TABLES = corners, edges, permutation
    return _TABLES


def pattern_bound(state: CubieState) -> int:
    """Take the maximum of overlapping abstract distances, never their sum."""
    corners, edges, permutation = prepare_patterns()
    return max(
        corners[orientation_index(state.corner_orientation, 3)],
        edges[orientation_index(state.edge_orientation, 2)],
        permutation[permutation_index(state.corner_permutation)],
    )
