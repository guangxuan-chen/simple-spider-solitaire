# Simple Spider Solitaire

Group member(s): Guangxuan Chen (solo project)

Single-suit Spider Solitaire implemented as a Python library (`engine`) with a
minimal command-line interface (`cli`).

## Overview

This project was built for BIOSTAT 821 and is now in a working, end-to-end
state:

- Core game logic is implemented in `src/spider_solitaire/engine.py`.
- A playable text CLI is implemented in `src/spider_solitaire/cli.py`.
- Unit and integration-style tests cover core flows in `tests/`.
- CI runs linting, formatting checks, type checking, and tests.

## Features

- 104-card one-suit deck (8 × A-K)
- Deterministic shuffle with optional seed
- Correct initial deal for 10 tableau columns (6/6/6/6/5/5/5/5/5/5)
- Stock dealing (one card to each column)
- Tableau move validation and execution
- Two move styles in CLI:
  - by start index: `move <src> <dst> <start_index>`
  - by count: `movec <src> <dst> <count>`
- Automatic complete-sequence (K->A) removal
- Win detection after 8 completed sequences
- Friendly CLI feedback and a win summary panel

## Game Rules (Implemented Scope)

- Only top cards are face up after initial deal.
- A moved sequence must:
  - come from one source column,
  - be fully face up,
  - be strictly descending by one rank.
- Destination rule:
  - destination top card must be exactly one rank higher than the moving base
    card, or
  - destination column may be empty.
- After a valid move (and after stock deal), the engine checks for complete top
  K->A sequences and removes them.
- Game status is `in_progress` or `won`.

## Architecture

The project is intentionally layered:

1. **Business logic layer** (`engine.py`)
   - owns state, rules, move legality, sequence removal, win condition
2. **Interface layer** (`cli.py`, `debug_cli.py`)
   - parses commands, renders output, calls engine APIs
   - does not duplicate game rules
3. **Tests** (`tests/`)
   - unit tests for engine and CLI functions
   - integration-style tests for key gameplay flows

## Repository Structure

```text
simple-spider-solitaire/
├── src/spider_solitaire/
│   ├── engine.py          # game models + rule engine
│   ├── cli.py             # interactive command handling + rendering
│   └── __init__.py        # public package exports
├── tests/                 # unit + integration-style tests
├── .github/workflows/     # CI checks and test workflows
├── debug_cli.py           # local entry script to play/test manually
├── pyproject.toml         # ruff, mypy, pytest config
├── requirements.txt       # runtime deps (currently minimal)
├── requirements-test.txt  # pytest + coverage
├── AI_USAGE.md            # required AI usage documentation
└── README.md
```

## Tech Stack

- **Language**: Python 3.10.8 (pyenv + venv workflow)
- **Runtime libs**: Python standard library only
- **Quality tools**: Ruff, mypy
- **Testing**: pytest, coverage
- **CI**: GitHub Actions

## Local Setup

```bash
pyenv local 3.10.8
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install ruff mypy
```

## Run the Game (CLI)

```bash
python debug_cli.py
```

Available commands:

- `show`
- `move <src> <dst> <start_index>`
- `movec <src> <dst> <count>`
- `deal`
- `new [seed]`
- `help`
- `quit`

Win-screen shortcuts:

- `n` new random game
- `s` restart with same seed
- `q` quit immediately

## Use Engine as a Library

Example (from project root):

```bash
PYTHONPATH=src python -c "from spider_solitaire import new_game; s=new_game(2026); print(len(s.tableau), len(s.stock))"
```

Core public exports are re-exported in `src/spider_solitaire/__init__.py`,
including `GameState`, `Move`, `new_game`, `apply_move`, `deal_stock`, and
`get_game_status`.

## Quality Checks and Tests

Run all local checks:

```bash
ruff check debug_cli.py src tests .github/workflows/diff_coverage.py
ruff format --check debug_cli.py src tests .github/workflows/diff_coverage.py
mypy debug_cli.py src tests .github/workflows/diff_coverage.py
pytest tests/
```

Optional coverage report:

```bash
coverage run -m pytest tests/
coverage report -m
```

## CI

Two GitHub Actions workflows are configured:

- `checks.yml`: Ruff + mypy
- `tests.yml`: pytest

Both run on `push`, `pull_request`, and manual dispatch.

## Documentation for Course Requirements

- Project plan and implementation history are tracked via GitHub issues/PRs.
- AI usage is documented in detail in `AI_USAGE.md`.
- This repository is designed so a newcomer can run the project and tests with
  the instructions above.

## Current Status

Core game engine and minimal CLI are complete for the scoped single-suit
version. Remaining improvements are polish-oriented (UI/UX, additional
commands, optional packaging/release hardening), not required for core gameplay.
