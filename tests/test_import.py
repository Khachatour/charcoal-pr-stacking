"""Basic import tests to verify package structure."""

from __future__ import annotations


def test_import_charcoal() -> None:
    """Test that the charcoal package can be imported."""
    import charcoal

    assert charcoal.__version__ == "0.2.4"


def test_import_subpackages() -> None:
    """Test that all subpackages can be imported."""
    import charcoal.actions
    import charcoal.commands
    import charcoal.lib
    import charcoal.lib.api
    import charcoal.lib.config
    import charcoal.lib.engine
    import charcoal.lib.git
    import charcoal.lib.utils

    # Basic assertion to ensure imports worked
    assert charcoal.actions is not None
    assert charcoal.commands is not None
    assert charcoal.lib is not None
