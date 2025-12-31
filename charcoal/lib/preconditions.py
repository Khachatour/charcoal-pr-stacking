"""Precondition checks for CLI commands.

This module provides functions to validate preconditions before executing
commands, such as ensuring we're in a git repository.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from charcoal.lib.errors import PreconditionsFailedError


def get_repo_root(start_path: Path | None = None) -> Path | None:
    """Find the git repository root by walking up the directory tree.

    Args:
        start_path: Path to start searching from (defaults to current directory)

    Returns:
        Path to the repository root, or None if not in a git repository
    """
    if start_path is None:
        start_path = Path.cwd()

    # Try using git to find the repo root (most reliable method)
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass

    # Fall back to manual search
    current = start_path.resolve()
    while True:
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            # Reached filesystem root
            return None
        current = parent


def ensure_in_repo(start_path: Path | None = None) -> Path:
    """Ensure we're in a git repository and return the repo root.

    Args:
        start_path: Path to start searching from (defaults to current directory)

    Returns:
        Path to the repository root

    Raises:
        PreconditionsFailedError: If not in a git repository
    """
    repo_root = get_repo_root(start_path)
    if repo_root is None:
        raise PreconditionsFailedError("No .git repository found.")
    return repo_root


def get_git_common_dir(start_path: Path | None = None) -> Path:
    """Get the git common directory path.

    This returns the path to the .git directory (or the common dir for worktrees).

    Args:
        start_path: Path to start searching from (defaults to current directory)

    Returns:
        Path to the git common directory

    Raises:
        PreconditionsFailedError: If not in a git repository
    """
    if start_path is None:
        start_path = Path.cwd()

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=start_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            common_dir = result.stdout.strip()
            # git returns relative path, so resolve it
            if not Path(common_dir).is_absolute():
                return (start_path / common_dir).resolve()
            return Path(common_dir)
    except Exception:
        pass

    raise PreconditionsFailedError("No .git repository found.")
