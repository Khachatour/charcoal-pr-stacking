"""Context object for CLI commands."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from charcoal.lib.config.models import RepoConfig, UserConfig
from charcoal.lib.git.runner import GitRunner


@dataclass
class ContextObject:
    """Shared context object passed between CLI commands.

    This dataclass encapsulates all shared state needed by CLI commands,
    including configuration, git runner, and command-line flags.

    Attributes:
        repo_root: Path to the git repository root (None if not in a repo)
        repo_config: Repository-specific configuration (None if not in a repo)
        user_config: User-specific configuration
        git_runner: GitRunner instance for executing git commands (None if not
            in a repo)
        debug: Whether debug mode is enabled
        quiet: Whether quiet mode is enabled (minimizes output)
        interactive: Whether interactive prompts are enabled
    """

    repo_root: Path | None
    repo_config: RepoConfig | None
    user_config: UserConfig
    git_runner: GitRunner | None
    debug: bool
    quiet: bool
    interactive: bool
