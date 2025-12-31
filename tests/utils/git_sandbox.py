"""Utilities for creating and managing temporary Git repositories for testing.

This module provides the GitSandbox class which is analogous to the TypeScript
GitRepo class used in the original test suite. It creates temporary Git
repositories and provides helper methods for common Git operations.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class GitSandbox:
    """A temporary Git repository for testing purposes.

    This class creates a temporary directory with a Git repository and provides
    helper methods for common Git operations like creating commits, branches,
    and running Git commands. It automatically cleans up the temporary directory
    when used as a context manager.

    Example:
        with GitSandbox() as sandbox:
            sandbox.create_commit("Initial commit")
            sandbox.create_branch("feature")
    """

    def __init__(self, initial_branch: str = "main") -> None:
        """Initialize a new Git sandbox.

        Args:
            initial_branch: The name of the initial branch (default: "main")
        """
        self.temp_dir: tempfile.TemporaryDirectory[str] | None = None
        self.dir: Path | None = None
        self.initial_branch = initial_branch
        self._cleanup_on_exit = True

    def __enter__(self) -> GitSandbox:
        """Set up the temporary Git repository."""
        self.setup()
        return self

    def __exit__(self, *args: Any) -> None:
        """Clean up the temporary Git repository."""
        if self._cleanup_on_exit:
            self.cleanup()

    def setup(self) -> None:
        """Create and initialize the temporary Git repository."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir = Path(self.temp_dir.name)

        # Initialize Git repository with specified initial branch
        self.run_git_command(["init", "-b", self.initial_branch])

        # Configure git user for commits
        self.run_git_command(["config", "user.name", "Test User"])
        self.run_git_command(["config", "user.email", "test@example.com"])

    def cleanup(self) -> None:
        """Remove the temporary directory."""
        if self.temp_dir is not None:
            self.temp_dir.cleanup()
            self.temp_dir = None
            self.dir = None

    def disable_cleanup(self) -> None:
        """Disable automatic cleanup (useful for debugging)."""
        self._cleanup_on_exit = False

    @property
    def path(self) -> Path:
        """Get the path to the temporary repository."""
        if self.dir is None:
            raise RuntimeError("GitSandbox not initialized. Call setup() first.")
        return self.dir

    def run_git_command(
        self, args: list[str], check: bool = True, capture_output: bool = False
    ) -> subprocess.CompletedProcess[str]:
        """Run a Git command in the sandbox repository.

        Args:
            args: Git command arguments (without 'git' prefix)
            check: Whether to raise an exception on non-zero exit code
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess object with the command result

        Raises:
            RuntimeError: If sandbox not initialized
            subprocess.CalledProcessError: If check=True and command fails
        """
        if self.dir is None:
            raise RuntimeError("GitSandbox not initialized")

        return subprocess.run(
            ["git"] + args,
            cwd=self.dir,
            check=check,
            capture_output=capture_output,
            text=True,
        )

    def run_git_command_output(self, args: list[str]) -> str:
        """Run a Git command and return its stdout.

        Args:
            args: Git command arguments (without 'git' prefix)

        Returns:
            Stripped stdout from the command
        """
        result = self.run_git_command(args, check=True, capture_output=True)
        return result.stdout.strip()

    def create_file(
        self, filename: str, content: str = "", subdir: str | None = None
    ) -> Path:
        """Create a file in the repository.

        Args:
            filename: Name of the file to create
            content: Content to write to the file
            subdir: Optional subdirectory to create the file in

        Returns:
            Path to the created file
        """
        if subdir:
            file_path = self.path / subdir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            file_path = self.path / filename

        file_path.write_text(content)
        return file_path

    def create_commit(
        self, message: str, filename: str = "test.txt", add_all: bool = False
    ) -> None:
        """Create a commit with a test file.

        Args:
            message: Commit message
            filename: Name of file to create (default: "test.txt")
            add_all: If True, stage all changes; otherwise only stage the new file
        """
        # Create or update the file with commit message as content
        self.create_file(filename, message)

        # Stage the file
        if add_all:
            self.run_git_command(["add", "."])
        else:
            self.run_git_command(["add", filename])

        # Create commit
        self.run_git_command(["commit", "-m", message])

    def create_branch(self, name: str, checkout: bool = True) -> None:
        """Create a new branch.

        Args:
            name: Name of the branch to create
            checkout: Whether to checkout the branch after creating it
        """
        if checkout:
            self.run_git_command(["checkout", "-b", name])
        else:
            self.run_git_command(["branch", name])

    def checkout_branch(self, name: str) -> None:
        """Checkout an existing branch.

        Args:
            name: Name of the branch to checkout
        """
        self.run_git_command(["checkout", name])

    def current_branch(self) -> str:
        """Get the name of the current branch.

        Returns:
            Name of the current branch
        """
        return self.run_git_command_output(["branch", "--show-current"])

    def delete_branch(self, name: str, force: bool = True) -> None:
        """Delete a branch.

        Args:
            name: Name of the branch to delete
            force: Whether to force deletion (use -D instead of -d)
        """
        flag = "-D" if force else "-d"
        self.run_git_command(["branch", flag, name])

    def rename_branch(self, new_name: str) -> None:
        """Rename the current branch.

        Args:
            new_name: New name for the current branch
        """
        self.run_git_command(["branch", "-m", new_name])

    def get_repo_config_path(self) -> Path:
        """Get the path to the .graphite_repo_config file.

        Returns:
            Path to the config file
        """
        return self.path / ".git" / ".graphite_repo_config"

    def read_repo_config(self) -> dict[str, Any]:
        """Read and parse the .graphite_repo_config file.

        Returns:
            Parsed JSON config as a dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        config_path = self.get_repo_config_path()
        config: dict[str, Any] = json.loads(config_path.read_text())
        return config

    def write_repo_config(self, config: dict[str, Any]) -> None:
        """Write a config dictionary to .graphite_repo_config.

        Args:
            config: Configuration dictionary to write
        """
        config_path = self.get_repo_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(config, indent=2))

    def remove_repo_config(self) -> None:
        """Remove the .graphite_repo_config file if it exists."""
        config_path = self.get_repo_config_path()
        if config_path.exists():
            config_path.unlink()

    def get_user_config_path(self) -> Path:
        """Get the path to the .graphite_user_config file.

        Returns:
            Path to the user config file
        """
        return self.path / ".git" / ".graphite_user_config"

    def write_user_config(self, config: dict[str, Any]) -> None:
        """Write a config dictionary to .graphite_user_config.

        Args:
            config: Configuration dictionary to write
        """
        config_path = self.get_user_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(config, indent=2))

    def merge_branch(self, branch: str) -> None:
        """Merge another branch into the current branch.

        Args:
            branch: Name of the branch to merge
        """
        self.run_git_command(["merge", branch])
