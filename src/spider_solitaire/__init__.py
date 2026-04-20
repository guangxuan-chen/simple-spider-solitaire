"""Core package for the simple Spider Solitaire project."""

from .engine import (
    CARDS_PER_RANK,
    INITIAL_COLUMN_SIZES,
    NUM_COLUMNS,
    ONE_SUIT,
    Card,
    GameState,
    Move,
    MoveResult,
    Rank,
    apply_move,
    create_deck,
    deal_stock,
    new_game,
    validate_move,
)

__all__ = [
    "CARDS_PER_RANK",
    "INITIAL_COLUMN_SIZES",
    "NUM_COLUMNS",
    "ONE_SUIT",
    "Card",
    "GameState",
    "Move",
    "MoveResult",
    "Rank",
    "apply_move",
    "create_deck",
    "deal_stock",
    "new_game",
    "validate_move",
]
