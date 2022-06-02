import datetime
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class BasePgSchema(ABC):

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        raise NotImplementedError()

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError()


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
class PersonList(BasePgSchema):
    """Персона (используется в списке)."""

    id: uuid.UUID  # noqa: VNE003
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "PersonList":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict[str, Any]:
        dct = {"uuid": self.id, "full_name": self.name}
        return dct


@dataclass
class MovieDetail(BasePgSchema):
    """Фильм в онлайн-кинотеатре."""

    id: uuid.UUID  # noqa: VNE003
    imdb_rating: float
    title: str
    description: str
    age_rating: str
    access_type: str
    release_date: datetime.date

    genres_names: list[str]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]

    genre: list[GenreList]
    actors: list[PersonList]
    writers: list[PersonList]
    directors: list[PersonList]

    @staticmethod
    def _prepare_genres(data: dict) -> dict:
        genres: list[dict] = data["genre"] or []
        dct = {
            "genre": [GenreList.from_dict(genre) for genre in genres],
        }
        return dct

    @staticmethod
    def _prepare_persons(data: dict) -> dict:
        persons_types: tuple[str, ...] = ("actors", "writers", "directors")
        person_data_map: dict[str, dict] = {
            person_type: data[person_type] or []
            for person_type in persons_types
        }
        dct = {
            person_type: [PersonList.from_dict(person) for person in person_data]
            for person_type, person_data in person_data_map.items()
        }
        return dct

    @staticmethod
    def _prepare_fields(data: dict) -> dict:
        dct = {
            "id": data["id"],
            "imdb_rating": data["imdb_rating"],
            "access_type": data["access_type"],
            "title": data["title"],
            "description": data["description"],
            "age_rating": data["age_rating"],
            "release_date": data["release_date"],
            "genres_names": data["genres_names"] or [],
            "actors_names": data["actors_names"] or [],
            "writers_names": data["writers_names"] or [],
            "directors_names": data["directors_names"] or [],
        }
        dct.update(MovieDetail._prepare_genres(data))
        dct.update(MovieDetail._prepare_persons(data))
        return dct

    @classmethod
    def from_dict(cls, data: dict) -> "MovieDetail":
        dct = cls._prepare_fields(data)
        return cls(**dct)

    def _serialize_persons(self) -> dict:
        persons_types: tuple[str, ...] = ("actors", "writers", "directors")
        dct = {
            persons_type: [person.to_dict() for person in getattr(self, persons_type)]
            for persons_type in persons_types
        }
        return dct

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "uuid": self.id,
            "access_type": self.access_type,
            "imdb_rating": self.imdb_rating, "title": self.title, "description": self.description,
            "age_rating": self.age_rating,
            "release_date": self.release_date,
            "genres_names": self.genres_names,
            "actors_names": self.actors_names,
            "writers_names": self.writers_names,
            "directors_names": self.directors_names,
            "genre": [genre.to_dict() for genre in self.genre],
        }
        dct.update(self._serialize_persons())
        return dct


@dataclass
class GenreDetail(BasePgSchema):
    """Жанр у Фильма."""

    id: uuid.UUID  # noqa: VNE003
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "GenreDetail":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict[str, Any]:
        dct = {"uuid": self.id, "name": self.name}
        return dct


@dataclass
class MovieList(BasePgSchema):
    """Список Фильмов."""

    id: uuid.UUID  # noqa: VNE003
    title: str
    imdb_rating: float
    age_rating: str
    release_date: datetime.date

    @classmethod
    def from_dict(cls, data: dict) -> "MovieList":
        return cls(
            id=data["id"], title=data["title"], imdb_rating=data["imdb_rating"], age_rating=data["age_rating"],
            release_date=data["release_date"],
        )

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "uuid": self.id, "title": self.title, "imdb_rating": self.imdb_rating,
            "age_rating": self.age_rating, "release_date": self.release_date,
        }
        return dct


@dataclass
class PersonRoleFilm(BasePgSchema):
    """Роль Персоны со списком Фильмов."""

    role: str
    films: list[MovieList]

    @staticmethod
    def _prepare_fields(data: dict) -> dict:
        role = data["role"]
        dct = {
            "role": role,
            "films": [MovieList.from_dict(film) for film in data[role] or []],
        }
        return dct

    @classmethod
    def from_dict(cls, data: dict) -> "PersonRoleFilm":
        dct = cls._prepare_fields(data)
        return cls(**dct)

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "role": self.role,
            "films": [film.to_dict() for film in self.films],
        }
        return dct


@dataclass
class PersonFullDetail(BasePgSchema):
    """Персона (с разбиением фильмов по ролям)."""

    id: uuid.UUID  # noqa: VNE003
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
        dct = {"roles": roles}
        return dct

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
        dct = {
            "uuid": self.id,
            "full_name": self.full_name,
            "films_ids": self.films_ids,
            "roles": [role.to_dict() for role in self.roles],
        }
        return dct
