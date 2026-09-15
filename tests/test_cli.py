"""Unit tests for CLI interface (src/cli.py)."""

from unittest.mock import patch
import pytest
from src.game import GameState
from src.cli import parse_move, prompt_human_move, print_status, run_game, main


def test_parse_move_integer():
    """Test integer move parsing."""
    state = GameState(rows=2, cols=2)
    assert parse_move("0", state) == 0
    assert parse_move("11", state) == 11
    # Out of range / already drawn
    assert parse_move("12", state) is None
    s2 = state.make_move(0)
    assert parse_move("0", s2) is None


def test_parse_move_coordinates():
    """Test coordinate move parsing (H r c, V r c)."""
    state = GameState(rows=2, cols=2)
    # H 0 0 -> index 0
    assert parse_move("H 0 0", state) == 0
    # h 0, 1 -> index 1
    assert parse_move("h 0, 1", state) == 1
    # V 0 0 -> index 6
    assert parse_move("V 0 0", state) == 6
    # v 1 2 -> index 11
    assert parse_move("v 1 2", state) == 11
    # Invalid coordinates
    assert parse_move("H 5 0", state) is None
    assert parse_move("invalid input", state) is None
    assert parse_move("", state) is None


def test_prompt_human_move():
    """Test user prompt retry logic and exit."""
    state = GameState(rows=1, cols=1)
    with patch("builtins.input", side_effect=["invalid", "0"]):
        move = prompt_human_move(state)
        assert move == 0

    with patch("builtins.input", side_effect=["q"]):
        with pytest.raises(SystemExit):
            prompt_human_move(state)


def test_print_status(capsys):
    """Test print_status output."""
    state = GameState(rows=1, cols=1)
    print_status(state)
    captured = capsys.readouterr()
    assert "Scores -> Player 1: 0 | Player 2: 0" in captured.out
    assert "Current turn: Player 1" in captured.out


def test_run_game_simulation():
    """Test a short full game run using simulated human moves."""
    # 1x1 board has 4 edges: 0, 1, 2, 3
    with patch("builtins.input", side_effect=["0", "1", "2", "3"]):
        run_game(rows=1, cols=1, human_player=1)


def test_main_cli_entry():
    """Test main function handling default inputs and exit."""
    with patch("builtins.input", side_effect=["1 1", "Y", "0", "1", "2", "3"]):
        main()

    with patch("builtins.input", side_effect=KeyboardInterrupt):
        main()
