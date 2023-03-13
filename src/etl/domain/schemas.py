from abc import ABC, abstractmethod
from typing import Any, TypeVar

TPgSchema = TypeVar("TPgSchema", bound="BasePgSchema")


class BasePgSchema(ABC):
    """Base Postgres schema."""

    @classmethod
    @abstractmethod
    def from_dict(cls: type[TPgSchema], data: dict) -> TPgSchema:
        """Deserialize input data."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize object."""
