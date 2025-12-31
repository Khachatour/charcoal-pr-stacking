"""Configuration models using Pydantic."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GtiConfig(BaseModel):
    """GTI configuration entry."""

    key: str
    value: str


class AlternativeProfile(BaseModel):
    """Alternative profile configuration."""

    name: str
    hostPrefix: str  # noqa: N815


class RepoConfig(BaseModel):
    """Repository-specific configuration."""

    # ruff: noqa: N815 - mixedCase names match TypeScript config for compatibility
    host: str | None = None
    owner: str | None = None
    name: str | None = None
    trunk: str | None = None
    remote: str | None = None
    lastFetchedPRInfoMs: int | None = None  # noqa: N815
    isGithubIntegrationEnabled: bool | None = None  # noqa: N815

    @property
    def full_repo(self) -> str | None:
        """Get the full repository name (owner/name)."""
        if self.owner and self.name:
            return f"{self.owner}/{self.name}"
        return None

    def get_remote(self) -> str:
        """Get the configured remote or default to 'origin'."""
        return self.remote or "origin"

    def get_is_github_integration_enabled(self) -> bool:
        """Get whether GitHub integration is enabled (default: True)."""
        if self.isGithubIntegrationEnabled is not None:
            return self.isGithubIntegrationEnabled
        return True

    def graphite_initialized(self) -> bool:
        """Check if the repository is initialized (has trunk set)."""
        return self.trunk is not None


class UserConfig(BaseModel):
    """User-specific configuration."""

    # ruff: noqa: N815 - mixedCase names match TypeScript config for compatibility
    branchPrefix: str | None = None  # noqa: N815
    branchDate: bool | None = None  # noqa: N815
    branchReplacement: str | None = Field(default=None, pattern=r"^(_|-|)$")  # noqa: N815
    tips: bool | None = None
    editor: str | None = None
    pager: str | None = None
    restackCommitterDateIsAuthorDate: bool | None = None  # noqa: N815
    submitIncludeCommitMessages: bool | None = None  # noqa: N815
    connectCliToLocalServer: bool | None = None  # noqa: N815
    gtiConfigs: list[GtiConfig] | None = None  # noqa: N815
    alternativeProfiles: list[AlternativeProfile] | None = None  # noqa: N815
