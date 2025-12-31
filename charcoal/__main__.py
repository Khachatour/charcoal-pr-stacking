"""Main CLI entry point for Charcoal PR Stacking tool."""

from __future__ import annotations

import click

from charcoal import __version__


@click.group()
@click.version_option(version=__version__, prog_name="gt")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Charcoal - A CLI for stacked pull requests and branch management.

    This is a Python implementation of the Graphite/Charcoal CLI tool
    for managing stacked git branches and pull requests.
    """
    # Initialize context object for shared state
    ctx.ensure_object(dict)


if __name__ == "__main__":
    cli()
