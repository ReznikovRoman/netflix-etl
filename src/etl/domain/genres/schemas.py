import uuid
from dataclasses import dataclass
from typing import Any

from etl.domain.schemas import BasePgSchema


@dataclass
class GenreList(BasePgSchema):
    """Genre list."""

    id: uuid.UUID
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "GenreList":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict[str, Any]:
        return {"uuid": self.id, "name": self.name}


@dataclass
class GenreDetail(BasePgSchema):
    """Genre detail."""

    id: uuid.UUID
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "GenreDetail":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict[str, Any]:
        return {"uuid": self.id, "name": self.name}
