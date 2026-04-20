# AI Usage Log

This document records generative AI usage for the BIOSTAT 821 final project, as required by the course policy.

## Tool Information

- Tool: Codex (GPT-5-based coding assistant in terminal)
- Provider: OpenAI
- Usage mode: prompt-response support for planning, documentation, and setup

## Usage Records

### Record 1
- Date: 2026-04-20
- Task: Brainstorm initial project README structure and issue planning scope.
- How AI was used:
  requested a README plan and suggested GitHub issue breakdown for a
  simplified one-suit Spider Solitaire project.
- What AI produced:
  README section structure, issue decomposition suggestions, and issue
  checklist fields.
- How output was used/modified:
  manually reviewed, then edited/replaced sections to match solo-project
  scope and course requirements.

### Record 2
- Date: 2026-04-20
- Task: Add dependency/library explanations and basic tech stack section.
- How AI was used:
  requested a concise explanation of runtime vs development libraries.
- What AI produced:
  README additions describing Python standard library usage and external
  tools (`pytest`, `ruff`, `mypy`, `coverage`).
- How output was used/modified:
  integrated into README and refined for clarity.

### Record 3
- Date: 2026-04-20
- Task: Complete Phase-1 repository setup.
- How AI was used:
  requested implementation of issue scope: project structure, config,
  `.gitignore`, initial docs, and AI usage updates.
- What AI produced:
  created/updated files:
  - `src/spider_solitaire/__init__.py`
  - `tests/test_smoke.py`
  - `requirements.txt`
  - `requirements-test.txt`
  - `pyproject.toml`
  - `.gitignore`
  - `README.md`
  - `AI_USAGE.md`
- How output was used/modified:
  manually reviewed; further manual edits may follow in later commits.

### Record 4
- Date: 2026-04-20
- Task: Simplify GitHub workflows.
- How AI was used:
  requested removal of unnecessary PR-status/comment automation and
  reduction to basic checks/tests pipelines.
- What AI produced:
  updated workflow files:
  - `.github/workflows/checks.yml` (simple lint + type-check job)
  - `.github/workflows/tests.yml` (simple pytest job)
  - removed `.github/workflows/report.yml` (EHR-specific report workflow)
- How output was used/modified:
  workflows were simplified and validated locally with `ruff` and `pytest`.

### Record 5
- Date: 2026-04-20
- Task: Implement Phase-2 engine foundation.
- How AI was used:
  requested implementation of core models and initial deal/stock logic for
  one-suit Spider Solitaire, plus acceptance-focused unit tests.
- What AI produced:
  created and updated files:
  - `src/spider_solitaire/engine.py`
  - `src/spider_solitaire/__init__.py`
  - `tests/test_engine_phase2.py`
  and executed validation commands:
  - `ruff check src tests`
  - `mypy src tests`
  - `pytest tests/`
- How output was used/modified:
  code was reviewed and lint/type/test issues were corrected before finalizing.

### Record 6
- Date: 2026-04-20
- Task: Implement Phase-3 move validation and execution.
- How AI was used:
  requested implementation of move legality checks and state updates for
  tableau-to-tableau moves, including input format, validation messages, and
  execution behavior.
- What AI produced:
  created and updated files:
  - `src/spider_solitaire/engine.py`
  - `src/spider_solitaire/__init__.py`
  - `tests/test_engine_phase3.py`
  and executed validation commands:
  - `ruff check src tests`
  - `mypy src tests`
  - `pytest tests/`
- How output was used/modified:
  output was reviewed and adjusted to satisfy lint line-length constraints and
  to keep error messages explicit for invalid moves.

### Record 7
- Date: 2026-04-20
- Task: Implement Phase-4 sequence removal and game completion checks.
- How AI was used:
  requested implementation for complete top-sequence detection/removal,
  automatic sequence checks after move and stock deal, and win/status API.
- What AI produced:
  created and updated files:
  - `src/spider_solitaire/engine.py`
  - `src/spider_solitaire/__init__.py`
  - `tests/test_engine_phase4.py`
  and executed validation commands:
  - `ruff check src tests`
  - `mypy src tests`
  - `pytest tests/`
- How output was used/modified:
  reviewed and adjusted to satisfy lint import ordering and line-length
  constraints while preserving requested behavior.

### Record 8
- Date: 2026-04-20
- Task: Add a root-level interactive debug script for manual testing.
- How AI was used:
  requested a simple local CLI to interact with engine logic for quick
  debugging and demonstration.
- What AI produced:
  created and updated files:
  - `debug_cli.py`
  - `README.md` (interactive debugging usage section)
- How output was used/modified:
  integrated directly to support interactive testing outside unit tests.

## Notes

- AI-assisted outputs were reviewed before acceptance.
- Final responsibility for correctness and submission content remains with
  the project author.
