from typing import ClassVar


class NetflixETLError(Exception):
    """Netflix ETL base exception."""

    message: ClassVar[str]
    code: ClassVar[str]


class ImproperlyConfiguredError(NetflixETLError):
    """Service was configured improperly."""

    message: ClassVar[str] = "Improperly configured service"
    code: ClassVar[str] = "improperly_configured"

    def __init__(self, message: str | None = None):
        msg = self.message
        if message is not None:
            msg = message
        self.msg = msg

    def __str__(self) -> str:
        return self.message
