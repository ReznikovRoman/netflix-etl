from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar

TPgSchema = TypeVar("TPgSchema", bound="BasePgSchema")


class BasePgSchema(ABC):
    """Базовая схема данных из Postgres."""

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[TPgSchema], data: dict) -> TPgSchema:
        """Десериализация объекта."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Сериализация объекта."""
