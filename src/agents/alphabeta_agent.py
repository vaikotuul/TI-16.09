"""Alpha-Beta pruning agent with static move ordering for Dots and Boxes.

Stage 3 implementation:
- Depth-limited Negamax with Alpha-Beta pruning over edge-mask representation.
- Critical bonus turn bounds shift: when g > 0, player retains turn, so bounds
  shift by -g: alpha' = alpha - g, beta' = beta - g, without perspective flip.
  When g == 0, turn passes to opponent: alpha' = -beta, beta' = -alpha.
- Static move ordering:
  1. Safe moves: edges that do not complete a box and do not create the 3rd side
     of any adjacent box.
  2. Capturing moves: edges that complete 1 or 2 boxes (g > 0).
  3. Other moves: edges that create the 3rd side of a box, sacrificing it.
- Global and agent-level node counter matching Stage 2 for direct comparison.
"""

from typing import List, Optional, Tuple
from src.game import (
    GameState,
    box_edges,
    boxes_completed_by_edge,
    edge_boxes,
    total_edges,
)

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


def order_moves(mask: int, rows: int, cols: int) -> List[int]:
    """Order legal moves to maximize alpha-beta cutoffs.

    Order:
    1. Safe moves (no box completed, no 3rd side created in any adjacent box)
    2. Box-completing moves (captures 1 or 2 boxes)
    3. Other moves (creates a 3rd side, gifting a box to the opponent)
    """
    num_edges = total_edges(rows, cols)
    safe: List[int] = []
    capture: List[int] = []
    other: List[int] = []

    for edge in range(num_edges):
        if not (mask & (1 << edge)):
            g = boxes_completed_by_edge(mask, edge, rows, cols)
            if g > 0:
                capture.append(edge)
            else:
                creates_third = False
                for r, c in edge_boxes(edge, rows, cols):
                    edges = box_edges(r, c, rows, cols)
                    drawn = sum(1 for be in edges if (mask & (1 << be)))
                    if drawn == 2:
                        creates_third = True
                        break
                if creates_third:
                    other.append(edge)
                else:
                    safe.append(edge)

    return safe + capture + other


def alphabeta(
    mask: int,
    player: int,
    depth: int,
    alpha: float,
    beta: float,
    rows: int,
    cols: int,
) -> Tuple[int, Optional[int]]:
    """Depth-limited minimax search with alpha-beta pruning and move ordering.

    Increments node_counter by 1 for each recursive call.
    Returns (best_score, best_move_index).
    """
    global node_counter
    node_counter += 1

    num_edges = total_edges(rows, cols)

    # Terminal state or depth limit reached
    if mask == (1 << num_edges) - 1 or depth <= 0:
        return 0, None

    best_val = -float("inf")
    best_move: Optional[int] = None

    moves = order_moves(mask, rows, cols)

    for edge in moves:
        new_mask = mask | (1 << edge)
        g = boxes_completed_by_edge(mask, edge, rows, cols)

        if g > 0:
            # Bonus turn: same player moves again; window shifted by g
            child_val, _ = alphabeta(
                new_mask, player, depth - 1, alpha - g, beta - g, rows, cols
            )
            val = g + child_val
        else:
            # Opponent turn: switch player and invert window
            child_val, _ = alphabeta(
                new_mask, 3 - player, depth - 1, -beta, -alpha, rows, cols
            )
            val = -child_val

        if val > best_val:
            best_val = val
            best_move = edge

        if best_val > alpha:
            alpha = best_val

        if alpha >= beta:
            break  # Beta cut-off

    return int(best_val), best_move


def choose_move(
    mask: int, player: int, depth: int, rows: int = 3, cols: int = 3
) -> int:
    """Choose best legal move index using Alpha-Beta search."""
    num_edges = total_edges(rows, cols)
    if mask == (1 << num_edges) - 1:
        raise ValueError("No legal moves available in terminal state.")
    if depth < 1:
        raise ValueError(f"Invalid search depth: {depth}; must be >= 1.")

    _, best_move = alphabeta(
        mask, player, depth, -float("inf"), float("inf"), rows, cols
    )
    assert best_move is not None
    return best_move


class AlphaBetaAgent:
    """Alpha-Beta agent for Dots and Boxes."""

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
