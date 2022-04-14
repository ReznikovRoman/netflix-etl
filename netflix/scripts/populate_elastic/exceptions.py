from typing import ClassVar


class ETLError(Exception):
    """Ошибка в сервисе ETL."""

    message: ClassVar[str]
    code: ClassVar[str]


class ImproperlyConfiguredError(ETLError):
    """Неверная конфигурация."""

    message: ClassVar[str] = "Improperly configured service"
    code: ClassVar[str] = "improperly_configured"

    def __init__(self, message: str | None = None):
        msg = self.message
        if message is not None:
            msg = message
        self.msg = msg

    def __str__(self) -> str:
        return self.message
