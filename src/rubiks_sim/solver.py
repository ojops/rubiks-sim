from math import ceil


FACES = ("U", "D", "F", "B", "R", "L")

MOVES = tuple(
    face + suffix
    for face in FACES
    for suffix in ("", "'", "2")
)

OPPOSITE_FACES = {
    "U": "D",
    "D": "U",
    "F": "B",
    "B": "F",
    "R": "L",
    "L": "R",
}

FACE_ORDER = {
    face: index
    for index, face in enumerate(FACES)
}


def heuristic(state):
    """
    Estimate a lower bound for the number of moves to solve the cube
    """

    misplaced_corners = sum(
        piece != position
        for position, piece in enumerate(state.corner_permutation)
    )

    misplaced_edges = sum(
        piece != position
        for position, piece in enumerate(state.edge_permutation)
    )

    twisted_corners = sum(
        orientation != 0
        for orientation in state.corner_orientation
    )

    flipped_edges = sum(
        orientation != 0
        for orientation in state.edge_orientation
    )

    return max(
        ceil(misplaced_corners / 4),
        ceil(misplaced_edges / 4),
        ceil(twisted_corners / 4),
        ceil(flipped_edges / 4),
    )


def inverse_move(move):
    if move.endswith("2"):
        return move

    if move.endswith("'"):
        return move[0]

    return move + "'"


def ida_star(state, max_depth=10):
    """
    Find a solution using Iterative Deepening A*

    Returns a list of singmaster moves or None if no solution is found within max_depth
    """

    path = []
    nodes_searched = 0

    def search(depth, bound, previous_face):
        nonlocal nodes_searched

        nodes_searched += 1

        estimate = depth + heuristic(state)

        if estimate > bound:
            return estimate

        if state.is_solved():
            return True

        minimum_excess = float("inf")

        for move in MOVES:
            face = move[0]

            # Avoid consecutive turns of the same face
            if face == previous_face:
                continue

            # Opposite faces commute so only explore one ordering
            if (
                previous_face is not None
                and OPPOSITE_FACES[previous_face] == face
                and FACE_ORDER[previous_face] > FACE_ORDER[face]
            ):
                continue

            state.apply_move(move)
            path.append(move)

            result = search(
                depth + 1,
                bound,
                face,
            )

            if result is True:
                return True

            path.pop()
            state.apply_move(inverse_move(move))

            minimum_excess = min(minimum_excess, result)

        return minimum_excess

    bound = heuristic(state)

    while bound <= max_depth:
        result = search(0, bound, None)

        if result is True:
            return path.copy()

        if result == float("inf"):
            return None

        bound = result

    return None