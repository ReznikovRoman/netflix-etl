import datetime
import uuid
from dataclasses import dataclass
from typing import Any

from etl.domain.genres.schemas import GenreList
from etl.domain.schemas import BasePgSchema


@dataclass
class MoviePersonList(BasePgSchema):
    """Person (used in the movie list)."""

    id: uuid.UUID
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "MoviePersonList":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict[str, Any]:
        return {"uuid": self.id, "full_name": self.name}


@dataclass
class MovieDetail(BasePgSchema):
    """Movie detail."""

    id: uuid.UUID
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
    actors: list[MoviePersonList]
    writers: list[MoviePersonList]
    directors: list[MoviePersonList]

    @staticmethod
    def _prepare_genres(data: dict) -> dict:
        genres: list[dict] = data["genre"] or []
        return {
            "genre": [GenreList.from_dict(genre) for genre in genres],
        }

    @staticmethod
    def _prepare_persons(data: dict) -> dict:
        persons_types: tuple[str, ...] = ("actors", "writers", "directors")
        person_data_map: dict[str, dict] = {
            person_type: data[person_type] or []
            for person_type in persons_types
        }
        return {
            person_type: [MoviePersonList.from_dict(person) for person in person_data]
            for person_type, person_data in person_data_map.items()
        }

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
        return {
            persons_type: [person.to_dict() for person in getattr(self, persons_type)]
            for persons_type in persons_types
        }

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
class MovieList(BasePgSchema):
    """Movie list."""

    id: uuid.UUID
    title: str
    imdb_rating: float
    age_rating: str
    release_date: datetime.date
    access_type: str

    @classmethod
    def from_dict(cls, data: dict) -> "MovieList":
        return cls(
            id=data["id"], title=data["title"], imdb_rating=data["imdb_rating"], age_rating=data["age_rating"],
            release_date=data["release_date"], access_type=data["access_type"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.id, "title": self.title, "imdb_rating": self.imdb_rating,
            "age_rating": self.age_rating, "release_date": self.release_date, "access_type": self.access_type,
        }
