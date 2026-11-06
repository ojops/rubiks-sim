"""Bounded IDA* search using the compact cubie representation."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite
from time import perf_counter
from typing import TYPE_CHECKING

from rubiks_sim.notation import FACES, MOVES

if TYPE_CHECKING:
    from rubiks_sim.cubie import CubieState

OPPOSITE_FACES = {
    "U": "D",
    "D": "U",
    "F": "B",
    "B": "F",
    "R": "L",
    "L": "R",
}

FACE_ORDER = {face: index for index, face in enumerate(FACES)}


def heuristic(state: CubieState) -> int:
    """Estimate remaining moves without overcounting overlapping cubie changes."""

    misplaced_corners = sum(
        piece != position for position, piece in enumerate(state.corner_permutation)
    )

    misplaced_edges = sum(
        piece != position for position, piece in enumerate(state.edge_permutation)
    )

    twisted_corners = sum(orientation != 0 for orientation in state.corner_orientation)

    flipped_edges = sum(orientation != 0 for orientation in state.edge_orientation)

    return max(
        ceil(misplaced_corners / 4),
        ceil(misplaced_edges / 4),
        ceil(twisted_corners / 4),
        ceil(flipped_edges / 4),
    )


def inverse_move(move: str) -> str:
    """Return the inverse of an already validated Singmaster move"""
    if move.endswith("2"):
        return move

    if move.endswith("'"):
        return move[0]

    return move + "'"


@dataclass(frozen=True)
class SearchResult:
    """Store the solution, stopping reason and IDA* search statistics.

    The solution is None unless solved. Node counts include bound cutoffs;
    elapsed time excludes the initial state copy. The bound is a search threshold.
    """

    solution: tuple[str, ...] | None
    status: str
    nodes: int
    elapsed_seconds: float
    bound: int


class _SearchLimit(Exception):
    pass


def solve(
    state: CubieState,
    max_depth: int = 10,
    *,
    max_nodes: int | None = None,
    time_limit: float | None = None,
) -> SearchResult:
    """Search a validated copy using bounded IDA*; half turns cost one move.

    Limits are optional (None means unlimited). Invalid limits raise ValueError;
    unexpected exceptions propagate without modifying the caller's state.
    """

    if type(max_depth) is not int or max_depth < 0:
        raise ValueError("max_depth must be a non-negative integer")

    if max_nodes is not None and (type(max_nodes) is not int or max_nodes < 0):
        raise ValueError("max_nodes must be a non-negative integer")

    if time_limit is not None and (
        isinstance(time_limit, bool)
        or not isinstance(time_limit, (int, float))
        or not isfinite(time_limit)
        or time_limit < 0
    ):
        raise ValueError("time_limit must be finite and non-negative")

    state = state.copy()
    started = perf_counter()
    path = []
    nodes = 0
    bound = heuristic(state)

    def finish(status, solution=None):
        return SearchResult(solution, status, nodes, perf_counter() - started, bound)

    def search(depth, previous_face):
        nonlocal nodes
        if max_nodes is not None and nodes >= max_nodes:
            raise _SearchLimit("node_limit")

        if time_limit is not None and perf_counter() - started >= time_limit:
            raise _SearchLimit("time_limit")

        nodes += 1
        estimate = depth + heuristic(state)
        if estimate > bound:
            return estimate

        if state.is_solved():
            return True

        minimum_excess = float("inf")
        for move in MOVES:
            face = move[0]
            if face == previous_face:
                continue
            # Opposite faces commute so choose one canonical ordering
            if (
                previous_face is not None
                and OPPOSITE_FACES[previous_face] == face
                and FACE_ORDER[previous_face] > FACE_ORDER[face]
            ):
                continue
            state.apply_move(move)
            path.append(move)
            try:
                result = search(depth + 1, face)
            finally:
                state.apply_move(inverse_move(move))
            if result is True:
                return True
            path.pop()
            minimum_excess = min(minimum_excess, result)
        return minimum_excess

    try:
        while bound <= max_depth:
            result = search(0, None)
            if result is True:
                return finish("solved", tuple(path))
            if result == float("inf"):
                break
            bound = result
    except _SearchLimit as stop:
        return finish(str(stop))
    return finish("depth_limit")


def ida_star(state: CubieState, max_depth: int = 10) -> list[str] | None:
    """Find a solution within max_depth, without modifying the input state."""

    result = solve(state, max_depth)
    return list(result.solution) if result.solution is not None else None
