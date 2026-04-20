"""Tests for Phase-4 sequence removal and game completion behavior."""

from __future__ import annotations

from spider_solitaire import (
    NUM_COLUMNS,
    WIN_COMPLETED_SEQUENCES,
    Card,
    GameState,
    GameStatus,
    Move,
    Rank,
    apply_move,
    deal_stock,
    get_game_status,
    remove_complete_sequences,
)


def test_remove_complete_sequence_from_top_and_increment_counter() -> None:
    """Top K->A run should be removed and completed counter incremented."""
    column = [_card(Rank.TEN, face_up=False), *_k_to_a_sequence()]
    state = _make_state(columns=[column])

    removed = remove_complete_sequences(state)

    assert removed == 1
    assert state.completed_sequences == 1
    assert [card.rank for card in state.tableau[0]] == [Rank.TEN]
    assert state.tableau[0][-1].face_up


def test_remove_complete_sequences_requires_face_up_k_to_a() -> None:
    """A face-down card inside top K->A should block sequence removal."""
    blocked_sequence = _k_to_a_sequence()
    blocked_sequence[-1].face_up = False
    state = _make_state(columns=[blocked_sequence])

    removed = remove_complete_sequences(state)

    assert removed == 0
    assert state.completed_sequences == 0
    assert len(state.tableau[0]) == 13


def test_apply_move_triggers_sequence_removal() -> None:
    """A move that completes top K->A should auto-remove the sequence."""
    destination = _k_to_two_sequence()
    source = [_card(Rank.ACE)]
    state = _make_state(columns=[source, destination])
    move = Move(source_column=0, destination_column=1, start_index=0)

    result = apply_move(state, move)

    assert result.success
    assert "Removed 1 complete sequence(s)." in result.message
    assert state.completed_sequences == 1
    assert state.tableau[1] == []


def test_deal_stock_triggers_sequence_removal() -> None:
    """Stock deal should run sequence cleanup after cards are dealt."""
    destination = _k_to_two_sequence()
    fillers = [
        _card(Rank.THREE, face_up=False) for _ in range(NUM_COLUMNS - 1)
    ]
    stock = [*fillers, _card(Rank.ACE, face_up=False)]
    state = _make_state(columns=[destination], stock=stock)

    deal_stock(state)

    assert state.completed_sequences == 1
    assert state.tableau[0] == []


def test_get_game_status_reports_progress_and_win() -> None:
    """Status API should expose in_progress and won states."""
    state = _make_state(columns=[[]], completed_sequences=0)
    assert get_game_status(state) == GameStatus.IN_PROGRESS

    state.completed_sequences = WIN_COMPLETED_SEQUENCES
    assert get_game_status(state) == GameStatus.WON


def test_apply_move_reports_won_status_after_eighth_sequence() -> None:
    """Move execution should report won status after final sequence removal."""
    destination = _k_to_two_sequence()
    source = [_card(Rank.ACE)]
    state = _make_state(
        columns=[source, destination],
        completed_sequences=WIN_COMPLETED_SEQUENCES - 1,
    )
    move = Move(source_column=0, destination_column=1, start_index=0)

    result = apply_move(state, move)

    assert result.success
    assert "Status: won." in result.message
    assert get_game_status(state) == GameStatus.WON


def _make_state(
    columns: list[list[Card]],
    stock: list[Card] | None = None,
    completed_sequences: int = 0,
) -> GameState:
    """Build a state with provided leading columns and empty remainder."""
    tableau = list(columns)
    tableau.extend([[] for _ in range(NUM_COLUMNS - len(tableau))])
    return GameState(
        tableau=tableau,
        stock=stock if stock is not None else [],
        completed_sequences=completed_sequences,
    )


def _k_to_a_sequence() -> list[Card]:
    """Create a full face-up descending K->A sequence."""
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
        Rank.ACE,
    )
    return [_card(rank) for rank in ranks]


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
    """Create a card fixture."""
    return Card(rank=rank, face_up=face_up)
