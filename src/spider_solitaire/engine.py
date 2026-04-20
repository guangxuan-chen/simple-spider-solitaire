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


@dataclass(slots=True, frozen=True)
class Move:
    """Input format for a tableau-to-tableau move."""

    source_column: int
    destination_column: int
    start_index: int | None = None
    card_count: int | None = None

    def __post_init__(self) -> None:
        """Validate that exactly one source locator is provided."""
        has_start_index = self.start_index is not None
        has_card_count = self.card_count is not None
        if has_start_index == has_card_count:
            raise ValueError(
                "Provide exactly one of `start_index` or `card_count`."
            )

        if self.start_index is not None and self.start_index < 0:
            raise ValueError("`start_index` must be non-negative.")

        if self.card_count is not None and self.card_count <= 0:
            raise ValueError("`card_count` must be positive.")


@dataclass(slots=True, frozen=True)
class MoveResult:
    """Result object for move validation and execution."""

    success: bool
    message: str


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


def validate_move(state: GameState, move: Move) -> MoveResult:
    """Validate whether a tableau-to-tableau move is legal."""
    if not _is_valid_column_index(state, move.source_column):
        return MoveResult(False, "Source column index is out of range.")

    if not _is_valid_column_index(state, move.destination_column):
        return MoveResult(False, "Destination column index is out of range.")

    if move.source_column == move.destination_column:
        return MoveResult(
            False, "Source and destination columns must be different."
        )

    source_column = state.tableau[move.source_column]
    if not source_column:
        return MoveResult(False, "Source column is empty.")

    start_index = _resolve_start_index(len(source_column), move)
    if start_index < 0:
        return MoveResult(
            False,
            "Card count exceeds the number of cards in source column.",
        )

    if start_index >= len(source_column):
        return MoveResult(
            False, "Move start index is out of range for source column."
        )

    moving_cards = source_column[start_index:]
    if any(not card.face_up for card in moving_cards):
        return MoveResult(False, "All moved cards must be face up.")

    if not _is_descending_sequence(moving_cards):
        return MoveResult(
            False,
            "Moved cards must be in descending rank order by one.",
        )

    destination_column = state.tableau[move.destination_column]
    if destination_column:
        destination_top = destination_column[-1]
        if not destination_top.face_up:
            return MoveResult(
                False,
                "Cannot place cards onto a face-down destination card.",
            )

        moving_base = moving_cards[0]
        if int(destination_top.rank) != int(moving_base.rank) + 1:
            return MoveResult(
                False,
                "Destination top card must be exactly one rank higher.",
            )

    return MoveResult(True, "Move is valid.")


def apply_move(state: GameState, move: Move) -> MoveResult:
    """Execute a legal tableau-to-tableau move and update game state."""
    validation = validate_move(state, move)
    if not validation.success:
        return validation

    source_column = state.tableau[move.source_column]
    destination_column = state.tableau[move.destination_column]
    start_index = _resolve_start_index(len(source_column), move)

    moving_cards = source_column[start_index:]
    del source_column[start_index:]
    destination_column.extend(moving_cards)

    if source_column and not source_column[-1].face_up:
        source_column[-1].face_up = True

    return MoveResult(
        True,
        (
            f"Moved {len(moving_cards)} card(s) from column "
            f"{move.source_column} to column {move.destination_column}."
        ),
    )


def _is_valid_column_index(state: GameState, column_index: int) -> bool:
    """Return True when a column index exists in the tableau."""
    return 0 <= column_index < len(state.tableau)


def _resolve_start_index(column_length: int, move: Move) -> int:
    """Resolve move start index from direct index or card count."""
    if move.start_index is not None:
        return move.start_index

    if move.card_count is None:
        raise ValueError("Move requires `start_index` or `card_count`.")
    return column_length - move.card_count


def _is_descending_sequence(cards: list[Card]) -> bool:
    """Return True if cards descend by one rank from bottom to top."""
    for index in range(len(cards) - 1):
        lower_card = cards[index]
        upper_card = cards[index + 1]
        if int(lower_card.rank) != int(upper_card.rank) + 1:
            return False
    return True


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
