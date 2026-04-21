"""Minimal command-line interface for the Spider Solitaire engine."""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass

from .engine import (
    WIN_COMPLETED_SEQUENCES,
    Card,
    GameState,
    GameStatus,
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
    move_applied: bool = False
    deal_applied: bool = False
    invalid_command: bool = False
    new_game_started: bool = False
    new_game_seed: int | None = None


@dataclass(slots=True)
class SessionStats:
    """Mutable stats for one CLI gameplay session."""

    started_at: float
    move_count: int = 0
    deal_count: int = 0
    invalid_count: int = 0


def run_cli() -> None:
    """Start an interactive game loop for manual engine interaction."""
    state = new_game(seed=None)
    current_seed: int | None = None
    stats = SessionStats(started_at=time.monotonic())
    use_color = _should_use_color()

    print("Spider CLI. Type `help` for commands.")
    print(render_state(state))

    while True:
        try:
            raw = input("spider> ").strip()
        except EOFError:
            print()
            break

        state, stats, quick_action, current_seed = _handle_won_shortcuts(
            state=state,
            stats=stats,
            raw=raw,
            current_seed=current_seed,
        )
        if quick_action:
            break
        if quick_action is None:
            continue

        state, outcome = handle_command(state, raw)

        if outcome.new_game_started:
            current_seed = outcome.new_game_seed
            stats = SessionStats(started_at=time.monotonic())
        if outcome.move_applied:
            stats.move_count += 1
        if outcome.deal_applied:
            stats.deal_count += 1
        if outcome.invalid_command:
            stats.invalid_count += 1

        for message in outcome.messages:
            print(message)
        if outcome.show_state:
            output = render_state(state)
            if get_game_status(state) == GameStatus.WON:
                output += "\n" + render_won_panel(
                    state=state,
                    stats=stats,
                    seed=current_seed,
                    use_color=use_color,
                )
            print(output)
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
    if command in {"quit", "exit"}:
        return state, CommandOutcome(should_quit=True)
    if command == "new":
        return _handle_new(parts)
    if command == "deal":
        return _handle_deal(state, parts)
    if command == "move":
        return _handle_move(state, parts)
    if command == "movec":
        return _handle_movec(state, parts)

    return state, CommandOutcome(
        messages=("Unknown command. Type `help`.",),
        invalid_command=True,
    )


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
        "  quit                         Exit the CLI\n"
        "When won:\n"
        "  n                            Start a new random game\n"
        "  s                            Restart with the same seed\n"
        "  q                            Quit immediately"
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
            messages=("Started a new game.",),
            show_state=True,
            new_game_started=True,
        )

    if len(parts) != 2:
        state = new_game(seed=None)
        return state, CommandOutcome(
            messages=("Usage: new [seed]", "Started a new game without seed."),
            show_state=True,
            invalid_command=True,
            new_game_started=True,
        )

    seed, parse_error = _parse_int(parts[1], "seed")
    if parse_error is not None:
        state = new_game(seed=None)
        return state, CommandOutcome(
            messages=(
                parse_error,
                "Started a new game without seed.",
            ),
            show_state=True,
            invalid_command=True,
            new_game_started=True,
        )

    state = new_game(seed=seed)
    return state, CommandOutcome(
        messages=(f"Started a new game with seed={seed}.",),
        show_state=True,
        new_game_started=True,
        new_game_seed=seed,
    )


def _handle_deal(
    state: GameState, parts: list[str]
) -> tuple[GameState, CommandOutcome]:
    """Handle `deal` command and propagate user-facing status."""
    if len(parts) != 1:
        return state, CommandOutcome(
            messages=("Usage: deal",),
            invalid_command=True,
        )

    try:
        deal_stock(state)
    except ValueError as exc:
        return state, CommandOutcome(
            messages=(f"Invalid action: {exc}",),
            invalid_command=True,
        )

    return state, CommandOutcome(
        messages=("Stock deal applied.",),
        show_state=True,
        deal_applied=True,
    )


def _handle_move(
    state: GameState, parts: list[str]
) -> tuple[GameState, CommandOutcome]:
    """Handle `move <src> <dst> <start_index>` command."""
    if len(parts) != 4:
        return state, CommandOutcome(
            messages=("Usage: move <src> <dst> <start>",),
            invalid_command=True,
        )

    source, source_error = _parse_int(parts[1], "source column")
    if source_error is not None:
        return state, CommandOutcome(
            messages=(source_error,),
            invalid_command=True,
        )
    destination, destination_error = _parse_int(parts[2], "destination column")
    if destination_error is not None:
        return state, CommandOutcome(
            messages=(destination_error,),
            invalid_command=True,
        )
    start_index, start_error = _parse_int(parts[3], "start index")
    if start_error is not None:
        return state, CommandOutcome(
            messages=(start_error,),
            invalid_command=True,
        )
    assert source is not None
    assert destination is not None
    assert start_index is not None

    try:
        move = Move(
            source_column=source,
            destination_column=destination,
            start_index=start_index,
        )
    except ValueError as exc:
        return state, CommandOutcome(
            messages=(f"Invalid move input: {exc}",),
            invalid_command=True,
        )

    result = apply_move(state, move)
    if result.success:
        return state, CommandOutcome(
            messages=(result.message,),
            show_state=True,
            move_applied=True,
        )
    return state, CommandOutcome(
        messages=(f"Invalid action: {result.message}",),
        invalid_command=True,
    )


def _handle_movec(
    state: GameState, parts: list[str]
) -> tuple[GameState, CommandOutcome]:
    """Handle `movec <src> <dst> <card_count>` command."""
    if len(parts) != 4:
        return state, CommandOutcome(
            messages=("Usage: movec <src> <dst> <count>",),
            invalid_command=True,
        )

    source, source_error = _parse_int(parts[1], "source column")
    if source_error is not None:
        return state, CommandOutcome(
            messages=(source_error,),
            invalid_command=True,
        )
    destination, destination_error = _parse_int(parts[2], "destination column")
    if destination_error is not None:
        return state, CommandOutcome(
            messages=(destination_error,),
            invalid_command=True,
        )
    card_count, count_error = _parse_int(parts[3], "card count")
    if count_error is not None:
        return state, CommandOutcome(
            messages=(count_error,),
            invalid_command=True,
        )
    assert source is not None
    assert destination is not None
    assert card_count is not None

    try:
        move = Move(
            source_column=source,
            destination_column=destination,
            card_count=card_count,
        )
    except ValueError as exc:
        return state, CommandOutcome(
            messages=(f"Invalid move input: {exc}",),
            invalid_command=True,
        )

    result = apply_move(state, move)
    if result.success:
        return state, CommandOutcome(
            messages=(result.message,),
            show_state=True,
            move_applied=True,
        )
    return state, CommandOutcome(
        messages=(f"Invalid action: {result.message}",),
        invalid_command=True,
    )


def render_won_panel(
    state: GameState,
    stats: SessionStats,
    seed: int | None,
    use_color: bool,
) -> str:
    """Render a celebratory won panel with simple game summary."""
    title = _style("YOU WON!", "1;32", use_color)
    bar = _style("=" * 38, "32", use_color)
    elapsed = _format_duration(time.monotonic() - stats.started_at)
    seed_label = str(seed) if seed is not None else "random"

    lines = [
        bar,
        f"{title}",
        bar,
        (
            "Completed sequences : "
            f"{state.completed_sequences}/{WIN_COMPLETED_SEQUENCES}"
        ),
        f"Successful moves    : {stats.move_count}",
        f"Invalid commands    : {stats.invalid_count}",
        f"Elapsed time        : {elapsed}",
        f"Seed                : {seed_label}",
        "Quick options       : [n] new random  [s] same seed  [q] quit",
        bar,
    ]
    return "\n".join(lines)


def _handle_won_shortcuts(
    state: GameState,
    stats: SessionStats,
    raw: str,
    current_seed: int | None,
) -> tuple[GameState, SessionStats, bool | None, int | None]:
    """Handle quick won-only shortcuts n/s/q before normal parsing."""
    if get_game_status(state) != GameStatus.WON:
        return state, stats, False, current_seed

    command = raw.lower()
    if command == "q":
        return state, stats, True, current_seed
    if command == "n":
        new_state = new_game(seed=None)
        new_stats = SessionStats(started_at=time.monotonic())
        print("Started a new random game.")
        print(render_state(new_state))
        return new_state, new_stats, None, None
    if command == "s":
        if current_seed is None:
            print("No seed available for this run; use `new <seed>` first.")
            stats.invalid_count += 1
            return state, stats, None, current_seed
        new_state = new_game(seed=current_seed)
        new_stats = SessionStats(started_at=time.monotonic())
        print(f"Restarted game with seed={current_seed}.")
        print(render_state(new_state))
        return new_state, new_stats, None, current_seed
    return state, stats, False, current_seed


def _parse_int(
    raw: str, field_name: str
) -> tuple[int, None] | tuple[None, str]:
    """Parse integer arguments and return friendly parse errors."""
    try:
        return int(raw), None
    except ValueError:
        return None, f"Invalid {field_name}: `{raw}`"


def _format_duration(seconds: float) -> str:
    """Format elapsed seconds as mm:ss."""
    total_seconds = max(0, int(seconds))
    minutes, remain = divmod(total_seconds, 60)
    return f"{minutes:02d}:{remain:02d}"


def _should_use_color() -> bool:
    """Enable ANSI colors unless NO_COLOR is set or stdout is not a TTY."""
    if os.getenv("NO_COLOR") is not None:
        return False
    return sys.stdout.isatty()


def _style(text: str, code: str, enabled: bool) -> str:
    """Apply ANSI style sequence when enabled."""
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


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
