"""Unit tests for Dots and Boxes core engine (src/game.py)."""

import pytest
from src.game import (
    GameState,
    box_edges,
    boxes_completed_by_edge,
    completed_boxes_by_edge,
    edge_boxes,
    edge_to_index,
    index_to_edge,
    num_horizontal_edges,
    num_vertical_edges,
    total_edges,
)


def test_edge_counts():
    """Verify edge count formulas for various board dimensions."""
    # 1x1 board: 1 box -> 2 H edges, 2 V edges -> 4 total
    assert num_horizontal_edges(1, 1) == 2
    assert num_vertical_edges(1, 1) == 2
    assert total_edges(1, 1) == 4

    # 2x2 board: 4 boxes -> 6 H, 6 V -> 12 total
    assert num_horizontal_edges(2, 2) == 6
    assert num_vertical_edges(2, 2) == 6
    assert total_edges(2, 2) == 12

    # 3x3 board: 9 boxes -> 12 H, 12 V -> 24 total
    assert num_horizontal_edges(3, 3) == 12
    assert num_vertical_edges(3, 3) == 12
    assert total_edges(3, 3) == 24

    # 2x3 board (rectangular)
    assert num_horizontal_edges(2, 3) == 9
    assert num_vertical_edges(2, 3) == 8
    assert total_edges(2, 3) == 17


def test_indexing_bijection():
    """Verify bidirectional bijection between coordinates and stable indices."""
    for rows, cols in [(1, 1), (2, 2), (2, 3), (3, 3)]:
        tot = total_edges(rows, cols)
        seen_indices = set()

        for idx in range(tot):
            kind, r, c = index_to_edge(idx, rows, cols)
            roundtrip_idx = edge_to_index(kind, r, c, rows, cols)
            assert roundtrip_idx == idx
            seen_indices.add(idx)

        assert len(seen_indices) == tot


def test_indexing_errors():
    """Verify edge cases and invalid coordinates raise ValueError."""
    with pytest.raises(ValueError):
        edge_to_index("X", 0, 0, 2, 2)
    with pytest.raises(ValueError):
        edge_to_index("H", 3, 0, 2, 2)  # r out of bounds (max is rows=2)
    with pytest.raises(ValueError):
        edge_to_index("V", 0, 3, 2, 2)  # c out of bounds (max is cols=2)
    with pytest.raises(ValueError):
        index_to_edge(12, 2, 2)  # index >= total 12
    with pytest.raises(ValueError):
        index_to_edge(-1, 2, 2)


def test_box_edges_and_edge_boxes():
    """Verify box edges relation and adjacent boxes."""
    # 2x2 board
    # Box (0, 0) edges:
    # top: H(0, 0) = 0
    # bottom: H(1, 0) = 2
    # left: V(0, 0) = 6
    # right: V(0, 1) = 7
    top, bottom, left, right = box_edges(0, 0, 2, 2)
    assert (top, bottom, left, right) == (0, 2, 6, 7)

    # Edge 2 is H(1, 0), internal between box (0, 0) and box (1, 0)
    adj = edge_boxes(2, 2, 2)
    assert sorted(adj) == [(0, 0), (1, 0)]

    # Edge 0 is H(0, 0), boundary touching only (0, 0)
    adj_boundary = edge_boxes(0, 2, 2)
    assert adj_boundary == [(0, 0)]


def test_boxes_completed_single_box():
    """Verify completing a single box gives count=1 and correct coordinates."""
    # 1x1 board: box edges are 0, 1 (H) and 2, 3 (V)
    # Draw edges 0, 1, 2 first
    mask = (1 << 0) | (1 << 1) | (1 << 2)
    assert boxes_completed_by_edge(mask, 3, 1, 1) == 1
    assert completed_boxes_by_edge(mask, 3, 1, 1) == [(0, 0)]

    # If only 2 edges drawn, drawing a 3rd edge completes 0 boxes
    partial_mask = (1 << 0) | (1 << 1)
    assert boxes_completed_by_edge(partial_mask, 2, 1, 1) == 0


def test_boxes_completed_double_box():
    """Verify an internal edge can complete two boxes at once."""
    # 2x1 board (2 rows, 1 col): Box (0, 0) and Box (1, 0)
    # Box (0, 0): H(0, 0)=0, H(1, 0)=1, V(0, 0)=3, V(0, 1)=4
    # Box (1, 0): H(1, 0)=1, H(2, 0)=2, V(1, 0)=5, V(1, 1)=6
    # Shared edge is H(1, 0) = index 1
    # Pre-draw the outer 6 edges: 0, 2, 3, 4, 5, 6
    mask = (1 << 0) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 6)
    shared_edge = edge_to_index("H", 1, 0, 2, 1)
    assert shared_edge == 1

    completed = completed_boxes_by_edge(mask, shared_edge, 2, 1)
    assert sorted(completed) == [(0, 0), (1, 0)]
    assert boxes_completed_by_edge(mask, shared_edge, 2, 1) == 2


def test_turn_rules_and_bonus():
    """Verify turn passing and bonus move logic."""
    state = GameState(rows=1, cols=1)
    assert state.current_player == 1
    assert len(state.legal_moves()) == 4

    # P1 moves edge 0 (no box completed) -> P2's turn
    s1 = state.make_move(0)
    assert s1.current_player == 2
    assert s1.scores == {1: 0, 2: 0}

    # P2 moves edge 1 (no box completed) -> P1's turn
    s2 = s1.make_move(1)
    assert s2.current_player == 1
    assert s2.scores == {1: 0, 2: 0}

    # P1 moves edge 2 (no box completed) -> P2's turn
    s3 = s2.make_move(2)
    assert s3.current_player == 2
    assert s3.scores == {1: 0, 2: 0}

    # P2 moves edge 3 (completes box (0, 0)) -> P2 gets bonus turn!
    s4 = s3.make_move(3)
    assert s4.scores == {1: 0, 2: 1}
    assert s4.box_owners[(0, 0)] == 2
    assert s4.is_terminal()
    assert s4.winner() == 2


def test_winner_tie():
    """Verify tie detection on 2x2 board (4 boxes total, 2-2 split)."""
    # 2x2 board: P1 gets 2 boxes, P2 gets 2 boxes
    state = GameState(
        rows=2,
        cols=2,
        mask=(1 << 12) - 1,
        current_player=1,
        scores={1: 2, 2: 2},
        box_owners={(0, 0): 1, (0, 1): 1, (1, 0): 2, (1, 1): 2},
    )
    assert state.is_terminal()
    assert state.winner() == 0


def test_render():
    """Verify board rendering includes points, lines and owners."""
    state = GameState(rows=1, cols=1)
    rendered = state.render()
    assert "r0 *" in rendered
    assert "r1 *" in rendered

    # Draw top edge and right edge
    top = edge_to_index("H", 0, 0, 1, 1)
    s1 = state.make_move(top)
    assert "---*" in s1.render()


def test_game_additional_coverage():
    """Test box_edges bounds, illegal move, and non-terminal winner."""
    with pytest.raises(ValueError):
        box_edges(-1, 0, 2, 2)
    with pytest.raises(ValueError):
        box_edges(2, 2, 2, 2)

    state = GameState(rows=1, cols=1)
    assert state.winner() is None

    with pytest.raises(ValueError):
        state.make_move(99)

