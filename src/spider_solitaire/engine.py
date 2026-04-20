"""Core engine models and setup logic for one-suit Spider Solitaire."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import IntEnum
from typing import Final

NUM_COLUMNS: Final[int] = 10
CARDS_PER_RANK: Final[int] = 8
INITIAL_COLUMN_SIZES: Final[tuple[int, ...]] = (6, 6, 6, 6, 5, 5, 5, 5, 5, 5)
ONE_SUIT: Final[str] = "S"


class Rank(IntEnum):
    """Card ranks from ace to king."""

    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13


@dataclass(slots=True)
class Card:
    """A single playing card used by the engine."""

    rank: Rank
    suit: str = ONE_SUIT
    face_up: bool = False


@dataclass(slots=True)
class GameState:
    """Mutable game state for a single Spider Solitaire run."""

    tableau: list[list[Card]]
    stock: list[Card]
    completed_sequences: int = 0


def create_deck() -> list[Card]:
    """Create a 104-card one-suit Spider Solitaire deck."""
    deck: list[Card] = []
    for _ in range(CARDS_PER_RANK):
        for rank in Rank:
            deck.append(Card(rank=rank))
    return deck


def new_game(seed: int | None = None) -> GameState:
    """Create a new game with shuffled deck and initial deal."""
    deck = create_deck()
    random.Random(seed).shuffle(deck)
    tableau = _deal_initial_tableau(deck)
    return GameState(tableau=tableau, stock=deck)


def deal_stock(state: GameState) -> None:
    """Deal one face-up stock card to each tableau column."""
    if len(state.stock) < NUM_COLUMNS:
        raise ValueError("Not enough cards in stock to deal to all columns.")

    for column in state.tableau:
        card = state.stock.pop()
        card.face_up = True
        column.append(card)


def _deal_initial_tableau(deck: list[Card]) -> list[list[Card]]:
    """Deal cards to the 10 columns using Spider initial layout rules."""
    tableau: list[list[Card]] = []
    for column_size in INITIAL_COLUMN_SIZES:
        column: list[Card] = []
        for card_index in range(column_size):
            card = deck.pop()
            card.face_up = card_index == (column_size - 1)
            column.append(card)
        tableau.append(column)
    return tableau
