"""Tests for Phase-3 move validation and execution behavior."""

from __future__ import annotations

import pytest

from spider_solitaire import (
    NUM_COLUMNS,
    Card,
    GameState,
    Move,
    Rank,
    apply_move,
    validate_move,
)


def test_apply_move_by_start_index_preserves_order_and_flips_exposed() -> None:
    """Move keeps card order and flips newly exposed source card."""
    state = _make_state(
        source_cards=[
            _card(Rank.TEN, False),
            _card(Rank.EIGHT),
            _card(Rank.SEVEN),
            _card(Rank.SIX),
        ],
        destination_cards=[_card(Rank.NINE)],
    )
    move = Move(source_column=0, destination_column=1, start_index=1)

    result = apply_move(state, move)

    assert result.success
    assert [card.rank for card in state.tableau[1]] == [
        Rank.NINE,
        Rank.EIGHT,
        Rank.SEVEN,
        Rank.SIX,
    ]
    assert [card.rank for card in state.tableau[0]] == [Rank.TEN]
    assert state.tableau[0][-1].face_up


def test_apply_move_by_card_count_is_supported() -> None:
    """Move input may use card_count instead of start_index."""
    state = _make_state(
        source_cards=[
            _card(Rank.TEN, False),
            _card(Rank.EIGHT),
            _card(Rank.SEVEN),
        ],
        destination_cards=[_card(Rank.NINE)],
    )
    move = Move(source_column=0, destination_column=1, card_count=2)

    result = apply_move(state, move)

    assert result.success
    assert [card.rank for card in state.tableau[1]] == [
        Rank.NINE,
        Rank.EIGHT,
        Rank.SEVEN,
    ]


def test_validate_move_rejects_face_down_cards_in_moving_sequence() -> None:
    """Source sequence must be fully face up to be movable."""
    state = _make_state(
        source_cards=[
            _card(Rank.TEN, False),
            _card(Rank.EIGHT, False),
            _card(Rank.SEVEN),
        ],
        destination_cards=[_card(Rank.NINE)],
    )
    move = Move(source_column=0, destination_column=1, start_index=1)

    result = validate_move(state, move)

    assert not result.success
    assert result.message == "All moved cards must be face up."


def test_validate_move_rejects_non_descending_source_sequence() -> None:
    """Moved cards must descend exactly by one rank."""
    state = _make_state(
        source_cards=[
            _card(Rank.TEN, False),
            _card(Rank.EIGHT),
            _card(Rank.SIX),
        ],
        destination_cards=[_card(Rank.NINE)],
    )
    move = Move(source_column=0, destination_column=1, start_index=1)

    result = validate_move(state, move)

    assert not result.success
    assert (
        result.message
        == "Moved cards must be in descending rank order by one."
    )


def test_validate_move_enforces_destination_rank_rule() -> None:
    """Destination top rank must be exactly one higher than moved base card."""
    state = _make_state(
        source_cards=[
            _card(Rank.TEN, False),
            _card(Rank.EIGHT),
            _card(Rank.SEVEN),
        ],
        destination_cards=[_card(Rank.JACK)],
    )
    move = Move(source_column=0, destination_column=1, start_index=1)

    result = validate_move(state, move)

    assert not result.success
    assert (
        result.message
        == "Destination top card must be exactly one rank higher."
    )


def test_validate_move_allows_any_sequence_to_empty_destination() -> None:
    """Any legal source sequence can move to an empty destination column."""
    state = _make_state(
        source_cards=[
            _card(Rank.TEN, False),
            _card(Rank.EIGHT),
            _card(Rank.SEVEN),
        ],
        destination_cards=[],
    )
    move = Move(source_column=0, destination_column=1, start_index=1)

    result = validate_move(state, move)

    assert result.success
    assert result.message == "Move is valid."


def test_apply_move_returns_clear_message_for_invalid_move() -> None:
    """Invalid moves should return a failure result with a clear message."""
    state = _make_state(
        source_cards=[
            _card(Rank.TEN, False),
            _card(Rank.EIGHT),
            _card(Rank.SEVEN),
        ],
        destination_cards=[_card(Rank.JACK)],
    )
    move = Move(source_column=0, destination_column=1, start_index=1)

    result = apply_move(state, move)

    assert not result.success
    assert (
        result.message
        == "Destination top card must be exactly one rank higher."
    )


def test_move_rejects_missing_or_duplicate_locator_inputs() -> None:
    """Move input format requires exactly one locator style."""
    with pytest.raises(ValueError, match="exactly one"):
        Move(source_column=0, destination_column=1)

    with pytest.raises(ValueError, match="exactly one"):
        Move(
            source_column=0,
            destination_column=1,
            start_index=2,
            card_count=3,
        )


def _make_state(
    source_cards: list[Card],
    destination_cards: list[Card],
) -> GameState:
    """Create a game state fixture with two primary tableau columns."""
    tableau = [source_cards, destination_cards]
    tableau.extend([[] for _ in range(NUM_COLUMNS - 2)])
    return GameState(tableau=tableau, stock=[])


def _card(rank: Rank, face_up: bool = True) -> Card:
    """Build a card for test fixture setup."""
    return Card(rank=rank, face_up=face_up)
