"""CLI interface for Dots and Boxes (Punktid ja Kastid)."""

import sys
from typing import Optional
from src.game import GameState, edge_to_index, index_to_edge
from src.agents.random_agent import RandomAgent


def parse_move(user_input: str, state: GameState) -> Optional[int]:
    """Parse user move from integer index or coordinate format like 'H 0 1'."""
    raw = user_input.strip()
    if not raw:
        return None

    # Option 1: single integer index
    if raw.isdigit():
        idx = int(raw)
        if state.is_legal_move(idx):
            return idx
        print(f"Index {idx} is already drawn or out of range.")
        return None

    # Option 2: 'H r c' or 'V r c'
    parts = raw.replace(",", " ").split()
    if len(parts) == 3 and parts[0].upper() in ("H", "V"):
        edge_type = parts[0].upper()
        if parts[1].isdigit() and parts[2].isdigit():
            r, c = int(parts[1]), int(parts[2])
            try:
                idx = edge_to_index(edge_type, r, c, state.rows, state.cols)
                if state.is_legal_move(idx):
                    return idx
                print(f"Edge {edge_type}({r}, {c}) (index {idx}) is already drawn.")
                return None
            except ValueError as err:
                print(f"Invalid coordinates: {err}")
                return None

    print("Unknown format. Enter edge index (e.g. '5') or format 'H 0 1' / 'V 1 2'.")
    return None


def prompt_human_move(state: GameState) -> int:
    """Prompt user until a valid move or exit command is given."""
    while True:
        try:
            line = input(f"Player {state.current_player} move (or 'q' to quit): ")
        except (EOFError, KeyboardInterrupt):
            print("\nGame aborted.")
            sys.exit(0)

        if line.strip().lower() in ("q", "quit", "exit"):
            print("Exiting game.")
            sys.exit(0)

        move = parse_move(line, state)
        if move is not None:
            return move


def print_status(state: GameState) -> None:
    """Display the current board, scores, and whose turn it is."""
    print("\n" + "=" * 32)
    print(f"Scores -> Player 1: {state.scores[1]} | Player 2: {state.scores[2]}")
    print(f"Current turn: Player {state.current_player}")
    print("-" * 32)
    print(state.render())
    print("=" * 32)


def run_game(rows: int = 3, cols: int = 3, human_player: int = 1) -> None:
    """Run full interactive game between human and random agent."""
    state = GameState(rows=rows, cols=cols)
    agent = RandomAgent()

    print(f"\nStarting Dots & Boxes ({rows}x{cols} boxes).")
    print(f"You are Player {human_player}. Agent is Player {3 - human_player}.")
    print("Input moves as 'H r c', 'V r c' or edge index (0..N).")

    while not state.is_terminal():
        print_status(state)
        curr = state.current_player
        old_scores = dict(state.scores)

        if curr == human_player:
            move = prompt_human_move(state)
        else:
            move = agent.choose_move_state(state)
            kind, r, c = index_to_edge(move, state.rows, state.cols)
            print(f"Agent chose edge {move} ({kind} row={r}, col={c})")

        state = state.make_move(move)
        gained = state.scores[curr] - old_scores[curr]
        if gained > 0:
            plural = "boxes" if gained > 1 else "box"
            print(f"-> Player {curr} completed {gained} {plural} and gets a bonus turn!")

    # Terminal state
    print_status(state)
    winner = state.winner()
    print("\n*** GAME OVER ***")
    print(f"Final score: Player 1: {state.scores[1]} | Player 2: {state.scores[2]}")
    if winner == 0:
        print("Result: It's a Tie!")
    elif winner == human_player:
        print("Congratulations! You won!")
    else:
        print("Agent won! Better luck next time.")


def main() -> None:
    """CLI entry point with option setup."""
    print("=== Dots and Boxes (Punktid ja Kastid) ===")
    try:
        size_str = input("Enter board size (rows cols) [default 3 3]: ").strip()
        if size_str:
            parts = size_str.split()
            r, c = int(parts[0]), int(parts[1]) if len(parts) > 1 else int(parts[0])
        else:
            r, c = 3, 3

        order_str = input("Do you want to play first? (Y/n) [default Y]: ").strip().lower()
        human_player = 2 if order_str == "n" else 1
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        return
    except Exception:
        r, c, human_player = 3, 3, 1

    run_game(rows=r, cols=c, human_player=human_player)


if __name__ == "__main__":
    main()
