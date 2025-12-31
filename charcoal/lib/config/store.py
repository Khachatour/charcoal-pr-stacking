"""Configuration persistence layer."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from charcoal.lib.errors import ConfigError

from .models import RepoConfig, UserConfig

# Configuration file names (preserving backward compatibility with .graphite_* names)
REPO_CONFIG_FILENAME = ".graphite_repo_config"
USER_CONFIG_FILENAME = ".graphite_user_config"
USER_CONFIG_DIR = ".graphite"
USER_CONFIG_ALT_FILENAME = "config.json"


def get_repo_config_path(repo_root: Path) -> Path:
    """Get the path to the repository configuration file.

    The config file is stored in the .git directory to match TypeScript behavior.
    """
    return repo_root / ".git" / REPO_CONFIG_FILENAME


def get_user_config_path() -> Path:
    """Get the primary path to the user configuration file.

    Note: This returns the preferred location. Use _get_all_user_config_paths()
    for all possible locations during loading.
    """
    return Path.home() / USER_CONFIG_FILENAME


def _get_all_user_config_paths() -> list[Path]:
    """Get all possible user configuration file paths in order of preference.

    Returns a list of paths to check:
    1. ~/.graphite_user_config (primary)
    2. ~/.graphite/config.json (alternative for backward compatibility)
    """
    home = Path.home()
    return [
        home / USER_CONFIG_FILENAME,  # Primary location
        home / USER_CONFIG_DIR / USER_CONFIG_ALT_FILENAME,  # Alternative location
    ]


def load_repo_config(repo_root: Path) -> RepoConfig:
    """Load repository configuration with fallback to user config and defaults.

    Args:
        repo_root: Path to the repository root

    Returns:
        RepoConfig instance (may be default-initialized if no config exists)

    Raises:
        ConfigError: If the configuration file exists but is malformed
    """
    repo_config_path = get_repo_config_path(repo_root)

    # Try loading from repo config first
    if repo_config_path.exists():
        try:
            config_text = repo_config_path.read_text()
            return RepoConfig.model_validate_json(config_text)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Malformed JSON in {repo_config_path}: {e}")
        except ValidationError as e:
            raise ConfigError(f"Invalid configuration in {repo_config_path}: {e}")

    # Fallback to user config if repo config doesn't exist
    user_config_path = get_user_config_path()
    if user_config_path.exists():
        try:
            config_text = user_config_path.read_text()
            # User config might have repo-specific settings
            return RepoConfig.model_validate_json(config_text)
        except (json.JSONDecodeError, ValidationError):
            # If user config is invalid, just return defaults
            pass

    # Return default config
    return RepoConfig()


def save_repo_config(repo_root: Path, config: RepoConfig) -> None:
    """Save repository configuration to file.

    Args:
        repo_root: Path to the repository root
        config: RepoConfig instance to save
    """
    repo_config_path = get_repo_config_path(repo_root)

    # Ensure parent directory exists (.git directory)
    repo_config_path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize to JSON with indentation for readability
    config_json = config.model_dump_json(indent=2, exclude_none=True)

    # Write to file with restricted permissions (0o600 = owner read/write only)
    repo_config_path.write_text(config_json)
    repo_config_path.chmod(0o600)


def load_user_config() -> UserConfig:
    """Load user configuration from possible locations.

    Checks multiple locations in order of preference:
    1. ~/.graphite_user_config
    2. ~/.graphite/config.json

    Returns:
        UserConfig instance (may be default-initialized if no config exists)

    Raises:
        ConfigError: If the configuration file exists but is malformed
    """
    # Try all possible config locations in order
    for config_path in _get_all_user_config_paths():
        if config_path.exists():
            try:
                config_text = config_path.read_text()
                return UserConfig.model_validate_json(config_text)
            except json.JSONDecodeError as e:
                raise ConfigError(f"Malformed JSON in {config_path}: {e}")
            except ValidationError as e:
                raise ConfigError(f"Invalid configuration in {config_path}: {e}")

    # Return default config if no file exists
    return UserConfig()


def save_user_config(config: UserConfig) -> None:
    """Save user configuration to file.

    Args:
        config: UserConfig instance to save
    """
    user_config_path = get_user_config_path()

    # Ensure parent directory exists
    user_config_path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize to JSON with indentation for readability
    config_json = config.model_dump_json(indent=2, exclude_none=True)

    # Write to file with restricted permissions (0o600 = owner read/write only)
    user_config_path.write_text(config_json)
    user_config_path.chmod(0o600)


def graphite_initialized(repo_root: Path) -> bool:
    """Check if the repository is initialized (has trunk configured).

    Args:
        repo_root: Path to the repository root

    Returns:
        True if trunk is configured, False otherwise
    """
    config = load_repo_config(repo_root)
    return config.graphite_initialized()
