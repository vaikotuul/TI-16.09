"""Transposition Table and Iterative Deepening agent for Dots and Boxes.

Stage 4 implementation:
- Alpha-Beta search with Transposition Table (TT) memoization.
- Search scores are relative to the current player (negamax convention),
  meaning the table key is SOLELY the board edge-mask.
- Both Flat array (bytearray, O(1) direct indexing without hashing or collisions)
  and Hash dict (DictTranspositionTable) implementations.
- Standard TT entry format: (depth, flag, value, best_move) with EXACT,
  LOWERBOUND (beta-cutoff), and UPPERBOUND (alpha-fail-low) flags.
- TT move ordering: best move retrieved from TT is tried first.
- Iterative deepening with a wall-clock time budget (default 1.0s).
"""

import time
from typing import Any, List, Optional, Tuple, Union
from src.game import (
    GameState,
    box_edges,
    boxes_completed_by_edge,
    edge_boxes,
    total_edges,
)

# TT flags
FLAG_EXACT: int = 0
FLAG_LOWERBOUND: int = 1  # Beta-cutoff (fail-high: value >= beta)
FLAG_UPPERBOUND: int = 2  # Alpha-cutoff (fail-low: value <= alpha)

# Global node counter
node_counter: int = 0


def reset_node_counter() -> None:
    """Reset the global node counter to zero."""
    global node_counter
    node_counter = 0


def get_node_counter() -> int:
    """Return current value of global node counter."""
    global node_counter
    return node_counter


class DictTranspositionTable:
    """Hash-map based Transposition Table."""

    def __init__(self) -> None:
        self.table: dict[int, Tuple[int, int, int, Optional[int]]] = {}

    def lookup(
        self, mask: int
    ) -> Optional[Tuple[int, int, int, Optional[int]]]:
        """Look up mask in table, returning (depth, flag, value, best_move) or None."""
        return self.table.get(mask)

    def store(
        self,
        mask: int,
        depth: int,
        flag: int,
        value: int,
        best_move: Optional[int],
    ) -> None:
        """Store or replace an entry if new depth >= existing depth."""
        existing = self.table.get(mask)
        if existing is None or depth >= existing[0]:
            self.table[mask] = (depth, flag, value, best_move)

    def clear(self) -> None:
        """Clear all entries."""
        self.table.clear()

    def __len__(self) -> int:
        return len(self.table)


class FlatTranspositionTable:
    """Flat memory array Transposition Table using direct mask indexing.

    Uses a contiguous bytearray where index is the edge mask itself.
    No hashing, no buckets, no collisions.
    Layout per entry: 4 bytes:
      - Byte 0: depth + 1 (0 indicates uninitialized / empty)
      - Byte 1: flag (0=EXACT, 1=LOWER, 2=UPPER)
      - Byte 2: value + 128 (encodes signed 8-bit integer in [0, 255])
      - Byte 3: best_move + 1 (0 indicates None, 1..25 indicates edge index 0..24)
    """

    def __init__(self, num_edges: int) -> None:
        self.num_edges = num_edges
        self.num_entries = 1 << num_edges
        self.entry_size = 4
        self.buffer = bytearray(self.num_entries * self.entry_size)

    @property
    def size_bytes(self) -> int:
        """Return total buffer size in bytes."""
        return len(self.buffer)

    @property
    def size_mb(self) -> float:
        """Return total buffer size in mebibytes (MiB)."""
        return len(self.buffer) / (1024 * 1024)

    def lookup(
        self, mask: int
    ) -> Optional[Tuple[int, int, int, Optional[int]]]:
        """Look up mask by direct offset."""
        idx = mask * self.entry_size
        d_p1 = self.buffer[idx]
        if d_p1 == 0:
            return None
        depth = d_p1 - 1
        flag = self.buffer[idx + 1]
        val = self.buffer[idx + 2] - 128
        m_p1 = self.buffer[idx + 3]
        best_move = (m_p1 - 1) if m_p1 > 0 else None
        return (depth, flag, val, best_move)

    def store(
        self,
        mask: int,
        depth: int,
        flag: int,
        value: int,
        best_move: Optional[int],
    ) -> None:
        """Store entry directly at index `mask * 4`."""
        idx = mask * self.entry_size
        existing_dp1 = self.buffer[idx]
        if existing_dp1 == 0 or depth >= (existing_dp1 - 1):
            self.buffer[idx] = min(depth + 1, 255)
            self.buffer[idx + 1] = flag
            self.buffer[idx + 2] = max(0, min(255, value + 128))
            self.buffer[idx + 3] = (best_move + 1) if best_move is not None else 0

    def clear(self) -> None:
        """Clear all entries by zeroing buffer."""
        self.buffer = bytearray(self.num_entries * self.entry_size)


TranspositionTable = Union[DictTranspositionTable, FlatTranspositionTable]


def order_moves_tt(
    mask: int,
    rows: int,
    cols: int,
    tt_move: Optional[int] = None,
) -> List[int]:
    """Order legal moves, placing the TT suggestion first if valid."""
    num_edges = total_edges(rows, cols)
    safe: List[int] = []
    capture: List[int] = []
    other: List[int] = []

    for edge in range(num_edges):
        if not (mask & (1 << edge)):
            if edge == tt_move:
                continue
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

    ordered = safe + capture + other
    if tt_move is not None and not (mask & (1 << tt_move)):
        return [tt_move] + ordered
    return ordered


def alphabeta_tt(
    mask: int,
    player: int,
    depth: int,
    alpha: float,
    beta: float,
    rows: int,
    cols: int,
    tt: TranspositionTable,
) -> Tuple[int, Optional[int]]:
    """Alpha-Beta search integrated with Transposition Table."""
    global node_counter
    node_counter += 1

    num_edges = total_edges(rows, cols)

    # Terminal state check
    if mask == (1 << num_edges) - 1 or depth <= 0:
        return 0, None

    orig_alpha = alpha
    tt_move: Optional[int] = None

    # TT Lookup
    entry = tt.lookup(mask)
    if entry is not None:
        e_depth, e_flag, e_val, e_move = entry
        tt_move = e_move
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

    moves = order_moves_tt(mask, rows, cols, tt_move)

    for edge in moves:
        new_mask = mask | (1 << edge)
        g = boxes_completed_by_edge(mask, edge, rows, cols)

        if g > 0:
            # Bonus turn: same player moves again; bounds shifted by g
            child_val, _ = alphabeta_tt(
                new_mask, player, depth - 1, alpha - g, beta - g, rows, cols, tt
            )
            val = g + child_val
        else:
            # Opponent turn: switch player and invert bounds
            child_val, _ = alphabeta_tt(
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

    # Store in TT
    if best_val <= orig_alpha:
        flag = FLAG_UPPERBOUND
    elif best_val >= beta:
        flag = FLAG_LOWERBOUND
    else:
        flag = FLAG_EXACT

    tt.store(mask, depth, flag, int(best_val), best_move)
    return int(best_val), best_move


def choose_move_iterative_deepening(
    mask: int,
    player: int,
    time_budget: float = 1.0,
    max_depth: Optional[int] = None,
    rows: int = 3,
    cols: int = 3,
    tt: Optional[TranspositionTable] = None,
) -> Tuple[int, int]:
    """Iterative deepening search with a wall-clock time limit.

    Searches depths 1, 2, 3, ... using the transposition table to share
    information across iterations. Returns (best_move, depth_reached).
    """
    num_edges = total_edges(rows, cols)
    if mask == (1 << num_edges) - 1:
        raise ValueError("No legal moves available in terminal state.")

    if tt is None:
        tt = DictTranspositionTable()

    target_max = max_depth if max_depth is not None else num_edges
    start_time = time.perf_counter()
    best_move: Optional[int] = None
    completed_depth = 0

    for depth in range(1, target_max + 1):
        now = time.perf_counter()
        if now - start_time >= time_budget and completed_depth > 0:
            break

        val, move = alphabeta_tt(
            mask, player, depth, -float("inf"), float("inf"), rows, cols, tt
        )

        elapsed = time.perf_counter() - start_time
        if elapsed > time_budget and completed_depth > 0:
            # Over budget; keep move from previously fully completed depth
            break

        best_move = move
        completed_depth = depth

        # If terminal reached or game completely decided
        if depth == num_edges:
            break

    assert best_move is not None
    return best_move, completed_depth



class TranspositionAgent:
    """Agent using Alpha-Beta with Transposition Table and Iterative Deepening."""

    def __init__(
        self,
        rows: int = 3,
        cols: int = 3,
        default_depth: Optional[int] = 6,
        time_budget: float = 1.0,
        use_flat: bool = False,
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.default_depth = default_depth
        self.time_budget = time_budget
        num_e = total_edges(rows, cols)
        if use_flat and num_e <= 24:
            self.tt: TranspositionTable = FlatTranspositionTable(num_e)
        else:
            self.tt = DictTranspositionTable()
        self._last_nodes: int = 0
        self._last_depth: int = 0

    @property
    def nodes_evaluated(self) -> int:
        return self._last_nodes

    @property
    def depth_reached(self) -> int:
        return self._last_depth

    def choose_move(
        self,
        mask: int,
        player: int,
        depth: Optional[int] = None,
        time_budget: Optional[float] = None,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
    ) -> int:
        r = rows if rows is not None else self.rows
        c = cols if cols is not None else self.cols
        budget = time_budget if time_budget is not None else self.time_budget
        d = depth if depth is not None else self.default_depth

        reset_node_counter()
        if budget is not None and budget > 0:
            move, reached = choose_move_iterative_deepening(
                mask, player, time_budget=budget, max_depth=d, rows=r, cols=c, tt=self.tt
            )
            self._last_depth = reached
        else:
            target_depth = d if d is not None else 6
            _, move = alphabeta_tt(
                mask, player, target_depth, -float("inf"), float("inf"), r, c, self.tt
            )
            self._last_depth = target_depth
            assert move is not None

        self._last_nodes = get_node_counter()
        return move

    def choose_move_state(
        self,
        state: GameState,
        depth: Optional[int] = None,
        time_budget: Optional[float] = None,
    ) -> int:
        return self.choose_move(
            state.mask,
            state.current_player,
            depth=depth,
            time_budget=time_budget,
            rows=state.rows,
            cols=state.cols,
        )
