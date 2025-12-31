"""Utilities for running CLI commands in tests.

This module provides utilities for executing the charcoal CLI in test contexts,
either using Click's CliRunner for unit-style tests or subprocess for integration
tests that exercise the actual installed command.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from click.testing import CliRunner

from charcoal.__main__ import cli


class CliTestRunner:
    """Runner for executing CLI commands in tests.

    This class provides methods for running the charcoal CLI in test contexts.
    It can use Click's CliRunner for fast unit tests or subprocess for more
    realistic integration tests.
    """

    def __init__(self, repo_dir: Path, use_subprocess: bool = False) -> None:
        """Initialize the CLI test runner.

        Args:
            repo_dir: Path to the repository where commands should run
            use_subprocess: If True, use subprocess; if False, use Click's CliRunner
        """
        self.repo_dir = repo_dir
        self.use_subprocess = use_subprocess
        self.click_runner = CliRunner() if not use_subprocess else None

    def run_command(
        self,
        args: list[str],
        expect_success: bool = True,
        env: dict[str, str] | None = None,
    ) -> CliResult:
        """Run a CLI command.

        Args:
            args: Command arguments (e.g., ["repo", "init", "--trunk", "main"])
            expect_success: If True, raise exception on non-zero exit code
            env: Optional environment variables to set

        Returns:
            CliResult with command output and exit code

        Raises:
            CliCommandError: If expect_success=True and command fails
        """
        if self.use_subprocess:
            return self._run_subprocess(args, expect_success, env)
        else:
            return self._run_click(args, expect_success, env)

    def _run_click(
        self,
        args: list[str],
        expect_success: bool = True,
        env: dict[str, str] | None = None,
    ) -> CliResult:
        """Run command using Click's CliRunner."""
        if self.click_runner is None:
            raise RuntimeError("CliRunner not initialized")

        # Set up environment
        test_env = os.environ.copy()
        if env:
            test_env.update(env)

        # Save current directory and change to repo directory
        old_cwd = os.getcwd()
        try:
            os.chdir(self.repo_dir)
            # Run the command (catch exceptions so we can wrap them)
            result = self.click_runner.invoke(
                cli, args, catch_exceptions=True, env=test_env, obj=None
            )
        finally:
            # Restore original directory
            os.chdir(old_cwd)

        # Handle exception type - Click may return BaseException
        exception: Exception | None = None
        if result.exception and isinstance(result.exception, Exception):
            exception = result.exception

        cli_result = CliResult(
            exit_code=result.exit_code,
            stdout=result.stdout or "",
            stderr=result.stderr or "" if hasattr(result, "stderr") else "",
            exception=exception,
        )

        if expect_success and result.exit_code != 0:
            raise CliCommandError(args, cli_result)

        return cli_result

    def _run_subprocess(
        self,
        args: list[str],
        expect_success: bool = True,
        env: dict[str, str] | None = None,
    ) -> CliResult:
        """Run command using subprocess (more realistic integration test)."""
        # Set up environment
        test_env = os.environ.copy()
        if env:
            test_env.update(env)

        # Run the command via the gt entry point
        try:
            result = subprocess.run(
                ["gt"] + args,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                env=test_env,
                check=False,
            )

            cli_result = CliResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                exception=None,
            )

            if expect_success and result.returncode != 0:
                raise CliCommandError(args, cli_result)

            return cli_result

        except FileNotFoundError:
            # CLI not installed - fall back to python -m execution
            result = subprocess.run(
                ["python", "-m", "charcoal"] + args,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                env=test_env,
                check=False,
            )

            cli_result = CliResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                exception=None,
            )

            if expect_success and result.returncode != 0:
                raise CliCommandError(args, cli_result)

            return cli_result


class CliResult:
    """Result from running a CLI command.

    Attributes:
        exit_code: The exit code from the command
        stdout: Standard output from the command
        stderr: Standard error from the command
        exception: Exception raised during Click execution (if using CliRunner)
    """

    def __init__(
        self,
        exit_code: int,
        stdout: str,
        stderr: str,
        exception: Exception | None = None,
    ) -> None:
        """Initialize a CLI result.

        Args:
            exit_code: The exit code from the command
            stdout: Standard output from the command
            stderr: Standard error from the command
            exception: Optional exception from Click execution
        """
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.exception = exception

    @property
    def success(self) -> bool:
        """Check if the command succeeded (exit code 0)."""
        return self.exit_code == 0

    @property
    def output(self) -> str:
        """Get combined stdout and stderr."""
        return self.stdout + self.stderr


class CliCommandError(Exception):
    """Exception raised when a CLI command fails unexpectedly.

    Attributes:
        cmd_args: The command arguments that were run
        result: The CliResult from the failed command
    """

    def __init__(self, args: list[str], result: CliResult) -> None:
        """Initialize the error.

        Args:
            args: The command arguments that were run
            result: The CliResult from the failed command
        """
        self.cmd_args = args
        self.result = result
        args_str = " ".join(args)
        message = (
            f"Command failed: gt {args_str}\n"
            f"Exit code: {result.exit_code}\n"
            f"Stdout: {result.stdout}\n"
            f"Stderr: {result.stderr}"
        )
        if result.exception:
            message += f"\nException: {result.exception}"
        super().__init__(message)
