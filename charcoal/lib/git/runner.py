"""Git command execution via subprocess."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from charcoal.lib.errors import CommandFailedError, CommandKilledError


@dataclass
class GitRunner:
    """Abstraction for running Git commands via subprocess.

    This class provides a clean interface for executing Git commands,
    handling errors consistently, and capturing output.

    Attributes:
        repo_root: The root directory of the git repository to operate on.
    """

    repo_root: Path

    def run(
        self,
        *args: str,
        check: bool = True,
        no_trim: bool = False,
    ) -> str:
        """Execute a git command and return its stdout.

        Args:
            *args: Git command arguments (e.g., 'status', '--short')
            check: If True, raise an exception on non-zero exit codes
            no_trim: If True, don't trim whitespace from the output

        Returns:
            The stdout output from the git command (trimmed by default)

        Raises:
            CommandKilledError: If the process is killed by a signal
            CommandFailedError: If the process exits with non-zero status and check=True
        """
        cmd = ["git", *args]

        try:
            proc = subprocess.run(
                cmd,
                cwd=self.repo_root,
                text=True,
                encoding="utf-8",
                errors="replace",  # Handle invalid UTF-8 gracefully
                capture_output=True,
            )
        except Exception as e:
            # Handle system-level errors (e.g., git not found)
            raise RuntimeError(f"Failed to execute git command: {e}") from e

        # Check if process was killed by a signal (negative return code)
        if proc.returncode < 0:
            # Negative return codes indicate signal termination
            signal_num = -proc.returncode
            raise CommandKilledError(cmd, signal_num)

        # Command succeeded
        if proc.returncode == 0:
            output = proc.stdout
            return output if no_trim else output.strip()

        # Command failed but we're ignoring errors
        if not check:
            return ""

        # Command failed and we're not ignoring errors
        raise CommandFailedError(
            cmd=cmd,
            exit_code=proc.returncode,
            stderr=proc.stderr,
            stdout=proc.stdout,
        )

    def run_and_split_lines(
        self,
        *args: str,
        check: bool = True,
    ) -> list[str]:
        """Execute a git command and return output split into non-empty lines.

        Args:
            *args: Git command arguments
            check: If True, raise an exception on non-zero exit codes

        Returns:
            List of non-empty lines from stdout
        """
        output = self.run(*args, check=check)
        return [line for line in output.split("\n") if line]
