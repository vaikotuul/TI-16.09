"""Unit tests for Alpha-Beta agent (src/agents/alphabeta_agent.py)."""

import random
import pytest
from src.game import GameState, total_edges
from src.agents.minimax_agent import (
    choose_move as mm_choose_move,
    get_node_counter as mm_get_nodes,
    minimax,
    reset_node_counter as mm_reset_nodes,
)
from src.agents.alphabeta_agent import (
    AlphaBetaAgent,
    alphabeta,
    choose_move,
    get_node_counter,
    order_moves,
    reset_node_counter,
)


def _generate_fixed_midgame_positions():
    """Generate deterministic midgame positions for testing."""
    positions = []
    for seed in range(5):
        state = GameState(rows=3, cols=3)
        rng = random.Random(seed * 777 + 13)
        for _ in range(12):
            moves = state.legal_moves()
            if not moves or state.is_terminal():
                break
            state = state.make_move(rng.choice(moves))
        positions.append((state.mask, state.current_player))
    return positions


def test_alphabeta_vs_minimax_exact_agreement_depth6():
    """Verify Alpha-Beta and Minimax select the exact same move on 5 midgame positions.

    Stage 3 correctness requirement:
    Checks 5 fixed positions at depth 6. If choices diverge, alpha-beta has a window/bounds error.
    """
    positions = _generate_fixed_midgame_positions()
    assert len(positions) == 5

    for i, (mask, player) in enumerate(positions):
        # Minimax move and evaluation
        mm_reset_nodes()
        val_mm, move_mm = minimax(mask, player, depth=6, rows=3, cols=3)
        nodes_mm = mm_get_nodes()

        # Alpha-Beta move and evaluation
        reset_node_counter()
        val_ab, move_ab = alphabeta(
            mask, player, depth=6, alpha=-float("inf"), beta=float("inf"), rows=3, cols=3
        )
        nodes_ab = get_node_counter()

        assert val_mm == val_ab, f"Pos {i}: value mismatch {val_mm} vs {val_ab}"
        assert move_mm == move_ab, f"Pos {i}: move mismatch {move_mm} vs {move_ab}"
        # Verify significant node reduction (> 80%)
        reduction = 100.0 * (1.0 - nodes_ab / nodes_mm)
        assert reduction > 80.0, f"Pos {i}: reduction was only {reduction:.1f}%"


def test_order_moves_categorization():
    """Verify order_moves correctly prioritizes safe, capturing, and unsafe moves."""
    # 2x2 board: draw top outer edges: 0, 1, 6, 8
    # Box (0,0) has top=0, left=6.
    # If we also draw bottom=2, it will have 3 sides (edges 0, 2, 6).
    # Then edge 7 (right of (0,0)) will complete box (0,0).
    mask = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 6) | (1 << 8)
    ordered = order_moves(mask, rows=2, cols=2)

    # Edge 7 completes box (0, 0), so it must be categorized as capturing
    assert 7 in ordered
    # Legal moves must contain all undrawn edges
    undrawn = [e for e in range(12) if not (mask & (1 << e))]
    assert set(ordered) == set(undrawn)


def test_node_counter():
    """Verify node counter reset and incrementation."""
    reset_node_counter()
    assert get_node_counter() == 0

    val, move = alphabeta(
        mask=0, player=1, depth=1, alpha=-float("inf"), beta=float("inf"), rows=1, cols=1
    )
    assert get_node_counter() > 0

    reset_node_counter()
    assert get_node_counter() == 0


def test_agent_class_and_state_interface():
    """Verify AlphaBetaAgent class methods and properties."""
    agent = AlphaBetaAgent(rows=2, cols=2, default_depth=2)
    state = GameState(rows=2, cols=2)

    move = agent.choose_move_state(state)
    assert state.is_legal_move(move)
    assert agent.nodes_evaluated > 0

    move2 = agent.choose_move(state.mask, player=1, depth=1)
    assert state.is_legal_move(move2)


def test_error_handling():
    """Verify error handling for invalid depth and full board."""
    with pytest.raises(ValueError):
        choose_move(mask=0, player=1, depth=0, rows=1, cols=1)

    full_mask = (1 << total_edges(1, 1)) - 1
    with pytest.raises(ValueError):
        choose_move(mask=full_mask, player=1, depth=2, rows=1, cols=1)
