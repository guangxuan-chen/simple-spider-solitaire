"""Integration-style tests for key engine and CLI gameplay flows."""

from __future__ import annotations

from spider_solitaire import (
    NUM_COLUMNS,
    WIN_COMPLETED_SEQUENCES,
    Card,
    GameState,
    Rank,
    get_game_status,
    new_game,
)
from spider_solitaire.cli import handle_command


def test_integration_cli_deal_updates_state_and_stock() -> None:
    """CLI deal command should update tableau/stock through engine API."""
    state = new_game(seed=7)
    before_sizes = [len(column) for column in state.tableau]
    before_stock = len(state.stock)

    returned_state, outcome = handle_command(state, "deal")

    assert returned_state is state
    assert outcome.show_state
    assert outcome.deal_applied
    assert len(state.stock) == before_stock - NUM_COLUMNS
    assert [len(column) for column in state.tableau] == [
        size + 1 for size in before_sizes
    ]


def test_integration_cli_move_can_complete_game_to_won() -> None:
    """CLI move command should drive engine to won status when applicable."""
    source = [_card(Rank.ACE)]
    destination = _k_to_two_sequence()
    state = _make_state(
        source=source,
        destination=destination,
        completed_sequences=WIN_COMPLETED_SEQUENCES - 1,
    )

    returned_state, outcome = handle_command(state, "move 0 1 0")

    assert returned_state is state
    assert outcome.show_state
    assert outcome.move_applied
    assert "Status: won." in outcome.messages[0]
    assert get_game_status(state).value == "won"
    assert state.completed_sequences == WIN_COMPLETED_SEQUENCES


def _make_state(
    source: list[Card],
    destination: list[Card],
    completed_sequences: int,
) -> GameState:
    """Build an integration fixture state with 10 tableau columns."""
    tableau = [source, destination]
    tableau.extend([[] for _ in range(NUM_COLUMNS - 2)])
    return GameState(
        tableau=tableau,
        stock=[],
        completed_sequences=completed_sequences,
    )


def _k_to_two_sequence() -> list[Card]:
    """Create a face-up descending K->2 sequence."""
    ranks = (
        Rank.KING,
        Rank.QUEEN,
        Rank.JACK,
        Rank.TEN,
        Rank.NINE,
        Rank.EIGHT,
        Rank.SEVEN,
        Rank.SIX,
        Rank.FIVE,
        Rank.FOUR,
        Rank.THREE,
        Rank.TWO,
    )
    return [_card(rank) for rank in ranks]


def _card(rank: Rank, face_up: bool = True) -> Card:
    """Create card fixtures."""
    return Card(rank=rank, face_up=face_up)
