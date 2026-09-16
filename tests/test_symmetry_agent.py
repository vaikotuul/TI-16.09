"""Unit tests for Symmetry Canonicalization Agent (src/agents/symmetry_agent.py)."""

import pytest
from src.game import GameState, total_edges
from src.agents.minimax_agent import minimax
from src.agents.symmetry_agent import (
    DictTranspositionTable,
    FlatTranspositionTable,
    SymmetryAgent,
    alphabeta_sym,
    canonicalize_mask,
    choose_move,
    get_node_counter,
    get_symmetry_permutations,
    reset_node_counter,
)


def test_symmetry_permutations_properties():
    """Verify symmetry permutation counts and bijection properties."""
    # Square boards: 8 symmetries (D4)
    perms_2x2 = get_symmetry_permutations(2, 2)
    assert len(perms_2x2) == 8
    for p in perms_2x2:
        assert sorted(p) == list(range(12))

    perms_3x3 = get_symmetry_permutations(3, 3)
    assert len(perms_3x3) == 8
    for p in perms_3x3:
        assert sorted(p) == list(range(24))

    # Rectangular boards: 4 symmetries (Identity, FlipH, FlipV, Rot180)
    perms_2x3 = get_symmetry_permutations(2, 3)
    assert len(perms_2x3) == 4
    for p in perms_2x3:
        assert sorted(p) == list(range(17))


def test_canonicalization_and_evaluation_invariance():
    """Construct position and its rotated/reflected counterpart.

    Verify both canonicalize to identical keys and evaluate to equal values.
    """
    perms = get_symmetry_permutations(2, 2)

    # State 1: edge 0 (top-left horizontal) is drawn
    mask1 = 1 << 0
    # State 2: 90-degree CW rotation of edge 0 (maps to right vertical of col 2)
    rot90_perm = perms[4]
    mask2 = 1 << rot90_perm[0]

    c1 = canonicalize_mask(mask1, 2, 2)
    c2 = canonicalize_mask(mask2, 2, 2)
    assert c1 == c2

    # Verify both positions evaluate to identical values
    tt1 = DictTranspositionTable()
    tt2 = DictTranspositionTable()
    val1, _ = alphabeta_sym(mask1, 1, depth=6, alpha=-float("inf"), beta=float("inf"), rows=2, cols=2, tt=tt1)
    val2, _ = alphabeta_sym(mask2, 1, depth=6, alpha=-float("inf"), beta=float("inf"), rows=2, cols=2, tt=tt2)
    assert val1 == val2


def test_stage4_consistency_on_midgame():
    """Verify symmetry agent selects the exact same moves as Minimax and Alpha-Beta."""
    # 2x2 midgame position with 6 moves played
    mask = (1 << 0) | (1 << 1) | (1 << 4) | (1 << 5) | (1 << 6) | (1 << 8)
    tt = DictTranspositionTable()

    val_mm, move_mm = minimax(mask, player=1, depth=4, rows=2, cols=2)
    val_sym, move_sym = alphabeta_sym(
        mask, player=1, depth=4, alpha=-float("inf"), beta=float("inf"), rows=2, cols=2, tt=tt
    )

    assert val_sym == val_mm
    assert move_sym == move_mm


def test_symmetry_agent_class_and_state():
    """Verify SymmetryAgent methods, flat table option, and state methods."""
    agent_dict = SymmetryAgent(rows=2, cols=2, default_depth=2)
    agent_flat = SymmetryAgent(rows=2, cols=2, default_depth=2, use_flat=True)
    state = GameState(rows=2, cols=2)

    move_d = agent_dict.choose_move_state(state)
    move_f = agent_flat.choose_move_state(state)

    assert state.is_legal_move(move_d)
    assert state.is_legal_move(move_f)
    assert agent_dict.nodes_evaluated > 0
    assert agent_flat.nodes_evaluated > 0

    # Depth override and explicit rows/cols
    move_explicit = agent_dict.choose_move(state.mask, player=1, depth=1, rows=2, cols=2)
    assert state.is_legal_move(move_explicit)

    # Test choose_move with tt=None default
    move_no_tt = choose_move(state.mask, player=1, depth=1, rows=2, cols=2, tt=None)
    assert state.is_legal_move(move_no_tt)

    # Test use_flat=True fallback when num_edges > 24
    large_agent = SymmetryAgent(rows=5, cols=5, use_flat=True)
    assert isinstance(large_agent.tt, DictTranspositionTable)



def test_error_handling():
    """Verify invalid depth and terminal state raise ValueError."""
    with pytest.raises(ValueError):
        choose_move(mask=0, player=1, depth=0, rows=1, cols=1)

    full_mask = (1 << total_edges(1, 1)) - 1
    with pytest.raises(ValueError):
        choose_move(mask=full_mask, player=1, depth=2, rows=1, cols=1)
