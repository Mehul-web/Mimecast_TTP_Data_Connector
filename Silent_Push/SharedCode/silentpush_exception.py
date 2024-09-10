"""This File contains custom Exception class for Silentpush."""


class SilentPushException(Exception):
    """Exception class to handle Silentpush exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Silentpush exception with custom message."""
        super().__init__(message)


class SilentPushTimeoutException(Exception):
    """Exception class to handle Silentpush exception.

    Args:
        Exception (string): will print exception message.
    """

    def __init__(self, message=None) -> None:
        """Initialize custom Silentpush exception with custom message."""
        super().__init__(message)
