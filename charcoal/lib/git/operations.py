"""Higher-level Git operations built on GitRunner."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from charcoal.lib.git.runner import GitRunner


def get_all_branches(git_runner: GitRunner) -> list[str]:
    """Get a list of all local branch names.

    Args:
        git_runner: GitRunner instance to use for executing git commands

    Returns:
        List of branch names sorted by commit date (most recent first)
    """
    # Use for-each-ref to get branches sorted by committer date
    output = git_runner.run(
        "for-each-ref",
        "--format=%(refname:short)",
        "--sort=-committerdate",
        "refs/heads/",
    )

    if not output:
        return []

    return [line for line in output.split("\n") if line]


def find_remote_branch(git_runner: GitRunner, remote: str = "origin") -> str | None:
    """Find a branch that tracks the given remote.

    This looks for git config entries like `branch.main.remote origin`
    and returns the branch name.

    Args:
        git_runner: GitRunner instance to use for executing git commands
        remote: Name of the remote to search for (default: "origin")

    Returns:
        The branch name that tracks the remote, or None if not found
    """
    # Search for git config entries: branch.<name>.remote <remote>
    output = git_runner.run(
        "config",
        "--get-regexp",
        "remote$",
        f"^{remote}$",
        check=False,
    )

    if not output:
        return None

    # Parse first line: "branch.main.remote origin" -> "main"
    lines = output.strip().split("\n")
    if lines:
        first_line = lines[0]
        # Extract branch name from "branch.<branchName>.remote"
        parts = first_line.split(".")
        if len(parts) >= 2:
            return parts[1]

    return None
