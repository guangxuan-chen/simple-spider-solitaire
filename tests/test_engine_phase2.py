"""Tests for Phase-2 engine foundation and initial dealing behavior."""

from __future__ import annotations

from collections import Counter

import pytest

from spider_solitaire import (
    INITIAL_COLUMN_SIZES,
    NUM_COLUMNS,
    Card,
    GameState,
    Rank,
    create_deck,
    deal_stock,
    new_game,
)


def test_create_deck_has_expected_size_and_rank_distribution() -> None:
    """Deck should contain 104 one-suit cards with 8 cards per rank."""
    deck = create_deck()

    assert len(deck) == 104
    assert all(card.suit == "S" for card in deck)

    rank_counts = Counter(card.rank for card in deck)
    assert all(rank_counts[rank] == 8 for rank in Rank)


def test_new_game_is_reproducible_when_seed_matches() -> None:
    """The same random seed should produce identical initial state."""
    state_1 = new_game(seed=2026)
    state_2 = new_game(seed=2026)

    assert _snapshot_state(state_1) == _snapshot_state(state_2)


def test_new_game_initial_tableau_and_stock_counts() -> None:
    """Initial layout should match Spider's one-suit setup rules."""
    state = new_game(seed=1)

    column_sizes = [len(column) for column in state.tableau]
    assert column_sizes == list(INITIAL_COLUMN_SIZES)
    assert len(state.stock) == 50


def test_new_game_only_top_tableau_cards_are_face_up() -> None:
    """Each tableau column should start with only its top card face up."""
    state = new_game(seed=7)

    for column in state.tableau:
        assert all(not card.face_up for card in column[:-1])
        assert column[-1].face_up


def test_deal_stock_adds_one_face_up_card_to_each_column() -> None:
    """Stock deal should add one face-up card to all 10 columns."""
    state = new_game(seed=10)
    previous_sizes = [len(column) for column in state.tableau]
    previous_stock_size = len(state.stock)

    deal_stock(state)

    assert len(state.stock) == previous_stock_size - NUM_COLUMNS
    for index, column in enumerate(state.tableau):
        assert len(column) == previous_sizes[index] + 1
        assert column[-1].face_up


def test_deal_stock_raises_if_fewer_than_ten_cards_remain() -> None:
    """Dealing stock requires at least one card per tableau column."""
    state = GameState(tableau=[[] for _ in range(NUM_COLUMNS)], stock=[])
    state.stock = [Card(rank=Rank.ACE) for _ in range(NUM_COLUMNS - 1)]

    with pytest.raises(ValueError, match="Not enough cards in stock"):
        deal_stock(state)


def _snapshot_state(
    state: GameState,
) -> tuple[
    tuple[tuple[tuple[Rank, bool], ...], ...],
    tuple[tuple[Rank, bool], ...],
]:
    """Convert state into immutable tuples for deterministic comparison."""
    tableau_view = tuple(
        tuple((card.rank, card.face_up) for card in column)
        for column in state.tableau
    )
    stock_view = tuple((card.rank, card.face_up) for card in state.stock)
    return tableau_view, stock_view
