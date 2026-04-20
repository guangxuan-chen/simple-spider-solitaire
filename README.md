# simple-spider-solitaire

Group member(s): Guangxuan Chen (solo project)

## Project Overview

This repository contains the BIOSTAT 821 final project: a simplified
single-suit `Spider Solitaire` implementation in Python.

Primary goal:
build a clean, testable Python library for game logic, then add an
interface layer (CLI first) that is decoupled from core business logic.

## Software Architecture

The project follows a layered architecture:

1. Core library (`src/`):
defines game state, rules, move validation, and win/loss logic.
2. Interface layer (CLI, optional future GUI/API):
reads user input and renders output, but does not implement game rules.
3. Tests (`tests/`):
validate the behavior of the core library independently of interface code.

Design rule:
all game rules must live in the core library, not in interface code.

## MVP Game Scope (Single-Suit Spider)

1. 104 cards total (8 sets of A-K in one suit).
2. 10 tableau columns.
3. Initial deal: first 4 columns get 6 cards each, remaining 6 get 5.
4. Only top cards are face up.
5. Remaining cards are in stock and can be dealt in batches.
6. Valid move: move a card/sequence onto a card exactly one rank higher.
7. Any card/sequence may be moved to an empty column.
8. Complete K->A sequences are removed automatically.
9. Remove all 8 complete sequences to win.

## Out of Scope for MVP

1. GUI
2. Online multiplayer
3. Animation/audio polish

## Repository Structure

```text
simple-spider-solitaire/
├── src/                    # Core library (business logic)
├── tests/                  # Unit/integration tests
├── .github/workflows/      # CI workflows
├── pyproject.toml          # ruff/mypy/pytest config
├── AI_USAGE.md             # required generative AI usage log
└── README.md
```

## Development Practices (Course Alignment)

1. Style consistency:
use `ruff` for linting and formatting checks.
2. Testing:
write and maintain tests for core functionality; tests must pass in CI.
3. Documentation:
README must enable a newcomer to run code and tests without assistance.
4. Collaboration:
use GitHub issues for planning, and pull requests for code review.

## Libraries Used

The project keeps runtime dependencies minimal and uses external libraries
mainly for development quality.

### Runtime (Core Library + CLI)

1. Python standard library:
`dataclasses`, `typing`, `enum`, `random`, and `argparse`.
2. Third-party runtime dependencies:
none planned for the MVP.

### Development, Testing, and Quality

1. `pytest`: unit and integration testing.
2. `ruff`: linting and formatting checks.
3. `mypy`: static type checking.
4. `coverage`: test coverage measurement.

## Basic Tech Stack

1. Language: Python 3.10+
2. Project packaging/config: `pyproject.toml`
3. Code quality: `ruff` + `mypy`
4. Testing: `pytest` + `coverage`
5. CI: GitHub Actions (`checks` + `tests`)

## Local Setup

```bash
pyenv local 3.10.8
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install ruff mypy
```

## Run Checks and Tests

```bash
ruff check $(git ls-files '*.py')
ruff format --check $(git ls-files '*.py')
mypy $(git ls-files '*.py')
pytest tests/
```

## Interactive Debugging

You can interact with current business logic in a local debug CLI:

```bash
python debug_cli.py
```

Available commands:

1. `show` to print tableau and status
2. `status` to print stock/completed/game status
3. `new [seed]` to restart with optional deterministic seed
4. `deal` to deal one card to each tableau column
5. `move <src> <dst> <start_index>` to move by start index
6. `movec <src> <dst> <card_count>` to move by card count
7. `quit` or `exit` to stop

## Project Plan: Initial Issue Breakdown

Since this is a solo project, use a smaller set of milestone-sized issues.
Assign all issues to `Guangxuan Chen`.

1. `chore: bootstrap project structure, dependencies, and CI setup`
2. `feat(engine): implement core models and initial deal/stock logic`
3. `feat(engine): implement move validation and move execution`
4. `feat(engine): implement sequence removal and win/loss detection`
5. `feat(cli): build minimal CLI interface decoupled from engine`
6. `test/docs: add engine tests, usage docs, and AI usage log template`

For each issue, include:
background, objective, acceptance criteria, out-of-scope notes, assignee(s),
and linked PRs.

## Pull Request Workflow

1. Open a branch from `main`.
2. Link each PR to one issue.
3. Ensure CI checks pass before merge.
4. For major changes, optionally request instructor feedback via PR.

## Generative AI Usage Requirement

This project allows generative AI usage only with full documentation.
Record all AI usage in `AI_USAGE.md`, including:

1. tool name
2. prompt/request summary
3. output summary
4. how the output was used or modified
