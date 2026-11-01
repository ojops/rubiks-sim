"""The supported face turns; a half turn counts as one move."""

FACES = ("U", "D", "F", "B", "R", "L")
MOVES = tuple(face + suffix for face in FACES for suffix in ("", "'", "2"))
VALID_MOVES = frozenset(MOVES)


def parse_moves(moves) -> list[str]:
    """Validate the whole sequence before a caller starts mutating state."""
    result = moves.split() if isinstance(moves, str) else list(moves)
    for move in result:
        if not isinstance(move, str):
            raise TypeError("Move notation must be a string")
        if move not in VALID_MOVES:
            raise ValueError(f"Invalid move: {move}")
    return result
