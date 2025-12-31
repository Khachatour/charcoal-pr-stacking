"""Main CLI entry point for Charcoal."""

from __future__ import annotations

import click

from charcoal import __version__


@click.group()
@click.version_option(version=__version__, prog_name="Charcoal")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Charcoal - A CLI for managing Git stacks and pull requests.

    This is a Python reimplementation of the Graphite CLI, providing
    tools for managing stacked pull requests and Git workflows.
    """
    # Ensure that ctx.obj exists and is a dict (for future context passing)
    ctx.ensure_object(dict)


@cli.command()
def hello() -> None:
    """Test command - prints a hello message."""
    click.echo("Hello from Charcoal! 🔥")
    click.echo(f"Version: {__version__}")


if __name__ == "__main__":
    cli()
