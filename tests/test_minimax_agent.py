"""Unit tests for Minimax agent (src/agents/minimax_agent.py)."""

import pytest
from src.game import GameState, total_edges
from src.agents.minimax_agent import (
    MinimaxAgent,
    choose_move,
    get_node_counter,
    minimax,
    reset_node_counter,
)


def test_node_counter():
    """Verify node counter reset and incrementation."""
    reset_node_counter()
    assert get_node_counter() == 0

    # 1x1 board has 4 edges. Depth 1 search from empty board
    val, move = minimax(mask=0, player=1, depth=1, rows=1, cols=1)
    # Root + 4 children = 5 calls
    assert get_node_counter() == 5

    reset_node_counter()
    assert get_node_counter() == 0


def test_bonus_turn_fixed_2x2_game():
    """Verify full endgame search on a fixed 2x2 position.

    Catches the bonus turn sign error:
    If completing a box incorrectly negates score, the agent avoids completing
    boxes and blunders. With correct non-negating bonus turn logic, Player 1
    wins decisively 4-0.
    """
    # 2x2 board has 12 edges.
    # Pre-draw 6 outer edges: 0, 1, 4, 5, 6, 8
    # Remaining 6 edges: 2, 3, 7, 9, 10, 11
    start_mask = (1 << 0) | (1 << 1) | (1 << 4) | (1 << 5) | (1 << 6) | (1 << 8)
    state = GameState(rows=2, cols=2, mask=start_mask, current_player=1)

    agent = MinimaxAgent(rows=2, cols=2)

    # Play until terminal with depth = remaining moves (searching to game end)
    while not state.is_terminal():
        rem = len(state.legal_moves())
        move = agent.choose_move_state(state, depth=rem)
        state = state.make_move(move)

    assert state.is_terminal()
    assert state.winner() == 1
    assert state.scores[1] == 4
    assert state.scores[2] == 0


def test_immediate_box_completion():
    """Verify minimax prioritizes immediately capturing an open box."""
    # 1x1 board: edges 0, 1, 2 drawn, edge 3 completes the box
    mask = (1 << 0) | (1 << 1) | (1 << 2)
    best_move = choose_move(mask, player=1, depth=2, rows=1, cols=1)
    assert best_move == 3


def test_agent_class_and_state_interface():
    """Verify MinimaxAgent class methods and properties."""
    agent = MinimaxAgent(rows=2, cols=2, default_depth=2)
    state = GameState(rows=2, cols=2)

    move = agent.choose_move_state(state)
    assert state.is_legal_move(move)
    assert agent.nodes_evaluated > 0

    # Explicit depth override
    move2 = agent.choose_move(state.mask, player=1, depth=1)
    assert state.is_legal_move(move2)


def test_error_handling():
    """Verify error conditions for choose_move."""
    # Invalid depth < 1
    with pytest.raises(ValueError):
        choose_move(mask=0, player=1, depth=0, rows=1, cols=1)

    # Terminal state (all edges drawn)
    full_mask = (1 << total_edges(1, 1)) - 1
    with pytest.raises(ValueError):
        choose_move(mask=full_mask, player=1, depth=2, rows=1, cols=1)


def test_cli_integration_with_minimax():
    """Verify CLI simulation using MinimaxAgent."""
    from unittest.mock import patch
    from src.cli import run_game

    agent = MinimaxAgent(rows=1, cols=1, default_depth=2)
    with patch("builtins.input", side_effect=["0", "1", "2", "3"]):
        run_game(rows=1, cols=1, human_player=1, agent=agent)

