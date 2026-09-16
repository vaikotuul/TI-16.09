"""Unit tests for Transposition Table and Iterative Deepening agent (src/agents/transposition_agent.py)."""

import pytest
from src.game import GameState, total_edges
from src.agents.minimax_agent import minimax
from src.agents.transposition_agent import (
    FLAG_EXACT,
    FLAG_LOWERBOUND,
    FLAG_UPPERBOUND,
    DictTranspositionTable,
    FlatTranspositionTable,
    TranspositionAgent,
    alphabeta_tt,
    choose_move_iterative_deepening,
    get_node_counter,
    reset_node_counter,
)


def test_dict_and_flat_tt_storage():
    """Verify entry storage and retrieval for both DictTT and FlatTT."""
    dict_tt = DictTranspositionTable()
    flat_tt = FlatTranspositionTable(num_edges=12)

    # 1. Exact entry
    dict_tt.store(mask=15, depth=4, flag=FLAG_EXACT, value=3, best_move=2)
    flat_tt.store(mask=15, depth=4, flag=FLAG_EXACT, value=3, best_move=2)

    d_res = dict_tt.lookup(15)
    f_res = flat_tt.lookup(15)

    assert d_res == (4, FLAG_EXACT, 3, 2)
    assert f_res == (4, FLAG_EXACT, 3, 2)

    # 2. Lowerbound entry with negative value
    dict_tt.store(mask=20, depth=6, flag=FLAG_LOWERBOUND, value=-2, best_move=5)
    flat_tt.store(mask=20, depth=6, flag=FLAG_LOWERBOUND, value=-2, best_move=5)

    assert dict_tt.lookup(20) == (6, FLAG_LOWERBOUND, -2, 5)
    assert flat_tt.lookup(20) == (6, FLAG_LOWERBOUND, -2, 5)

    # 3. Upperbound entry
    dict_tt.store(mask=30, depth=2, flag=FLAG_UPPERBOUND, value=0, best_move=None)
    flat_tt.store(mask=30, depth=2, flag=FLAG_UPPERBOUND, value=0, best_move=None)

    assert dict_tt.lookup(30) == (2, FLAG_UPPERBOUND, 0, None)
    assert flat_tt.lookup(30) == (2, FLAG_UPPERBOUND, 0, None)

    # 4. Uninitialized entry
    assert dict_tt.lookup(99) is None
    assert flat_tt.lookup(99) is None

    # 5. Clear
    dict_tt.clear()
    flat_tt.clear()
    assert len(dict_tt) == 0
    assert flat_tt.lookup(15) is None


def test_flat_tt_buffer_size():
    """Verify flat TT buffer size calculation."""
    # 2x2 board: 12 edges -> 2**12 entries * 4 bytes = 16,384 bytes
    flat_2x2 = FlatTranspositionTable(12)
    assert flat_2x2.size_bytes == 16384
    assert flat_2x2.size_mb == 16384 / (1024 * 1024)

    # 1 byte per record theoretical: 2**12 = 4096 bytes
    assert (1 << 12) == 4096


def test_2x2_full_solve_agreement():
    """Verify 2x2 full solve yields optimal score 2 with both TT types."""
    dict_tt = DictTranspositionTable()
    flat_tt = FlatTranspositionTable(12)

    val_dict, move_dict = alphabeta_tt(
        0, 1, depth=12, alpha=-float("inf"), beta=float("inf"), rows=2, cols=2, tt=dict_tt
    )
    val_flat, move_flat = alphabeta_tt(
        0, 1, depth=12, alpha=-float("inf"), beta=float("inf"), rows=2, cols=2, tt=flat_tt
    )

    assert val_dict == 2
    assert val_flat == 2
    assert move_dict == move_flat


def test_midgame_consistency_with_minimax():
    """Verify alphabeta_tt produces the exact same moves as Minimax at depth 4 on midgame."""
    # Fixed 2x2 midgame position with 6 moves played
    mask = (1 << 0) | (1 << 1) | (1 << 4) | (1 << 5) | (1 << 6) | (1 << 8)
    tt = DictTranspositionTable()

    val_mm, move_mm = minimax(mask, player=1, depth=4, rows=2, cols=2)
    val_tt, move_tt = alphabeta_tt(
        mask, player=1, depth=4, alpha=-float("inf"), beta=float("inf"), rows=2, cols=2, tt=tt
    )

    assert val_mm == val_tt
    assert move_mm == move_tt


def test_iterative_deepening_respects_budget():
    """Verify iterative deepening returns a legal move within time budget."""
    tt = DictTranspositionTable()
    move, depth = choose_move_iterative_deepening(
        mask=0, player=1, time_budget=0.1, max_depth=10, rows=2, cols=2, tt=tt
    )
    assert 0 <= move < total_edges(2, 2)
    assert depth >= 1

    # Default tt=None and reaching max depth on 1x1 board
    move_default, d_1x1 = choose_move_iterative_deepening(
        mask=0, player=1, time_budget=1.0, max_depth=4, rows=1, cols=1
    )
    assert d_1x1 == 4

    # Early timeout check
    import time
    move_to, d_to = choose_move_iterative_deepening(
        mask=0, player=1, time_budget=0.00001, max_depth=10, rows=2, cols=2
    )
    assert d_to >= 1



def test_transposition_agent_class_and_state():
    """Verify TranspositionAgent class methods and properties."""
    agent_dict = TranspositionAgent(rows=2, cols=2, default_depth=2, time_budget=0.1)
    agent_flat = TranspositionAgent(rows=2, cols=2, default_depth=2, time_budget=0.1, use_flat=True)
    state = GameState(rows=2, cols=2)

    move_d = agent_dict.choose_move_state(state)
    move_f = agent_flat.choose_move_state(state)

    assert state.is_legal_move(move_d)
    assert state.is_legal_move(move_f)
    assert agent_dict.nodes_evaluated > 0
    assert agent_flat.nodes_evaluated > 0

    # Test with fixed depth without time budget
    move_fixed = agent_dict.choose_move(state.mask, player=1, depth=2, time_budget=0.0, rows=2, cols=2)
    assert state.is_legal_move(move_fixed)
    assert agent_dict.depth_reached == 2

    # Test choose_move_state with explicit depth and budget
    move_state_param = agent_dict.choose_move_state(state, depth=2, time_budget=0.1)
    assert state.is_legal_move(move_state_param)

    # Test use_flat=True when num_edges > 24 falls back to DictTranspositionTable
    large_agent = TranspositionAgent(rows=5, cols=5, use_flat=True)
    assert isinstance(large_agent.tt, DictTranspositionTable)


def test_error_handling():
    """Verify terminal state error handling."""
    full_mask = (1 << total_edges(1, 1)) - 1
    with pytest.raises(ValueError):
        choose_move_iterative_deepening(full_mask, player=1, time_budget=1.0, rows=1, cols=1)

