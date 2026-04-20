"""Minimal command-line interface for the Spider Solitaire engine."""

from __future__ import annotations

from dataclasses import dataclass

from .engine import (
    Card,
    GameState,
    Move,
    apply_move,
    deal_stock,
    get_game_status,
    new_game,
)


@dataclass(slots=True, frozen=True)
class CommandOutcome:
    """Result metadata for one parsed CLI command."""

    messages: tuple[str, ...] = ()
    show_state: bool = False
    should_quit: bool = False


def run_cli() -> None:
    """Start an interactive game loop for manual engine interaction."""
    state = new_game(seed=None)
    print("Spider CLI. Type `help` for commands.")
    print(render_state(state))

    while True:
        try:
            raw = input("spider> ")
        except EOFError:
            print()
            break

        state, outcome = handle_command(state, raw)
        for message in outcome.messages:
            print(message)
        if outcome.show_state:
            print(render_state(state))
        if outcome.should_quit:
            break


def handle_command(
    state: GameState, raw: str
) -> tuple[GameState, CommandOutcome]:
    """Parse one command line, call engine APIs, and return UI outcomes."""
    parts = raw.strip().split()
    if not parts:
        return state, CommandOutcome()

    command = parts[0].lower()

    if command == "help":
        return state, CommandOutcome(messages=(help_text(),))
    if command == "show":
        return state, CommandOutcome(show_state=True)
    if command == "quit":
        return state, CommandOutcome(should_quit=True)
    if command == "new":
        return _handle_new(parts)
    if command == "deal":
        return _handle_deal(state, parts)
    if command == "move":
        return _handle_move(state, parts)
    if command == "movec":
        return _handle_movec(state, parts)

    return state, CommandOutcome(messages=("Unknown command. Type `help`.",))


def help_text() -> str:
    """Return the supported command summary."""
    return (
        "Commands:\n"
        "  show                         Show tableau and status\n"
        "  move <src> <dst> <start>     Move cards from source start index\n"
        "  movec <src> <dst> <count>    Move last <count> cards from source\n"
        "  deal                         Deal one card to each tableau column\n"
        "  new [seed]                   Start a new game (optional seed)\n"
        "  help                         Show this help\n"
        "  quit                         Exit the CLI"
    )


def render_state(state: GameState) -> str:
    """Render stock/completion status and all tableau columns."""
    lines = [
        (
            "Status: "
            f"stock={len(state.stock)} "
            f"completed={state.completed_sequences} "
            f"game={get_game_status(state).value}"
        ),
        "Tableau:",
    ]

    for column_index, column in enumerate(state.tableau):
        cards = " ".join(_card_label(card) for card in column) or "(empty)"
        lines.append(f"  {column_index}: {cards}")
    return "\n".join(lines)


def _handle_new(parts: list[str]) -> tuple[GameState, CommandOutcome]:
    """Handle `new [seed]` command and return replacement state."""
    if len(parts) == 1:
        state = new_game(seed=None)
        return state, CommandOutcome(
            messages=("Started a new game.",), show_state=True
        )

    if len(parts) != 2:
        state = new_game(seed=None)
        return state, CommandOutcome(
            messages=("Usage: new [seed]", "Started a new game without seed."),
            show_state=True,
        )

    seed = _parse_int(parts[1], "seed")
    if seed is None:
        state = new_game(seed=None)
        return state, CommandOutcome(
            messages=("Started a new game without seed.",),
            show_state=True,
        )

    state = new_game(seed=seed)
    return state, CommandOutcome(
        messages=(f"Started a new game with seed={seed}.",),
        show_state=True,
    )


def _handle_deal(
    state: GameState, parts: list[str]
) -> tuple[GameState, CommandOutcome]:
    """Handle `deal` command and propagate user-facing status."""
    if len(parts) != 1:
        return state, CommandOutcome(messages=("Usage: deal",))

    try:
        deal_stock(state)
    except ValueError as exc:
        return state, CommandOutcome(messages=(f"Invalid action: {exc}",))

    return state, CommandOutcome(
        messages=("Stock deal applied.",),
        show_state=True,
    )


def _handle_move(
    state: GameState, parts: list[str]
) -> tuple[GameState, CommandOutcome]:
    """Handle `move <src> <dst> <start_index>` command."""
    if len(parts) != 4:
        return state, CommandOutcome(
            messages=("Usage: move <src> <dst> <start>",)
        )

    source = _parse_int(parts[1], "source column")
    destination = _parse_int(parts[2], "destination column")
    start_index = _parse_int(parts[3], "start index")
    if source is None or destination is None or start_index is None:
        return state, CommandOutcome()

    try:
        move = Move(
            source_column=source,
            destination_column=destination,
            start_index=start_index,
        )
    except ValueError as exc:
        return state, CommandOutcome(messages=(f"Invalid move input: {exc}",))

    result = apply_move(state, move)
    if result.success:
        return state, CommandOutcome(
            messages=(result.message,), show_state=True
        )
    return state, CommandOutcome(
        messages=(f"Invalid action: {result.message}",)
    )


def _handle_movec(
    state: GameState, parts: list[str]
) -> tuple[GameState, CommandOutcome]:
    """Handle `movec <src> <dst> <card_count>` command."""
    if len(parts) != 4:
        return state, CommandOutcome(
            messages=("Usage: movec <src> <dst> <count>",)
        )

    source = _parse_int(parts[1], "source column")
    destination = _parse_int(parts[2], "destination column")
    card_count = _parse_int(parts[3], "card count")
    if source is None or destination is None or card_count is None:
        return state, CommandOutcome()

    try:
        move = Move(
            source_column=source,
            destination_column=destination,
            card_count=card_count,
        )
    except ValueError as exc:
        return state, CommandOutcome(messages=(f"Invalid move input: {exc}",))

    result = apply_move(state, move)
    if result.success:
        return state, CommandOutcome(
            messages=(result.message,), show_state=True
        )
    return state, CommandOutcome(
        messages=(f"Invalid action: {result.message}",)
    )


def _parse_int(raw: str, field_name: str) -> int | None:
    """Parse integer arguments and produce friendly parse errors."""
    try:
        return int(raw)
    except ValueError:
        print(f"Invalid {field_name}: `{raw}`")
        return None


def _card_label(card: Card) -> str:
    """Render one card token for CLI display."""
    if not card.face_up:
        return "XX"

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
    return rank_to_label.get(int(card.rank), "?")
