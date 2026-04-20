"""Smoke tests for Phase-1 project setup."""


def test_import_package() -> None:
    """Ensure the core package can be imported."""
    import spider_solitaire

    assert spider_solitaire is not None
