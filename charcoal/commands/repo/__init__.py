"""Repository-level commands."""

from __future__ import annotations

import click

from charcoal.commands.repo import init


@click.group(name="repo")
def repo_group() -> None:
    """Repository-level commands for managing Charcoal configuration."""
    pass


# Register subcommands
repo_group.add_command(init.init_command)
