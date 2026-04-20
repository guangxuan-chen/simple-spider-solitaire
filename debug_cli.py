"""Interactive debug CLI for the Spider Solitaire core engine."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from spider_solitaire import (  # noqa: E402
    GameState,
    Move,
    apply_move,
    deal_stock,
    get_game_status,
    new_game,
)


def main() -> None:
    """Run a small interactive command loop for engine debugging."""
    state = new_game(seed=None)
    print("Spider debug CLI. Type `help` for commands.")
    _print_state(state)

    while True:
        try:
            raw = input("spider> ").strip()
        except EOFError:
            print()
            break

        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()

        if command in {"quit", "exit"}:
            break
        if command == "help":
            _print_help()
            continue
        if command == "show":
            _print_state(state)
            continue
        if command == "status":
            _print_status(state)
            continue
        if command == "new":
            state = _handle_new(parts)
            _print_state(state)
            continue
        if command == "deal":
            _handle_deal(state)
            continue
        if command == "move":
            _handle_move_by_start_index(parts, state)
            continue
        if command == "movec":
            _handle_move_by_card_count(parts, state)
            continue

        print("Unknown command. Type `help`.")


def _print_help() -> None:
    """Print supported commands."""
    print("Commands:")
    print("  show                         Show tableau, stock, and status")
    print("  status                       Show compact status only")
    print("  new [seed]                   Start a new game (optional seed)")
    print("  deal                         Deal one stock card to each column")
    print("  move <src> <dst> <start>     Move from source start index")
    print("  movec <src> <dst> <count>    Move last <count> cards from source")
    print("  help                         Show this help")
    print("  quit / exit                  Leave the CLI")


def _handle_new(parts: list[str]) -> GameState:
    """Create a new game using optional integer seed."""
    if len(parts) == 1:
        return new_game(seed=None)
    if len(parts) != 2:
        print("Usage: new [seed]")
        return new_game(seed=None)

    seed = _parse_int(parts[1], "seed")
    if seed is None:
        return new_game(seed=None)
    return new_game(seed=seed)


def _handle_deal(state: GameState) -> None:
    """Execute stock deal and print results."""
    try:
        deal_stock(state)
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    print("Stock deal applied.")
    _print_state(state)


def _handle_move_by_start_index(parts: list[str], state: GameState) -> None:
    """Execute move command using start index format."""
    if len(parts) != 4:
        print("Usage: move <src> <dst> <start_index>")
        return

    source = _parse_int(parts[1], "source column")
    destination = _parse_int(parts[2], "destination column")
    start_index = _parse_int(parts[3], "start index")
    if source is None or destination is None or start_index is None:
        return

    try:
        move = Move(
            source_column=source,
            destination_column=destination,
            start_index=start_index,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    result = apply_move(state, move)
    print(result.message)
    _print_state(state)


def _handle_move_by_card_count(parts: list[str], state: GameState) -> None:
    """Execute move command using card count format."""
    if len(parts) != 4:
        print("Usage: movec <src> <dst> <card_count>")
        return

    source = _parse_int(parts[1], "source column")
    destination = _parse_int(parts[2], "destination column")
    card_count = _parse_int(parts[3], "card count")
    if source is None or destination is None or card_count is None:
        return

    try:
        move = Move(
            source_column=source,
            destination_column=destination,
            card_count=card_count,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    result = apply_move(state, move)
    print(result.message)
    _print_state(state)


def _parse_int(raw: str, field_name: str) -> int | None:
    """Parse integer input and report user-facing parse failures."""
    try:
        return int(raw)
    except ValueError:
        print(f"Invalid {field_name}: `{raw}`")
        return None


def _print_status(state: GameState) -> None:
    """Print stock, completed sequence count, and win status."""
    print(
        "Status:",
        f"stock={len(state.stock)}",
        f"completed={state.completed_sequences}",
        f"game={get_game_status(state).value}",
    )


def _print_state(state: GameState) -> None:
    """Render all tableau columns plus compact status."""
    _print_status(state)
    print("Tableau:")
    for column_index, column in enumerate(state.tableau):
        cards = " ".join(_card_label(card) for card in column) or "(empty)"
        print(f"  {column_index}: {cards}")


def _card_label(card: object) -> str:
    """Render one card as face-down token or rank label."""
    rank_to_label = {
        1: "A",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
        11: "J",
        12: "Q",
        13: "K",
    }

    face_up = getattr(card, "face_up", False)
    if not face_up:
        return "XX"
    rank = getattr(card, "rank", None)
    return rank_to_label.get(int(rank), "?")


if __name__ == "__main__":
    main()
