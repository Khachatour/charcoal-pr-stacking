"""Logging utilities for Charcoal CLI.

This module provides styled logging functions that respect the quiet flag
and output appropriate colors for different message types.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from charcoal.lib.context import ContextObject


def _should_output(ctx_obj: ContextObject | None, for_error: bool = False) -> bool:
    """Check if we should output a message based on quiet flag.

    Args:
        ctx_obj: Context object (may be None if called before context is
            initialized)
        for_error: True if this is an error message (errors are shown even in
            quiet mode)

    Returns:
        True if the message should be output
    """
    if ctx_obj is None:
        return True
    if for_error:
        return True
    return not ctx_obj.quiet


def newline(ctx_obj: ContextObject | None = None) -> None:
    """Print a blank line.

    Args:
        ctx_obj: Context object (optional)
    """
    if _should_output(ctx_obj):
        click.echo()


def info(message: str, ctx_obj: ContextObject | None = None) -> None:
    """Print an info message.

    Args:
        message: The message to print
        ctx_obj: Context object (optional)
    """
    if _should_output(ctx_obj):
        click.echo(message)


def debug(message: str, ctx_obj: ContextObject | None = None) -> None:
    """Print a debug message (only if debug mode is enabled).

    Args:
        message: The message to print
        ctx_obj: Context object (optional)
    """
    if ctx_obj and ctx_obj.debug:
        timestamp = datetime.now().isoformat()
        styled_message = click.style(f"{timestamp}: {message}", dim=True)
        click.echo(styled_message)


def error(message: str, ctx_obj: ContextObject | None = None) -> None:
    """Print an error message to stderr.

    Args:
        message: The error message to print
        ctx_obj: Context object (optional)
    """
    if _should_output(ctx_obj, for_error=True):
        styled_message = click.style(f"ERROR: {message}", fg="red", bold=True)
        click.echo(styled_message, err=True)


def warn(message: str, ctx_obj: ContextObject | None = None) -> None:
    """Print a warning message.

    Args:
        message: The warning message to print
        ctx_obj: Context object (optional)
    """
    if _should_output(ctx_obj):
        styled_message = click.style(f"WARNING: {message}", fg="yellow")
        click.echo(styled_message)


def message(message: str, ctx_obj: ContextObject | None = None) -> None:
    """Print a highlighted message.

    Args:
        message: The message to print
        ctx_obj: Context object (optional)
    """
    if _should_output(ctx_obj):
        styled_message = click.style(message, fg="yellow")
        click.echo(f"{styled_message}\n")


def tip(message: str, ctx_obj: ContextObject | None = None) -> None:
    """Print a tip message (only if tips are enabled in user config).

    Args:
        message: The tip message to print
        ctx_obj: Context object (optional)
    """
    # Check if tips are enabled in user config
    if ctx_obj and ctx_obj.user_config and ctx_obj.user_config.tips is False:
        return

    if _should_output(ctx_obj):
        tip_header = click.style("tip:", bold=True)
        tip_footer = click.style(
            "Feeling expert? `gt user tips --disable`", italic=True
        )
        styled_message = click.style(
            f"\n{tip_header} {message}\n{tip_footer}\n", dim=True
        )
        click.echo(styled_message)


def page(content: str, ctx_obj: ContextObject | None = None) -> None:
    """Output content through a pager if configured, otherwise print directly.

    Args:
        content: The content to page
        ctx_obj: Context object (optional)
    """
    # Get pager from user config
    pager = None
    if ctx_obj and ctx_obj.user_config:
        pager = ctx_obj.user_config.pager

    if not pager:
        click.echo(content)
        return

    # Use click's pager functionality
    try:
        click.echo_via_pager(content)
    except Exception as e:
        # If pager fails, fall back to direct output
        click.echo(content)
        warn(
            f"Tried to send output to your pager ({pager}) but encountered an "
            f"error.\nYou can change your configured pager or disable paging: "
            f"`gt user pager --help`",
            ctx_obj=ctx_obj,
        )
        debug(f"Pager error: {e}", ctx_obj=ctx_obj)
