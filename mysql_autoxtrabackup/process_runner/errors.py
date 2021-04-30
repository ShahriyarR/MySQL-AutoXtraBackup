import logging

logger = logging.getLogger(__name__)

# TODO: use these errors in the future - keeping it for future


def log_error(expression: str, message: str) -> None:
    logger.error("FAILED: " + expression + " " + message)


class Error(Exception):
    """Base class for all sort of exceptions"""


class ExternalCommandFailed(Error):
    """
    Exception raised for external tool/command fails.
    """

    def __init__(self, expression: str, message: str) -> None:
        self.expression = expression
        self.message = message
        log_error(self.expression, self.message)


class FullBackupFailed(Error):
    """
    Exception raised for full backup error.
    """

    def __init__(self, expression: str, message: str) -> None:
        self.expression = expression
        self.message = message
        log_error(self.expression, self.message)


class IncrementalBackupFailed(Error):
    """
    Exception raised for incremental backup error.
    """

    def __init__(self, expression: str, message: str) -> None:
        self.expression = expression
        self.message = message
        log_error(self.expression, self.message)


class SomethingWentWrong(Error):
    """
    Exception raised for all general failed commands.
    """

    def __init__(self, expression: str, message: str) -> None:
        self.expression = expression
        self.message = message
        log_error(self.expression, self.message)
