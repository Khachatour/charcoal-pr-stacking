"""Repository initialization action."""

from __future__ import annotations

from pathlib import Path

import click

from charcoal.lib.config.models import RepoConfig
from charcoal.lib.config.store import save_repo_config
from charcoal.lib.errors import PreconditionsFailedError
from charcoal.lib.git.operations import find_remote_branch, get_all_branches
from charcoal.lib.git.runner import GitRunner
from charcoal.lib.utils import splog


def init_repository(
    repo_root: Path,
    git_runner: GitRunner,
    repo_config: RepoConfig,
    trunk_arg: str | None,
    interactive: bool,
) -> None:
    """Initialize a Charcoal repository by setting the trunk branch.

    This is the main action function for `gt repo init`. It:
    1. Gets all branches from the repository
    2. Selects the trunk branch (from arg, inference, or prompt)
    3. Saves the trunk to repo config
    4. Logs success message

    Args:
        repo_root: Path to the repository root
        git_runner: GitRunner instance for executing git commands
        repo_config: Current repository configuration
        trunk_arg: Trunk branch name provided via --trunk option (may be None)
        interactive: Whether to prompt the user for input

    Raises:
        PreconditionsFailedError: If no branches exist or trunk cannot be determined
    """
    # Display welcome message
    already_initialized = repo_config.graphite_initialized()
    if already_initialized:
        splog.info("Reinitializing Charcoal...")
    else:
        splog.info("Welcome to Charcoal!")
    splog.newline()

    # Get all branches
    all_branches = get_all_branches(git_runner)

    if not all_branches:
        raise PreconditionsFailedError(
            "No branches found in current repo; cannot initialize Charcoal.\n"
            "Please create your first commit and then re-run your Charcoal command."
        )

    # Select trunk branch
    trunk_name = select_trunk_branch(
        all_branches=all_branches,
        git_runner=git_runner,
        trunk_arg=trunk_arg,
        interactive=interactive,
    )

    # Save trunk to config
    repo_config.trunk = trunk_name
    save_repo_config(repo_root, repo_config)

    # Log success
    styled_trunk = click.style(trunk_name, fg="green")
    splog.info(f"Trunk set to {styled_trunk}")


def select_trunk_branch(
    all_branches: list[str],
    git_runner: GitRunner,
    trunk_arg: str | None,
    interactive: bool,
) -> str:
    """Select the trunk branch from arguments, inference, or user prompt.

    Args:
        all_branches: List of all branch names
        git_runner: GitRunner instance for executing git commands
        trunk_arg: Trunk branch name provided via --trunk option (may be None)
        interactive: Whether to prompt the user for input

    Returns:
        The selected trunk branch name

    Raises:
        PreconditionsFailedError: If trunk cannot be determined
    """
    # If --trunk is provided and valid, use it immediately
    if trunk_arg and trunk_arg in all_branches:
        return trunk_arg

    # Try to infer trunk (whether or not trunk_arg was provided)
    inferred_trunk = infer_trunk_branch(all_branches, git_runner)

    # If not interactive, use inferred trunk or fail
    if not interactive:
        if inferred_trunk:
            return inferred_trunk
        else:
            raise PreconditionsFailedError(
                "Could not infer trunk branch, pass in an existing branch name "
                "with --trunk or run in interactive mode."
            )

    # Interactive mode: prompt user
    prompt_message = "Select a trunk branch, which you open pull requests against"
    if inferred_trunk:
        styled_trunk = click.style(inferred_trunk, fg="green")
        prompt_message += f" - inferred trunk {styled_trunk}"
    prompt_message += " (autocomplete or arrow keys)"

    # Use click.prompt with a choice type
    trunk_name = str(
        click.prompt(
            prompt_message,
            type=click.Choice(all_branches),
            default=inferred_trunk if inferred_trunk else all_branches[0],
            show_choices=False,  # Don't show all choices inline (too many)
        )
    )

    return trunk_name


def infer_trunk_branch(all_branches: list[str], git_runner: GitRunner) -> str | None:
    """Try to infer the trunk branch from remote tracking or common names.

    Args:
        all_branches: List of all branch names
        git_runner: GitRunner instance for executing git commands

    Returns:
        The inferred trunk branch name, or None if inference fails
    """
    # Try to find a branch that tracks origin
    remote_branch = find_remote_branch(git_runner, "origin")
    if remote_branch and remote_branch in all_branches:
        return remote_branch

    # Try common trunk names
    common_trunks = ["main", "master", "development", "develop"]
    matching_trunks = [b for b in all_branches if b in common_trunks]

    # Only return if exactly one match (otherwise ambiguous)
    if len(matching_trunks) == 1:
        return matching_trunks[0]

    return None
