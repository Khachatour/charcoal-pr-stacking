"""Tests for the `gt repo init` command.

This test module verifies the repository initialization functionality, including:
- Setting the trunk branch
- Creating config files with correct structure and permissions
- Handling invalid trunk branches with fallback logic
- Error handling when trunk cannot be inferred
"""

from __future__ import annotations

import pytest

from tests.utils.cli_runner import CliCommandError, CliTestRunner
from tests.utils.git_sandbox import GitSandbox


class TestRepoInit:
    """Tests for the `gt repo init` command."""

    def test_can_run_repo_init(self) -> None:
        """Test that repo init can be run with explicit trunk branch."""
        with GitSandbox() as sandbox:
            # Create initial commit (required for branch to exist)
            sandbox.create_commit("Initial commit")

            # Remove config if it exists
            sandbox.remove_repo_config()

            # Create CLI runner
            runner = CliTestRunner(sandbox.path, use_subprocess=False)

            # Run repo init
            result = runner.run_command(["repo", "init", "--trunk", "main"])

            # Verify command succeeded
            assert result.success, f"Command failed: {result.output}"

            # Verify config file was created
            config_path = sandbox.get_repo_config_path()
            assert config_path.exists(), "Config file was not created"

            # Verify config contains correct trunk
            config = sandbox.read_repo_config()
            assert config["trunk"] == "main", f"Expected trunk=main, got {config}"

    def test_config_file_location(self) -> None:
        """Test that config file is created in .git/ directory."""
        with GitSandbox() as sandbox:
            sandbox.create_commit("Initial commit")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)
            runner.run_command(["repo", "init", "--trunk", "main"])

            # Verify config is in .git/.graphite_repo_config
            config_path = sandbox.path / ".git" / ".graphite_repo_config"
            assert config_path.exists(), "Config not in expected location"
            assert config_path.is_file(), "Config path is not a file"

    def test_config_file_permissions(self) -> None:
        """Test that config file has correct permissions (0o600)."""
        with GitSandbox() as sandbox:
            sandbox.create_commit("Initial commit")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)
            runner.run_command(["repo", "init", "--trunk", "main"])

            config_path = sandbox.get_repo_config_path()
            # Get file permissions
            stat_info = config_path.stat()
            permissions = stat_info.st_mode & 0o777

            # Should be 0o600 (read/write for owner only)
            assert permissions == 0o600, (
                f"Expected permissions 0o600, got {oct(permissions)}"
            )

    def test_config_file_structure(self) -> None:
        """Test that config file contains valid JSON with expected fields."""
        with GitSandbox() as sandbox:
            sandbox.create_commit("Initial commit")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)
            runner.run_command(["repo", "init", "--trunk", "main"])

            config = sandbox.read_repo_config()

            # Verify it's a dict
            assert isinstance(config, dict), "Config is not a dictionary"

            # Verify trunk is present
            assert "trunk" in config, "Config missing 'trunk' field"
            assert config["trunk"] == "main", "Trunk has wrong value"

    def test_falls_back_to_main_if_nonexistent_branch_passed(self) -> None:
        """Test that init falls back to 'main' when invalid trunk is provided."""
        with GitSandbox() as sandbox:
            # Create initial commit on main
            sandbox.create_commit("Initial commit")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)

            # Try to init with non-existent branch in non-interactive mode
            runner.run_command(
                ["repo", "init", "--trunk", "random", "--no-interactive"]
            )

            # Should fall back to main
            config = sandbox.read_repo_config()
            assert config["trunk"] == "main", (
                f"Expected fallback to main, got {config['trunk']}"
            )

    def test_falls_back_to_master_if_no_main(self) -> None:
        """Test that init falls back to 'master' when 'main' doesn't exist."""
        with GitSandbox(initial_branch="master") as sandbox:
            # Create initial commit on master
            sandbox.create_commit("Initial commit")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)

            # Try to init with non-existent branch in non-interactive mode
            runner.run_command(
                ["repo", "init", "--trunk", "random", "--no-interactive"]
            )

            # Should fall back to master (since main doesn't exist)
            config = sandbox.read_repo_config()
            assert config["trunk"] == "master", (
                f"Expected fallback to master, got {config['trunk']}"
            )

    def test_cannot_set_invalid_trunk_if_trunk_cannot_be_inferred(self) -> None:
        """Test that init fails when invalid trunk is given and no fallback exists."""
        with GitSandbox() as sandbox:
            # Create initial commit on main
            sandbox.create_commit("Initial commit")

            # Rename main to something else (so main/master don't exist)
            sandbox.rename_branch("main2")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)

            # Try to init with non-existent branch - should fail
            with pytest.raises(CliCommandError) as exc_info:
                runner.run_command(
                    ["repo", "init", "--trunk", "random", "--no-interactive"]
                )

            # Verify the command failed
            assert exc_info.value.result.exit_code != 0, "Expected non-zero exit code"

    def test_reinitializing_repo_updates_config(self) -> None:
        """Test that running init on an already initialized repo updates the config."""
        with GitSandbox() as sandbox:
            sandbox.create_commit("Initial commit")
            sandbox.create_branch("develop")
            sandbox.checkout_branch("main")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)

            # Initialize with main
            runner.run_command(["repo", "init", "--trunk", "main"])
            config = sandbox.read_repo_config()
            assert config["trunk"] == "main"

            # Reinitialize with develop
            runner.run_command(["repo", "init", "--trunk", "develop"])
            config = sandbox.read_repo_config()
            assert config["trunk"] == "develop"

    def test_init_with_existing_trunk(self) -> None:
        """Test initializing with a trunk that exists."""
        with GitSandbox() as sandbox:
            sandbox.create_commit("Initial commit")

            # Create a custom trunk branch
            sandbox.create_branch("trunk")
            sandbox.checkout_branch("main")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)

            # Initialize with the custom trunk
            runner.run_command(["repo", "init", "--trunk", "trunk"])

            config = sandbox.read_repo_config()
            assert config["trunk"] == "trunk"

    def test_multiple_commits_before_init(self) -> None:
        """Test init works correctly with multiple commits."""
        with GitSandbox() as sandbox:
            # Create multiple commits
            sandbox.create_commit("First commit")
            sandbox.create_commit("Second commit", "file2.txt")
            sandbox.create_commit("Third commit", "file3.txt")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)
            runner.run_command(["repo", "init", "--trunk", "main"])

            config = sandbox.read_repo_config()
            assert config["trunk"] == "main"

    def test_init_with_branches_already_created(self) -> None:
        """Test init works when branches already exist in the repo."""
        with GitSandbox() as sandbox:
            sandbox.create_commit("Initial commit")

            # Create some branches
            sandbox.create_branch("feature-1")
            sandbox.create_commit("Feature 1 work")
            sandbox.checkout_branch("main")

            sandbox.create_branch("feature-2")
            sandbox.create_commit("Feature 2 work")
            sandbox.checkout_branch("main")

            runner = CliTestRunner(sandbox.path, use_subprocess=False)
            runner.run_command(["repo", "init", "--trunk", "main"])

            config = sandbox.read_repo_config()
            assert config["trunk"] == "main"

            # Verify branches still exist
            assert sandbox.current_branch() == "main"
            result = sandbox.run_git_command_output(["branch", "--list"])
            assert "feature-1" in result
            assert "feature-2" in result
