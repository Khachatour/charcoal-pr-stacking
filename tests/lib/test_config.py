"""Tests for configuration management."""

import json
from pathlib import Path

import pytest

from charcoal.lib.config import (
    AlternativeProfile,
    GtiConfig,
    RepoConfig,
    UserConfig,
    get_repo_config_path,
    get_user_config_path,
    graphite_initialized,
    load_repo_config,
    load_user_config,
    save_repo_config,
    save_user_config,
)
from charcoal.lib.errors import ConfigError


class TestRepoConfig:
    """Tests for RepoConfig model."""

    def test_default_initialization(self):
        """Test that RepoConfig can be initialized with defaults."""
        config = RepoConfig()
        assert config.host is None
        assert config.owner is None
        assert config.name is None
        assert config.trunk is None
        assert config.remote is None
        assert config.lastFetchedPRInfoMs is None
        assert config.isGithubIntegrationEnabled is None

    def test_full_repo_property(self):
        """Test the full_repo computed property."""
        # With both owner and name
        config = RepoConfig(owner="myorg", name="myrepo")
        assert config.full_repo == "myorg/myrepo"

        # With only owner
        config = RepoConfig(owner="myorg")
        assert config.full_repo is None

        # With only name
        config = RepoConfig(name="myrepo")
        assert config.full_repo is None

        # With neither
        config = RepoConfig()
        assert config.full_repo is None

    def test_get_remote(self):
        """Test get_remote method."""
        # With configured remote
        config = RepoConfig(remote="upstream")
        assert config.get_remote() == "upstream"

        # Without configured remote (default)
        config = RepoConfig()
        assert config.get_remote() == "origin"

    def test_get_is_github_integration_enabled(self):
        """Test get_is_github_integration_enabled method."""
        # Explicitly enabled
        config = RepoConfig(isGithubIntegrationEnabled=True)
        assert config.get_is_github_integration_enabled() is True

        # Explicitly disabled
        config = RepoConfig(isGithubIntegrationEnabled=False)
        assert config.get_is_github_integration_enabled() is False

        # Not set (default to True)
        config = RepoConfig()
        assert config.get_is_github_integration_enabled() is True

    def test_graphite_initialized(self):
        """Test graphite_initialized method."""
        # With trunk set
        config = RepoConfig(trunk="main")
        assert config.graphite_initialized() is True

        # Without trunk
        config = RepoConfig()
        assert config.graphite_initialized() is False


class TestUserConfig:
    """Tests for UserConfig model."""

    def test_default_initialization(self):
        """Test that UserConfig can be initialized with defaults."""
        config = UserConfig()
        assert config.branchPrefix is None
        assert config.branchDate is None
        assert config.branchReplacement is None
        assert config.tips is None
        assert config.editor is None
        assert config.pager is None
        assert config.restackCommitterDateIsAuthorDate is None
        assert config.submitIncludeCommitMessages is None

    def test_branch_replacement_validation(self):
        """Test that branchReplacement only accepts valid values."""
        # Valid values
        UserConfig(branchReplacement="_")
        UserConfig(branchReplacement="-")
        UserConfig(branchReplacement="")

        # Invalid value should raise validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            UserConfig(branchReplacement="invalid")

    def test_gti_configs(self):
        """Test gtiConfigs with proper GtiConfig models."""
        # Valid gtiConfigs
        config = UserConfig(
            gtiConfigs=[
                GtiConfig(key="foo", value="bar"),
                GtiConfig(key="baz", value="qux"),
            ]
        )
        assert len(config.gtiConfigs) == 2
        assert config.gtiConfigs[0].key == "foo"
        assert config.gtiConfigs[0].value == "bar"
        assert config.gtiConfigs[1].key == "baz"
        assert config.gtiConfigs[1].value == "qux"

    def test_alternative_profiles(self):
        """Test alternativeProfiles with proper AlternativeProfile models."""
        # Valid alternativeProfiles
        config = UserConfig(
            alternativeProfiles=[
                AlternativeProfile(name="default", hostPrefix=""),
                AlternativeProfile(name="staging", hostPrefix="staging"),
            ]
        )
        assert len(config.alternativeProfiles) == 2
        assert config.alternativeProfiles[0].name == "default"
        assert config.alternativeProfiles[0].hostPrefix == ""
        assert config.alternativeProfiles[1].name == "staging"
        assert config.alternativeProfiles[1].hostPrefix == "staging"


class TestGtiConfig:
    """Tests for GtiConfig model."""

    def test_initialization(self):
        """Test that GtiConfig requires key and value."""
        config = GtiConfig(key="test_key", value="test_value")
        assert config.key == "test_key"
        assert config.value == "test_value"

    def test_missing_fields(self):
        """Test that GtiConfig requires both fields."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            GtiConfig(key="only_key")  # type: ignore
        with pytest.raises(Exception):  # Pydantic ValidationError
            GtiConfig(value="only_value")  # type: ignore


class TestAlternativeProfile:
    """Tests for AlternativeProfile model."""

    def test_initialization(self):
        """Test that AlternativeProfile requires name and hostPrefix."""
        profile = AlternativeProfile(name="prod", hostPrefix="prod")
        assert profile.name == "prod"
        assert profile.hostPrefix == "prod"

    def test_missing_fields(self):
        """Test that AlternativeProfile requires both fields."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            AlternativeProfile(name="only_name")  # type: ignore
        with pytest.raises(Exception):  # Pydantic ValidationError
            AlternativeProfile(hostPrefix="only_prefix")  # type: ignore


class TestConfigPersistence:
    """Tests for configuration persistence functions."""

    def test_get_repo_config_path(self, tmp_path):
        """Test repo config path resolution."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        config_path = get_repo_config_path(repo_root)
        assert config_path == repo_root / ".graphite_repo_config"

    def test_get_user_config_path(self):
        """Test user config path resolution."""
        config_path = get_user_config_path()
        assert config_path == Path.home() / ".graphite_user_config"

    def test_save_and_load_repo_config(self, tmp_path):
        """Test saving and loading repository config."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        # Create and save config
        config = RepoConfig(
            trunk="main",
            remote="origin",
            owner="testorg",
            name="testrepo",
            isGithubIntegrationEnabled=True,
        )
        save_repo_config(repo_root, config)

        # Verify file exists and has correct permissions
        config_path = get_repo_config_path(repo_root)
        assert config_path.exists()
        assert config_path.stat().st_mode & 0o777 == 0o600

        # Load and verify
        loaded_config = load_repo_config(repo_root)
        assert loaded_config.trunk == "main"
        assert loaded_config.remote == "origin"
        assert loaded_config.owner == "testorg"
        assert loaded_config.name == "testrepo"
        assert loaded_config.isGithubIntegrationEnabled is True

    def test_load_repo_config_defaults(self, tmp_path):
        """Test loading repo config when file doesn't exist."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        # Should return default config
        config = load_repo_config(repo_root)
        assert config.trunk is None
        assert config.remote is None

    def test_load_repo_config_malformed_json(self, tmp_path):
        """Test loading repo config with malformed JSON."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        config_path = get_repo_config_path(repo_root)
        config_path.write_text("{ invalid json }")

        with pytest.raises(ConfigError) as exc_info:
            load_repo_config(repo_root)
        # Should raise ConfigError with message about invalid JSON
        error_msg = str(exc_info.value)
        assert "Invalid configuration" in error_msg or "Malformed JSON" in error_msg

    def test_save_and_load_user_config(self, tmp_path, monkeypatch):
        """Test saving and loading user config."""
        # Mock home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))

        # Create and save config
        config = UserConfig(
            branchPrefix="user/",
            branchDate=True,
            branchReplacement="-",
            tips=False,
            editor="vim",
        )
        save_user_config(config)

        # Verify file exists and has correct permissions
        config_path = fake_home / ".graphite_user_config"
        assert config_path.exists()
        assert config_path.stat().st_mode & 0o777 == 0o600

        # Load and verify
        loaded_config = load_user_config()
        assert loaded_config.branchPrefix == "user/"
        assert loaded_config.branchDate is True
        assert loaded_config.branchReplacement == "-"
        assert loaded_config.tips is False
        assert loaded_config.editor == "vim"

    def test_load_user_config_defaults(self, tmp_path, monkeypatch):
        """Test loading user config when file doesn't exist."""
        # Mock home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))

        # Should return default config
        config = load_user_config()
        assert config.branchPrefix is None
        assert config.editor is None

    def test_load_user_config_malformed_json(self, tmp_path, monkeypatch):
        """Test loading user config with malformed JSON."""
        # Mock home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))

        config_path = fake_home / ".graphite_user_config"
        config_path.write_text("{ invalid json }")

        with pytest.raises(ConfigError) as exc_info:
            load_user_config()
        # Should raise ConfigError with message about invalid JSON
        error_msg = str(exc_info.value)
        assert "Invalid configuration" in error_msg or "Malformed JSON" in error_msg

    def test_load_user_config_alternative_location(self, tmp_path, monkeypatch):
        """Test loading user config from ~/.graphite/config.json."""
        # Mock home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))

        # Create config in alternative location
        graphite_dir = fake_home / ".graphite"
        graphite_dir.mkdir()
        alt_config_path = graphite_dir / "config.json"

        config = UserConfig(
            branchPrefix="alt/",
            editor="emacs",
        )
        alt_config_path.write_text(config.model_dump_json(indent=2, exclude_none=True))

        # Load and verify
        loaded_config = load_user_config()
        assert loaded_config.branchPrefix == "alt/"
        assert loaded_config.editor == "emacs"

    def test_load_user_config_primary_takes_precedence(self, tmp_path, monkeypatch):
        """Test that primary location takes precedence over alternative."""
        # Mock home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))

        # Create config in both locations
        primary_config = UserConfig(branchPrefix="primary/", editor="vim")
        primary_path = fake_home / ".graphite_user_config"
        primary_json = primary_config.model_dump_json(indent=2, exclude_none=True)
        primary_path.write_text(primary_json)

        graphite_dir = fake_home / ".graphite"
        graphite_dir.mkdir()
        alt_config = UserConfig(branchPrefix="alt/", editor="emacs")
        alt_path = graphite_dir / "config.json"
        alt_path.write_text(alt_config.model_dump_json(indent=2, exclude_none=True))

        # Load and verify primary location is used
        loaded_config = load_user_config()
        assert loaded_config.branchPrefix == "primary/"
        assert loaded_config.editor == "vim"

    def test_graphite_initialized_function(self, tmp_path):
        """Test graphite_initialized helper function."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        # Initially not initialized
        assert graphite_initialized(repo_root) is False

        # Save config with trunk
        config = RepoConfig(trunk="main")
        save_repo_config(repo_root, config)

        # Now initialized
        assert graphite_initialized(repo_root) is True

    def test_config_exclude_none(self, tmp_path):
        """Test that None values are excluded from saved JSON."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        # Create config with only some fields set
        config = RepoConfig(trunk="main", remote="origin")
        save_repo_config(repo_root, config)

        # Load raw JSON and verify None fields are not present
        config_path = get_repo_config_path(repo_root)
        saved_json = json.loads(config_path.read_text())
        assert "trunk" in saved_json
        assert "remote" in saved_json
        assert "owner" not in saved_json  # None value excluded
        assert "name" not in saved_json  # None value excluded

    def test_config_json_formatting(self, tmp_path):
        """Test that saved JSON is properly formatted."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        config = RepoConfig(trunk="main")
        save_repo_config(repo_root, config)

        # Verify JSON is indented (readable)
        config_path = get_repo_config_path(repo_root)
        saved_text = config_path.read_text()
        assert "\n" in saved_text  # Should have newlines (indented)
        assert saved_text.count("\n") > 1  # Should be multi-line
