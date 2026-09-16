"""Symmetry Canonicalization Agent for Dots and Boxes.

Stage 5 implementation:
- Exploits D4 dihedral symmetry of the board (up to 8 symmetries: 4 rotations,
  4 reflections for square boards; 4 reflections/rotations for rectangular boards).
- Precomputes edge index permutation tables once at initialization.
- Canonicalizes board edge masks before TT lookups and stores by taking the
  lexicographically smallest (integer minimum) mask among all symmetric variants.
- Achieves up to ~8x reduction in stored transposition table states.
- Preserves exact game-theoretic values and move choices from Stage 3 and Stage 4.
"""

import functools
import time
from typing import Callable, List, Optional, Tuple
from src.game import (
    GameState,
    edge_to_index,
    index_to_edge,
    total_edges,
)
from src.agents.transposition_agent import (
    FLAG_EXACT,
    FLAG_LOWERBOUND,
    FLAG_UPPERBOUND,
    DictTranspositionTable,
    FlatTranspositionTable,
    TranspositionTable,
    order_moves_tt,
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


@functools.lru_cache(maxsize=None)
def get_symmetry_permutations(rows: int, cols: int) -> Tuple[Tuple[int, ...], ...]:
    """Compute and cache all valid edge index permutations under D4 grid symmetries.

    Dots coordinates are in [0..rows] x [0..cols].
    For square boards (rows == cols), all 8 D4 symmetries are valid.
    For rectangular boards (rows != cols), only the 4 aspect-ratio-preserving
    transformations (Identity, Flip H, Flip V, Rot 180) are valid.
    """
    transforms: List[Callable[[int, int], Tuple[int, int]]] = []

    # 1. Identity
    transforms.append(lambda r, c: (r, c))
    # 2. Flip horizontal (across vertical centerline)
    transforms.append(lambda r, c: (r, cols - c))
    # 3. Flip vertical (across horizontal centerline)
    transforms.append(lambda r, c: (rows - r, c))
    # 4. Rotate 180 deg (flip both)
    transforms.append(lambda r, c: (rows - r, cols - c))

    if rows == cols:
        N = rows
        # 5. Rotate 90 deg clockwise: (r, c) -> (c, N - r)
        transforms.append(lambda r, c: (c, N - r))
        # 6. Rotate 270 deg clockwise: (r, c) -> (N - c, r)
        transforms.append(lambda r, c: (N - c, r))
        # 7. Flip main diagonal: (r, c) -> (c, r)
        transforms.append(lambda r, c: (c, r))
        # 8. Flip anti-diagonal: (r, c) -> (N - c, N - r)
        transforms.append(lambda r, c: (N - c, N - r))

    num_edges = total_edges(rows, cols)
    permutations: List[Tuple[int, ...]] = []

    for T in transforms:
        perm = [0] * num_edges
        for e in range(num_edges):
            kind, r, c = index_to_edge(e, rows, cols)
            if kind == "H":
                p1 = (r, c)
                p2 = (r, c + 1)
            else:
                p1 = (r, c)
                p2 = (r + 1, c)

            p1_prime = T(p1[0], p1[1])
            p2_prime = T(p2[0], p2[1])

            if p1_prime[0] == p2_prime[0]:
                # Transformed edge is horizontal
                r_prime = p1_prime[0]
                c_prime = min(p1_prime[1], p2_prime[1])
                e_prime = edge_to_index("H", r_prime, c_prime, rows, cols)
            else:
                # Transformed edge is vertical
                r_prime = min(p1_prime[0], p2_prime[0])
                c_prime = p1_prime[1]
                e_prime = edge_to_index("V", r_prime, c_prime, rows, cols)

            perm[e] = e_prime
        permutations.append(tuple(perm))

    return tuple(permutations)


def canonicalize_mask(mask: int, rows: int, cols: int) -> int:
    """Return the lexicographically minimum edge mask under all D4 symmetries."""
    perms = get_symmetry_permutations(rows, cols)
    min_mask = mask

    for perm in perms[1:]:
        m = 0
        temp = mask
        while temp:
            lsb = temp & -temp
            edge_idx = lsb.bit_length() - 1
            m |= 1 << perm[edge_idx]
            temp ^= lsb
        if m < min_mask:
            min_mask = m

    return min_mask


def alphabeta_sym(
    mask: int,
    player: int,
    depth: int,
    alpha: float,
    beta: float,
    rows: int,
    cols: int,
    tt: TranspositionTable,
) -> Tuple[int, Optional[int]]:
    """Alpha-Beta search with Transposition Table and Symmetry Canonicalization."""
    global node_counter
    node_counter += 1

    num_edges = total_edges(rows, cols)

    # Terminal state or depth limit
    if mask == (1 << num_edges) - 1 or depth <= 0:
        return 0, None

    orig_alpha = alpha
    c_mask = canonicalize_mask(mask, rows, cols)

    # Lookup in TT using canonical mask
    entry = tt.lookup(c_mask)
    tt_move: Optional[int] = None
    if entry is not None:
        e_depth, e_flag, e_val, e_move = entry
        tt_move = e_move if c_mask == mask else None
        if e_depth >= depth:
            if e_flag == FLAG_EXACT:
                return e_val, e_move
            elif e_flag == FLAG_LOWERBOUND:
                if e_val >= beta:
                    return e_val, e_move
                alpha = max(alpha, e_val)
            elif e_flag == FLAG_UPPERBOUND:
                if e_val <= alpha:
                    return e_val, e_move
                beta = min(beta, e_val)
            if alpha >= beta:
                return e_val, e_move

    best_val = -float("inf")
    best_move: Optional[int] = None

    from src.game import boxes_completed_by_edge

    moves = order_moves_tt(mask, rows, cols, tt_move)

    for edge in moves:
        new_mask = mask | (1 << edge)
        g = boxes_completed_by_edge(mask, edge, rows, cols)

        if g > 0:
            child_val, _ = alphabeta_sym(
                new_mask, player, depth - 1, alpha - g, beta - g, rows, cols, tt
            )
            val = g + child_val
        else:
            child_val, _ = alphabeta_sym(
                new_mask, 3 - player, depth - 1, -beta, -alpha, rows, cols, tt
            )
            val = -child_val

        if val > best_val:
            best_val = val
            best_move = edge

        if best_val > alpha:
            alpha = best_val

        if alpha >= beta:
            break

    # Store entry in TT under the canonical mask key
    if best_val <= orig_alpha:
        flag = FLAG_UPPERBOUND
    elif best_val >= beta:
        flag = FLAG_LOWERBOUND
    else:
        flag = FLAG_EXACT

    tt.store(c_mask, depth, flag, int(best_val), best_move if c_mask == mask else None)
    return int(best_val), best_move


def choose_move(
    mask: int,
    player: int,
    depth: int,
    rows: int = 3,
    cols: int = 3,
    tt: Optional[TranspositionTable] = None,
) -> int:
    """Choose best move index using Alpha-Beta with symmetry canonicalization."""
    num_edges = total_edges(rows, cols)
    if mask == (1 << num_edges) - 1:
        raise ValueError("No legal moves available in terminal state.")
    if depth < 1:
        raise ValueError(f"Invalid search depth: {depth}; must be >= 1.")

    if tt is None:
        tt = DictTranspositionTable()

    _, best_move = alphabeta_sym(
        mask, player, depth, -float("inf"), float("inf"), rows, cols, tt
    )
    assert best_move is not None
    return best_move


class SymmetryAgent:
    """Agent using Alpha-Beta search with Transposition Table and D4 Symmetry Reduction."""

    def __init__(
        self,
        rows: int = 3,
        cols: int = 3,
        default_depth: int = 4,
        use_flat: bool = False,
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.default_depth = default_depth
        num_e = total_edges(rows, cols)
        if use_flat and num_e <= 24:
            self.tt: TranspositionTable = FlatTranspositionTable(num_e)
        else:
            self.tt = DictTranspositionTable()
        self._last_nodes: int = 0

    @property
    def nodes_evaluated(self) -> int:
        return self._last_nodes

    def choose_move(
        self,
        mask: int,
        player: int,
        depth: Optional[int] = None,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
    ) -> int:
        r = rows if rows is not None else self.rows
        c = cols if cols is not None else self.cols
        d = depth if depth is not None else self.default_depth

        reset_node_counter()
        move = choose_move(mask, player, d, rows=r, cols=c, tt=self.tt)
        self._last_nodes = get_node_counter()
        return move

    def choose_move_state(
        self, state: GameState, depth: Optional[int] = None
    ) -> int:
        return self.choose_move(
            state.mask,
            state.current_player,
            depth=depth,
            rows=state.rows,
            cols=state.cols,
        )
