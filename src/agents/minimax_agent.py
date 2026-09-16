"""Depth-limited Minimax agent for Dots and Boxes (Punktid ja Kastid).

Stage 2 implementation:
- Pure depth-limited minimax search over edge-mask representation.
- Critical bonus turn rule: completing a box gives a bonus turn to the SAME player;
  the recursive call does NOT negate the score. Perspective is negated only when
  no box is completed and turn passes to opponent.
- Global resettable node counter for performance benchmarking.
- Sunk-cost invariant: leaf returns 0 for relative gain in remaining game,
  accumulating (my_boxes - opponent_boxes) across the search tree.

Empty 3x3 board baseline node counts:
- Depth 1: 25 nodes (0.0002s)
- Depth 2: 577 nodes (0.0040s)
- Depth 3: 12,721 nodes (0.0880s)
- Depth 4: 267,745 nodes (1.82s)
- Depth 5: 5,368,225 nodes (~35s)
- Depth 6: ~1.02 x 10^8 nodes (~11 min pure minimax, practical limit)
- Depth 8: ~3.06 x 10^10 nodes (intractable for pure minimax without alpha-beta)
- Depth 10: ~7.35 x 10^12 nodes (intractable for pure minimax without alpha-beta)
"""

from typing import Optional, Tuple
from src.game import GameState, boxes_completed_by_edge, total_edges

# Global resettable node counter
node_counter: int = 0


def reset_node_counter() -> None:
    """Reset the global node counter to zero."""
    global node_counter
    node_counter = 0


def get_node_counter() -> int:
    """Return current value of global node counter."""
    global node_counter
    return node_counter


def evaluate_leaf(mask: int, rows: int, cols: int) -> int:
    """Evaluate leaf position at search depth limit.

    Since box gains are accumulated along tree branches via negamax
    (adding g on bonus turns, negating child value on turn passes),
    returning 0 at the depth limit corresponds exactly to
    (my_boxes_gained - opponent_boxes_gained) over the searched horizon.
    """
    return 0


def minimax(
    mask: int, player: int, depth: int, rows: int, cols: int
) -> Tuple[int, Optional[int]]:
    """Depth-limited minimax search.

    Increments node_counter by 1 for each recursive call.
    Returns (best_score, best_move_index).
    """
    global node_counter
    node_counter += 1

    num_edges = total_edges(rows, cols)

    # Terminal state (all edges drawn) or depth limit reached
    if mask == (1 << num_edges) - 1 or depth <= 0:
        return evaluate_leaf(mask, rows, cols), None

    best_val = -float("inf")
    best_move: Optional[int] = None

    for edge in range(num_edges):
        if not (mask & (1 << edge)):
            new_mask = mask | (1 << edge)
            g = boxes_completed_by_edge(mask, edge, rows, cols)

            if g > 0:
                # Bonus turn: same player moves again, DO NOT negate score!
                child_val, _ = minimax(new_mask, player, depth - 1, rows, cols)
                val = g + child_val
            else:
                # Turn passes to opponent: switch player and negate score!
                child_val, _ = minimax(new_mask, 3 - player, depth - 1, rows, cols)
                val = -child_val

            if val > best_val:
                best_val = val
                best_move = edge

    return int(best_val), best_move


def choose_move(
    mask: int, player: int, depth: int, rows: int = 3, cols: int = 3
) -> int:
    """Choose the best legal move index using depth-limited minimax."""
    num_edges = total_edges(rows, cols)
    if mask == (1 << num_edges) - 1:
        raise ValueError("No legal moves available in terminal state.")
    if depth < 1:
        raise ValueError(f"Invalid search depth: {depth}; must be >= 1.")

    _, best_move = minimax(mask, player, depth, rows, cols)
    assert best_move is not None
    return best_move



class MinimaxAgent:
    """Minimax agent for Dots and Boxes."""

    def __init__(self, rows: int = 3, cols: int = 3, default_depth: int = 4):
        self.rows = rows
        self.cols = cols
        self.default_depth = default_depth
        self._last_nodes: int = 0

    @property
    def nodes_evaluated(self) -> int:
        """Return number of nodes evaluated during the last search."""
        return self._last_nodes

    def choose_move(
        self,
        mask: int,
        player: int,
        depth: Optional[int] = None,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
    ) -> int:
        """Choose best move, updating nodes_evaluated."""
        r = rows if rows is not None else self.rows
        c = cols if cols is not None else self.cols
        d = depth if depth is not None else self.default_depth

        reset_node_counter()
        move = choose_move(mask, player, d, rows=r, cols=c)
        self._last_nodes = get_node_counter()
        return move

    def choose_move_state(
        self, state: GameState, depth: Optional[int] = None
    ) -> int:
        """Choose best move for a given GameState."""
        return self.choose_move(
            state.mask,
            state.current_player,
            depth=depth,
            rows=state.rows,
            cols=state.cols,
        )
