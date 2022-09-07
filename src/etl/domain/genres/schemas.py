import uuid
from dataclasses import dataclass
from typing import Any

from etl.domain.schemas import BasePgSchema


@dataclass
class GenreList(BasePgSchema):
    """Жанр (используется в списке)."""

    id: uuid.UUID  # noqa: VNE003
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "GenreList":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict[str, Any]:
        dct = {"uuid": self.id, "name": self.name}
        return dct


@dataclass
class GenreDetail(BasePgSchema):
    """Жанр у фильма."""

    id: uuid.UUID  # noqa: VNE003
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "GenreDetail":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict[str, Any]:
        dct = {"uuid": self.id, "name": self.name}
        return dct
