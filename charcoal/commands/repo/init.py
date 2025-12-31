"""Repository initialization command."""

from __future__ import annotations

import click

from charcoal.actions.init import init_repository
from charcoal.lib.context import ContextObject
from charcoal.lib.preconditions import ensure_in_repo


@click.command(name="init")
@click.option(
    "--trunk",
    type=str,
    help="The name of your trunk branch.",
)
@click.option(
    "--no-interactive",
    is_flag=True,
    default=False,
    help="Disable interactive prompts.",
)
@click.pass_context
def init_command(ctx: click.Context, trunk: str | None, no_interactive: bool) -> None:
    """Create or regenerate a `.graphite_repo_config` file.

    This command initializes Charcoal in your repository by setting the
    trunk branch, which is the branch you open pull requests against
    (typically 'main' or 'master').

    Examples:
        gt repo init --trunk main
        gt repo init  # Interactive mode
    """
    ctx_obj: ContextObject = ctx.obj

    # Ensure we're in a repository
    repo_root = ensure_in_repo()

    # Ensure git_runner is available (should be if we're in a repo)
    if ctx_obj.git_runner is None:
        raise RuntimeError("GitRunner not initialized")

    # Ensure repo_config is available
    if ctx_obj.repo_config is None:
        raise RuntimeError("RepoConfig not initialized")

    # Determine interactive mode: local flag overrides global setting
    interactive = ctx_obj.interactive and not no_interactive

    # Call the init action
    init_repository(
        repo_root=repo_root,
        git_runner=ctx_obj.git_runner,
        repo_config=ctx_obj.repo_config,
        trunk_arg=trunk,
        interactive=interactive,
    )
