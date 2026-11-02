"""The supported face turns; a half turn counts as one move."""

from collections.abc import Iterable

FACES = ("U", "D", "F", "B", "R", "L")
MOVES = tuple(face + suffix for face in FACES for suffix in ("", "'", "2"))
VALID_MOVES = frozenset(MOVES)


def parse_moves(moves: str | Iterable[str]) -> list[str]:
    """Return validated moves from a space-separated string or iterable.

    Raise TypeError for non-string moves and ValueError for unsupported turns.
    Consume and validate the entire input before returning any moves.
    """
    result = moves.split() if isinstance(moves, str) else list(moves)
    for move in result:
        if not isinstance(move, str):
            raise TypeError("Move notation must be a string")
        if move not in VALID_MOVES:
            raise ValueError(f"Invalid move: {move}")
    return result
