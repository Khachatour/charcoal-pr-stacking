"""Main CLI entry point for Charcoal."""

from __future__ import annotations

import os
import sys
from datetime import datetime

import click

from charcoal import __version__
from charcoal.commands.repo import repo_group
from charcoal.lib.config.models import RepoConfig
from charcoal.lib.config.store import load_repo_config, load_user_config
from charcoal.lib.context import ContextObject
from charcoal.lib.errors import UserFacingError
from charcoal.lib.git.runner import GitRunner
from charcoal.lib.preconditions import get_repo_root
from charcoal.lib.utils import splog


@click.group()
@click.version_option(version=__version__, prog_name="Charcoal")
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Display debug output.",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    default=False,
    help="Minimize output to the terminal.",
)
@click.option(
    "--interactive/--no-interactive",
    default=True,
    help="Prompt the user. Disable with --no-interactive.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    debug: bool,
    quiet: bool,
    interactive: bool,
) -> None:
    """Charcoal - A CLI for managing Git stacks and pull requests.

    This is a Python reimplementation of the Graphite CLI, providing
    tools for managing stacked pull requests and Git workflows.
    """
    # Check for GTI environment variable (behave as non-interactive if set)
    if os.environ.get("GRAPHITE_INTERACTIVE"):
        interactive = False

    # Try to find repository root (may be None if not in a repo)
    repo_root = get_repo_root()

    # Load configurations
    user_config = load_user_config()
    repo_config: RepoConfig | None = None
    git_runner: GitRunner | None = None

    if repo_root:
        # We're in a repository, load repo config and create git runner
        repo_config = load_repo_config(repo_root)
        git_runner = GitRunner(repo_root=repo_root)

    # Create context object
    ctx_obj = ContextObject(
        repo_root=repo_root,
        repo_config=repo_config,
        user_config=user_config,
        git_runner=git_runner,
        debug=debug,
        quiet=quiet,
        interactive=interactive,
    )

    # Store in Click context for subcommands
    ctx.obj = ctx_obj

    # Log debug info
    splog.debug(f"Charcoal version: {__version__}", ctx_obj)
    splog.debug(f"Repository root: {repo_root}", ctx_obj)
    splog.debug(f"Debug mode: {debug}", ctx_obj)
    splog.debug(f"Quiet mode: {quiet}", ctx_obj)
    splog.debug(f"Interactive mode: {interactive}", ctx_obj)


# Register command groups
cli.add_command(repo_group)


@cli.command()
@click.pass_context
def hello(ctx: click.Context) -> None:
    """Test command - prints a hello message."""
    ctx_obj: ContextObject = ctx.obj
    splog.info("Hello from Charcoal! 🔥", ctx_obj)
    splog.info(f"Version: {__version__}", ctx_obj)


def main() -> None:
    """Main entry point with exception handling."""
    # Parse debug flag from command line args before calling cli()
    # This allows us to access it in exception handlers even after context is gone
    debug_mode = "--debug" in sys.argv

    try:
        cli()
    except UserFacingError as e:
        # Print error message (always shown)
        click.echo(click.style(f"ERROR: {e}", fg="red", bold=True), err=True)

        # Print stack trace if debug mode is enabled
        if debug_mode:
            import traceback

            timestamp = datetime.now().isoformat()
            styled_message = click.style(
                f"{timestamp}: Stack trace:\n{traceback.format_exc()}", dim=True
            )
            click.echo(styled_message)

        # Exit with error code
        sys.exit(1)
    except click.ClickException:
        # Let Click handle its own exceptions (e.g., --help, bad arguments)
        raise
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        click.echo("\nInterrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        # Unexpected error - print full traceback
        click.echo(
            click.style(f"ERROR: Unexpected error: {e}", fg="red", bold=True),
            err=True,
        )

        import traceback

        click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
