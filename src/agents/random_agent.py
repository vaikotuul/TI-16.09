"""Random move agent for Dots and Boxes."""

import random
from typing import List, Optional
from src.game import GameState, total_edges


def get_legal_moves_from_mask(mask: int, rows: int, cols: int) -> List[int]:
    """Return all undrawn edge indices for a given board mask."""
    num_edges = total_edges(rows, cols)
    return [i for i in range(num_edges) if not (mask & (1 << i))]


def choose_move(
    mask: int, rows: int, cols: int, rng: Optional[random.Random] = None
) -> int:
    """Select a move uniformly at random from undrawn edges."""
    moves = get_legal_moves_from_mask(mask, rows, cols)
    if not moves:
        raise ValueError("No legal moves available in current state.")
    picker = rng if rng is not None else random
    return picker.choice(moves)


class RandomAgent:
    """Agent that chooses uniformly random legal moves."""

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)

    def choose_move(self, mask: int, rows: int, cols: int) -> int:
        """Choose a random legal edge index given mask and board size."""
        return choose_move(mask, rows, cols, self.rng)

    def choose_move_state(self, state: GameState) -> int:
        """Choose a random legal edge index given a GameState."""
        return choose_move(state.mask, state.rows, state.cols, self.rng)
