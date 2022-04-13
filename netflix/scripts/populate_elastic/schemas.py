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
class PersonDetail(BasePgSchema):
    id: uuid.uuid4  # noqa: VNE003
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> 'PersonDetail':
        return cls(id=data['id'], name=data['name'])

    def to_dict(self) -> dict[str, Any]:
        dct = {"id": self.id, "name": self.name}
        return dct


@dataclass
class MovieDetail(BasePgSchema):
    id: uuid.uuid4  # noqa: VNE003
    imdb_rating: float
    title: str
    description: str
    genre: list[str]  # список жанров
    director: list[str]  # список режиссеров
    actors_names: str  # список актеров, разделенных запятыми
    writers_names: str  # список сценаристов, разделенных запятыми

    actors: list[PersonDetail]
    writers: list[PersonDetail]

    @staticmethod
    def _prepare_fields(data: dict) -> dict:
        actors = data['actors'] or []
        writers = data['writers'] or []
        dct = {
            'id': data['id'],
            'imdb_rating': data['imdb_rating'], 'title': data['title'], 'description': data['description'],
            'genre': data['genre'] or [],
            'director': data['director'] or [],
            'actors_names': data['actors_names'], 'writers_names': data['writers_names'],
            'actors': [PersonDetail.from_dict(actor) for actor in actors],
            'writers': [PersonDetail.from_dict(writer) for writer in writers],
        }
        return dct

    @classmethod
    def from_dict(cls, data: dict) -> 'MovieDetail':
        dct = cls._prepare_fields(data)
        return cls(**dct)

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "imdb_rating": self.imdb_rating, "title": self.title, "description": self.description,
            "genre": self.genre,
            "director": self.director, "actors_names": self.actors_names, "writers_names": self.writers_names,
            "actors": [actor.to_dict() for actor in self.actors],
            "writers": [writer.to_dict() for writer in self.writers],
        }
        return dct
