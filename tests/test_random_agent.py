"""Unit tests for RandomAgent (src/agents/random_agent.py)."""

import pytest
from src.game import GameState, total_edges
from src.agents.random_agent import RandomAgent, choose_move


def test_random_agent_picks_legal_move():
    """Verify that random agent always chooses undrawn legal moves."""
    agent = RandomAgent(seed=42)
    state = GameState(rows=2, cols=2)

    move = agent.choose_move_state(state)
    assert state.is_legal_move(move)

    # Test directly with mask
    mask = (1 << 0) | (1 << 1)
    chosen = agent.choose_move(mask, 2, 2)
    assert chosen in range(2, 12)
    assert (mask & (1 << chosen)) == 0


def test_random_agent_full_board_raises():
    """Verify error when no legal moves remain."""
    agent = RandomAgent()
    tot = total_edges(2, 2)
    full_mask = (1 << tot) - 1

    with pytest.raises(ValueError):
        choose_move(full_mask, 2, 2)


def test_random_agent_self_play_to_completion():
    """Play full games between two random agents to verify termination."""
    for seed in range(5):
        agent = RandomAgent(seed=seed)
        state = GameState(rows=2, cols=2)
        step_count = 0

        while not state.is_terminal():
            step_count += 1
            move = agent.choose_move_state(state)
            state = state.make_move(move)
            assert step_count <= 100  # Guard against infinite loops

        assert state.is_terminal()
        assert sum(state.scores.values()) == 4
        assert state.winner() in (0, 1, 2)
