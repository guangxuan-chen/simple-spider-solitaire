"""Root entry script for running the project CLI during development."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"


def main() -> None:
    """Bootstrap src path and delegate to package CLI entry point."""
    if str(SRC_PATH) not in sys.path:
        sys.path.insert(0, str(SRC_PATH))

    from spider_solitaire.cli import run_cli

    run_cli()


if __name__ == "__main__":
    main()
