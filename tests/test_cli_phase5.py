"""Tests for Phase-5 minimal command-line interface behavior."""

from __future__ import annotations

import time

from spider_solitaire import Card, GameState, Rank, new_game
from spider_solitaire.cli import (
    SessionStats,
    handle_command,
    render_state,
    render_won_panel,
)


def test_help_and_show_commands() -> None:
    """CLI should support help text and state rendering trigger."""
    state = new_game(seed=1)

    same_state, outcome_help = handle_command(state, "help")
    assert same_state is state
    assert outcome_help.messages
    assert "Commands:" in outcome_help.messages[0]

    same_state, outcome_show = handle_command(state, "show")
    assert same_state is state
    assert outcome_show.show_state


def test_quit_command_sets_exit_flag() -> None:
    """CLI quit command should request loop termination."""
    state = new_game(seed=1)
    same_state, outcome = handle_command(state, "quit")
    assert same_state is state
    assert outcome.should_quit


def test_new_command_supports_seed_and_reproducibility() -> None:
    """`new <seed>` should restart game deterministically."""
    base_state = new_game(seed=1)
    state_1, _ = handle_command(base_state, "new 2026")
    state_2, _ = handle_command(base_state, "new 2026")

    assert _snapshot(state_1) == _snapshot(state_2)


def test_move_command_maps_to_engine_api_and_updates_state() -> None:
    """CLI move command should parse and execute a valid engine move."""
    state = _make_state(
        source=[_card(Rank.TEN, False), _card(Rank.EIGHT), _card(Rank.SEVEN)],
        destination=[_card(Rank.NINE)],
    )

    returned_state, outcome = handle_command(state, "move 0 1 1")

    assert returned_state is state
    assert outcome.show_state
    assert outcome.messages
    assert "Moved 2 card(s)" in outcome.messages[0]
    assert outcome.move_applied
    assert [card.rank for card in state.tableau[1]] == [
        Rank.NINE,
        Rank.EIGHT,
        Rank.SEVEN,
    ]


def test_movec_command_maps_to_engine_api_and_updates_state() -> None:
    """CLI movec command should parse and execute card-count moves."""
    state = _make_state(
        source=[_card(Rank.TEN, False), _card(Rank.EIGHT), _card(Rank.SEVEN)],
        destination=[_card(Rank.NINE)],
    )

    returned_state, outcome = handle_command(state, "movec 0 1 2")

    assert returned_state is state
    assert outcome.show_state
    assert outcome.messages
    assert "Moved 2 card(s)" in outcome.messages[0]
    assert [card.rank for card in state.tableau[1]] == [
        Rank.NINE,
        Rank.EIGHT,
        Rank.SEVEN,
    ]


def test_move_command_reports_friendly_error_for_invalid_move() -> None:
    """Invalid moves should return a friendly action error message."""
    state = _make_state(
        source=[_card(Rank.TEN, False), _card(Rank.EIGHT), _card(Rank.SEVEN)],
        destination=[_card(Rank.JACK)],
    )

    _, outcome = handle_command(state, "move 0 1 1")

    assert outcome.messages == (
        "Invalid action: Destination top card must be exactly one rank "
        "higher.",
    )


def test_deal_command_reports_usage_and_action_errors() -> None:
    """Deal command should return usage errors and action errors clearly."""
    state = _make_state(source=[], destination=[])

    _, usage_outcome = handle_command(state, "deal extra")
    assert usage_outcome.messages == ("Usage: deal",)

    _, error_outcome = handle_command(state, "deal")
    assert error_outcome.messages
    assert error_outcome.messages[0].startswith("Invalid action:")


def test_movec_command_reports_usage_error() -> None:
    """Movec command should show usage when arguments are missing."""
    state = _make_state(source=[], destination=[])
    _, outcome = handle_command(state, "movec 0 1")
    assert outcome.messages == ("Usage: movec <src> <dst> <count>",)


def test_unknown_command_returns_friendly_message() -> None:
    """Unknown commands should guide users to help."""
    state = new_game(seed=1)
    _, outcome = handle_command(state, "foobar")
    assert outcome.messages == ("Unknown command. Type `help`.",)
    assert outcome.invalid_command


def test_render_state_contains_status_and_tableau_lines() -> None:
    """Rendered state should include compact status and tableau section."""
    state = _make_state(
        source=[_card(Rank.TEN, False), _card(Rank.EIGHT)],
        destination=[],
    )
    rendered = render_state(state)

    assert "Status:" in rendered
    assert "Tableau:" in rendered
    assert "0: XX 8" in rendered


def test_render_won_panel_contains_summary_and_quick_options() -> None:
    """Won panel should include summary metrics and n/s/q shortcuts."""
    state = _make_state(source=[], destination=[])
    state.completed_sequences = 8
    stats = SessionStats(
        started_at=time.monotonic() - 125.0,
        move_count=31,
        deal_count=5,
        invalid_count=2,
    )

    panel = render_won_panel(
        state=state,
        stats=stats,
        seed=2026,
        use_color=False,
    )

    assert "YOU WON!" in panel
    assert "Completed sequences : 8/8" in panel
    assert "Successful moves    : 31" in panel
    assert "Invalid commands    : 2" in panel
    assert "Seed                : 2026" in panel
    assert "[n] new random" in panel
    assert "[s] same seed" in panel
    assert "[q] quit" in panel


def _make_state(source: list[Card], destination: list[Card]) -> GameState:
    """Build minimal two-column setup for CLI tests."""
    tableau = [source, destination]
    tableau.extend([[] for _ in range(8)])
    return GameState(tableau=tableau, stock=[])


def _card(rank: Rank, face_up: bool = True) -> Card:
    """Create card fixtures."""
    return Card(rank=rank, face_up=face_up)


def _snapshot(
    state: GameState,
) -> tuple[
    tuple[tuple[tuple[Rank, bool], ...], ...],
    tuple[tuple[Rank, bool], ...],
    int,
]:
    """Create immutable state snapshot for deterministic comparisons."""
    tableau = tuple(
        tuple((card.rank, card.face_up) for card in column)
        for column in state.tableau
    )
    stock = tuple((card.rank, card.face_up) for card in state.stock)
    return tableau, stock, state.completed_sequences
