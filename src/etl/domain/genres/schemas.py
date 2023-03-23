from dataclasses import dataclass
from typing import Any

from etl.domain.schemas import PgSchema


@dataclass
class GenreList(PgSchema):
    """Genre list."""

    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "GenreList":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict[str, Any]:
        return {"uuid": self.id, "name": self.name}


@dataclass
class GenreDetail(PgSchema):
    """Genre detail."""

    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "GenreDetail":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict[str, Any]:
        return {"uuid": self.id, "name": self.name}
