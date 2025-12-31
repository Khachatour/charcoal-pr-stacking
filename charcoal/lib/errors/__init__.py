"""Error definitions and exception handling."""


class UserFacingError(Exception):
    """Base class for errors that should be shown cleanly to users."""

    def __init__(self, message: str):
        super().__init__(message)
        self.name = self.__class__.__name__


class CommandFailedError(UserFacingError):
    """Raised when a subprocess command exits with a non-zero status."""

    def __init__(self, cmd: list[str], exit_code: int, stderr: str, stdout: str = ""):
        self.cmd = cmd
        self.exit_code = exit_code
        self.stderr = stderr
        self.stdout = stdout

        message_parts = [
            f"Command failed with exit code {exit_code}:",
            " ".join(cmd),
        ]

        if stdout:
            message_parts.append(stdout)

        if stderr:
            message_parts.append(stderr)

        super().__init__("\n".join(message_parts))


class CommandKilledError(UserFacingError):
    """Raised when a subprocess command is killed by a signal."""

    def __init__(self, cmd: list[str], signal: int):
        self.cmd = cmd
        self.signal = signal

        message_parts = [
            f"Command killed with signal {signal}:",
            " ".join(cmd),
        ]

        super().__init__("\n".join(message_parts))


class ConfigError(UserFacingError):
    """Raised when there's an issue with configuration."""
    pass


class GitError(UserFacingError):
    """Raised for git-specific failures."""
    pass


class PreconditionsFailedError(UserFacingError):
    """Raised when preconditions for an operation are not met."""
    pass
