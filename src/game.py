"""Dots and Boxes (Punktid ja Kastid) game engine.

EDGE INDEXING CONTRACT:
The board is defined by dimensions `rows` and `cols` (the count of boxes).
Dots grid size is `(rows + 1) * (cols + 1)`.

Edges are partitioned into horizontal ('H') and vertical ('V') sets:
1. Horizontal edges ('H'):
   - row `r` in `0 .. rows` (inclusive), col `c` in `0 .. cols - 1` (inclusive).
   - Count: `h_count = (rows + 1) * cols`.
   - Index formula: `index = r * cols + c`.
   - Index range: `0 <= index < h_count`.
   - Inverse: `r = index // cols`, `c = index % cols`, type = 'H'.

2. Vertical edges ('V'):
   - row `r` in `0 .. rows - 1` (inclusive), col `c` in `0 .. cols` (inclusive).
   - Count: `v_count = rows * (cols + 1)`.
   - Index formula: `index = h_count + r * (cols + 1) + c`.
   - Index range: `h_count <= index < h_count + v_count`.
   - Inverse: `offset = index - h_count`, `r = offset // (cols + 1)`,
              `c = offset % (cols + 1)`, type = 'V'.

Canonical board state: an integer bitmask where bit `i` (1 << i) is 1
if edge `i` has been drawn, and 0 otherwise. Total edges: `h_count + v_count`.
This indexing contract is fixed and immutable across all development stages.
"""

from typing import Dict, List, Optional, Tuple


def num_horizontal_edges(rows: int, cols: int) -> int:
    """Return the total number of horizontal edges."""
    return (rows + 1) * cols


def num_vertical_edges(rows: int, cols: int) -> int:
    """Return the total number of vertical edges."""
    return rows * (cols + 1)


def total_edges(rows: int, cols: int) -> int:
    """Return total number of edges on the board."""
    return num_horizontal_edges(rows, cols) + num_vertical_edges(rows, cols)


def edge_to_index(edge_type: str, r: int, c: int, rows: int, cols: int) -> int:
    """Convert (edge_type, row, col) to a stable integer edge index."""
    kind = edge_type.upper()
    if kind == "H":
        if not (0 <= r <= rows and 0 <= c < cols):
            raise ValueError(f"Invalid horizontal edge coordinate: ({r}, {c})")
        return r * cols + c
    elif kind == "V":
        if not (0 <= r < rows and 0 <= c <= cols):
            raise ValueError(f"Invalid vertical edge coordinate: ({r}, {c})")
        return num_horizontal_edges(rows, cols) + r * (cols + 1) + c
    else:
        raise ValueError(f"Invalid edge_type '{edge_type}'; expected 'H' or 'V'.")


def index_to_edge(index: int, rows: int, cols: int) -> Tuple[str, int, int]:
    """Convert integer edge index to (edge_type, row, col)."""
    h_count = num_horizontal_edges(rows, cols)
    total = h_count + num_vertical_edges(rows, cols)
    if not (0 <= index < total):
        raise ValueError(f"Edge index {index} out of bounds for {rows}x{cols} board.")
    if index < h_count:
        return "H", index // cols, index % cols
    idx_v = index - h_count
    return "V", idx_v // (cols + 1), idx_v % (cols + 1)


def box_edges(r: int, c: int, rows: int, cols: int) -> Tuple[int, int, int, int]:
    """Return the 4 edge indices (top, bottom, left, right) of box (r, c)."""
    if not (0 <= r < rows and 0 <= c < cols):
        raise ValueError(f"Box coordinates ({r}, {c}) out of bounds.")
    top = edge_to_index("H", r, c, rows, cols)
    bottom = edge_to_index("H", r + 1, c, rows, cols)
    left = edge_to_index("V", r, c, rows, cols)
    right = edge_to_index("V", r, c + 1, rows, cols)
    return top, bottom, left, right


def edge_boxes(edge_index: int, rows: int, cols: int) -> List[Tuple[int, int]]:
    """Return list of box coordinates (r, c) adjacent to the given edge."""
    edge_type, r, c = index_to_edge(edge_index, rows, cols)
    boxes = []
    if edge_type == "H":
        if r > 0:
            boxes.append((r - 1, c))
        if r < rows:
            boxes.append((r, c))
    else:
        if c > 0:
            boxes.append((r, c - 1))
        if c < cols:
            boxes.append((r, c))
    return boxes


def completed_boxes_by_edge(
    mask: int, edge: int, rows: int, cols: int
) -> List[Tuple[int, int]]:
    """Return (r, c) boxes that are completed by adding `edge`.

    Works whether `mask` already has the bit for `edge` set or not.
    """
    completed = []
    for r, c in edge_boxes(edge, rows, cols):
        top, bottom, left, right = box_edges(r, c, rows, cols)
        other_edges = [e for e in (top, bottom, left, right) if e != edge]
        if all((mask & (1 << e)) != 0 for e in other_edges):
            completed.append((r, c))
    return completed


def boxes_completed_by_edge(mask: int, edge: int, rows: int, cols: int) -> int:
    """Return number of boxes (0, 1, or 2) completed by drawing `edge`."""
    return len(completed_boxes_by_edge(mask, edge, rows, cols))


class GameState:
    """Immutable representation of a Dots and Boxes game state."""

    def __init__(
        self,
        rows: int,
        cols: int,
        mask: int = 0,
        current_player: int = 1,
        scores: Optional[Dict[int, int]] = None,
        box_owners: Optional[Dict[Tuple[int, int], int]] = None,
    ):
        self.rows = rows
        self.cols = cols
        self.mask = mask
        self.current_player = current_player
        self.scores = {1: 0, 2: 0} if scores is None else dict(scores)
        self.box_owners = {} if box_owners is None else dict(box_owners)
        self.num_edges = total_edges(rows, cols)
        self.total_boxes = rows * cols

    def legal_moves(self) -> List[int]:
        """Return list of indices for edges that have not been drawn yet."""
        return [i for i in range(self.num_edges) if not (self.mask & (1 << i))]

    def is_legal_move(self, edge: int) -> bool:
        """Check if an edge index is in range and not yet drawn."""
        return 0 <= edge < self.num_edges and not (self.mask & (1 << edge))

    def make_move(self, edge: int) -> "GameState":
        """Apply a move and return the resulting new GameState."""
        if not self.is_legal_move(edge):
            raise ValueError(f"Illegal move {edge} for current state.")

        new_mask = self.mask | (1 << edge)
        new_boxes = completed_boxes_by_edge(self.mask, edge, self.rows, self.cols)
        new_owners = dict(self.box_owners)
        new_scores = dict(self.scores)

        if new_boxes:
            for b in new_boxes:
                new_owners[b] = self.current_player
            new_scores[self.current_player] += len(new_boxes)
            next_player = self.current_player  # Bonus turn!
        else:
            next_player = 2 if self.current_player == 1 else 1

        return GameState(
            rows=self.rows,
            cols=self.cols,
            mask=new_mask,
            current_player=next_player,
            scores=new_scores,
            box_owners=new_owners,
        )

    def is_terminal(self) -> bool:
        """Game is over when all edges are drawn."""
        return self.mask == (1 << self.num_edges) - 1

    def winner(self) -> Optional[int]:
        """Return winning player (1 or 2), 0 for tie, or None if not finished."""
        if not self.is_terminal():
            return None
        if self.scores[1] > self.scores[2]:
            return 1
        if self.scores[2] > self.scores[1]:
            return 2
        return 0

    def render(self) -> str:
        """Render board with dots, edges, and box owner markings."""
        lines = []
        col_header = "   " + "".join(f"  c{c} " for c in range(self.cols))
        lines.append(col_header)
        for r in range(self.rows + 1):
            h_line = [f"r{r} *"]
            for c in range(self.cols):
                h_idx = edge_to_index("H", r, c, self.rows, self.cols)
                drawn = (self.mask & (1 << h_idx)) != 0
                h_line.append("---*" if drawn else "   *")
            lines.append("".join(h_line))

            if r < self.rows:
                v_line = ["   "]
                for c in range(self.cols + 1):
                    v_idx = edge_to_index("V", r, c, self.rows, self.cols)
                    drawn = (self.mask & (1 << v_idx)) != 0
                    v_line.append("|" if drawn else " ")
                    if c < self.cols:
                        owner = self.box_owners.get((r, c))
                        sym = str(owner) if owner else " "
                        v_line.append(f" {sym} ")
                lines.append("".join(v_line))
        return "\n".join(lines)
