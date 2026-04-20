"""Core package for the simple Spider Solitaire project."""

from .engine import (
    CARDS_PER_RANK,
    INITIAL_COLUMN_SIZES,
    NUM_COLUMNS,
    ONE_SUIT,
    Card,
    GameState,
    Rank,
    create_deck,
    deal_stock,
    new_game,
)

__all__ = [
    "CARDS_PER_RANK",
    "INITIAL_COLUMN_SIZES",
    "NUM_COLUMNS",
    "ONE_SUIT",
    "Card",
    "GameState",
    "Rank",
    "create_deck",
    "deal_stock",
    "new_game",
]
