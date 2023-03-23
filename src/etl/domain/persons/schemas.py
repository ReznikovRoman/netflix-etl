import uuid
from dataclasses import dataclass
from typing import Any

from etl.domain.filmworks.schemas import MovieList
from etl.domain.schemas import BasePgSchema, PgSchema


@dataclass
class PersonRoleFilm(BasePgSchema):
    """Person role with movie list."""

    role: str
    films: list[MovieList]

    @staticmethod
    def _prepare_fields(data: dict) -> dict:
        role = data["role"]
        return {
            "role": role,
            "films": [MovieList.from_dict(film) for film in data[role] or []],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PersonRoleFilm":
        dct = cls._prepare_fields(data)
        return cls(**dct)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "films": [film.to_dict() for film in self.films],
        }


@dataclass
class PersonFullDetail(PgSchema):
    """Person full detail (with films by roles)."""

    full_name: str
    films_ids: list[uuid.UUID]
    roles: list[PersonRoleFilm]

    @staticmethod
    def _prepare_roles(data: dict) -> dict:
        persons_types: tuple[str, ...] = ("actor", "writer", "director")
        roles = [
            PersonRoleFilm.from_dict({"role": person_type, person_type: data[person_type]})
            for person_type in persons_types
        ]
        return {"roles": roles}

    @staticmethod
    def _prepare_fields(data: dict) -> dict:
        dct = {
            "id": data["id"],
            "full_name": data["full_name"],
            "films_ids": data["films_ids"] or [],
        }
        dct.update(PersonFullDetail._prepare_roles(data))
        return dct

    @classmethod
    def from_dict(cls, data: dict) -> "PersonFullDetail":
        dct = cls._prepare_fields(data)
        return cls(**dct)

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.id,
            "full_name": self.full_name,
            "films_ids": self.films_ids,
            "roles": [role.to_dict() for role in self.roles],
        }
