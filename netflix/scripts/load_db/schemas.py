from __future__ import annotations

import datetime
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from scripts.load_db.constants import FILMWORK_TYPE_SQLITE_TO_PG_MAP


if TYPE_CHECKING:
    from movies_types import PgSchema, SQLiteSchemaClass


class BasePgSchema(ABC):

    @abstractmethod
    def to_tuple(self) -> tuple:
        raise NotImplemented  # noqa: F901

    @staticmethod
    @abstractmethod
    def db_tablename() -> str:
        raise NotImplemented  # noqa: F901

    @staticmethod
    @abstractmethod
    def db_fieldnames() -> tuple[str, ...]:
        raise NotImplemented  # noqa: F901


class BaseSQLiteSchema(ABC):

    @abstractmethod
    def to_pg(self):
        raise NotImplemented  # noqa: F901


@dataclass
class Filmwork:
    title: str
    type: str
    creation_date: datetime.date | None
    rating: float | None
    description: str | None
    file_path: str | None


@dataclass
class FilmworkPg(BasePgSchema, Filmwork):
    id: uuid.uuid4
    created: datetime.datetime
    modified: datetime.datetime

    def _prepare_fields(self) -> tuple:
        return (
            self.id, self.title, self.description or "", self.creation_date, self.rating,
            FILMWORK_TYPE_SQLITE_TO_PG_MAP[self.type],
            self.created, self.modified, self.file_path,
        )

    def to_tuple(self) -> tuple:
        return self._prepare_fields()

    @staticmethod
    def db_tablename() -> str:
        return "content.film_work"

    @staticmethod
    def db_fieldnames() -> tuple[str, ...]:
        return "id", "title", "description", "creation_date", "rating", "type", "created", "modified", "file_path"


@dataclass
class FilmworkSQLite(BaseSQLiteSchema, Filmwork):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def to_pg(self) -> FilmworkPg:
        return FilmworkPg(
            id=self.id, title=self.title, type=self.type, rating=self.rating, description=self.description,
            file_path=self.file_path, creation_date=self.creation_date,
            created=self.created_at, modified=self.updated_at,
        )


@dataclass
class Genre:
    name: str
    description: str | None


@dataclass
class GenrePg(BasePgSchema, Genre):
    id: uuid.uuid4
    created: datetime.datetime | None
    modified: datetime.datetime | None

    def _prepare_fields(self) -> tuple:
        return self.id, self.name, self.description or "", self.created, self.modified

    def to_tuple(self) -> tuple:
        return self._prepare_fields()

    @staticmethod
    def db_tablename() -> str:
        return "content.genre"

    @staticmethod
    def db_fieldnames() -> tuple[str, ...]:
        return "id", "name", "description", "created", "modified"


@dataclass
class GenreSQLite(BaseSQLiteSchema, Genre):
    id: str
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None

    def to_pg(self) -> GenrePg:
        return GenrePg(
            id=self.id, name=self.name, description=self.description, created=self.created_at, modified=self.updated_at)


@dataclass
class Person:
    full_name: str


@dataclass
class PersonPg(BasePgSchema, Person):
    id: uuid.uuid4
    created: datetime.datetime | None
    modified: datetime.datetime | None

    def to_tuple(self) -> tuple:
        return self.id, self.full_name, self.created, self.modified

    @staticmethod
    def db_tablename() -> str:
        return "content.person"

    @staticmethod
    def db_fieldnames() -> tuple[str, ...]:
        return "id", "full_name", "created", "modified"


@dataclass
class PersonSQLite(BaseSQLiteSchema, Person):
    id: str
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None

    def to_pg(self) -> PersonPg:
        return PersonPg(
            id=self.id, full_name=self.full_name, created=self.created_at, modified=self.updated_at)


@dataclass
class GenreFilmworkPg(BasePgSchema):
    id: uuid.uuid4
    genre_id: uuid.uuid4
    film_work_id: uuid.uuid4
    created: datetime.datetime | None

    def to_tuple(self) -> tuple:
        return self.id, self.genre_id, self.film_work_id, self.created

    @staticmethod
    def db_tablename() -> str:
        return "content.genre_film_work"

    @staticmethod
    def db_fieldnames() -> tuple[str, ...]:
        return "id", "genre_id", "film_work_id", "created"


@dataclass
class GenreFilmworkSQLite(BaseSQLiteSchema):
    id: str
    genre_id: str
    film_work_id: str
    created_at: datetime.datetime | None

    def to_pg(self) -> GenreFilmworkPg:
        return GenreFilmworkPg(
            id=self.id, genre_id=self.genre_id, film_work_id=self.film_work_id, created=self.created_at)


@dataclass
class PersonFilmwork:
    role: str


@dataclass
class PersonFilmworkPg(BasePgSchema, PersonFilmwork):
    id: uuid.uuid4
    film_work_id: uuid.uuid4
    person_id: uuid.uuid4
    created: datetime.datetime | None

    def to_tuple(self) -> tuple:
        return self.id, self.film_work_id, self.person_id, self.role, self.created

    @staticmethod
    def db_tablename() -> str:
        return "content.person_film_work"

    @staticmethod
    def db_fieldnames() -> tuple[str, ...]:
        return "id", "film_work_id", "person_id", "role", "created"


@dataclass
class PersonFilmworkSQLite(BaseSQLiteSchema, PersonFilmwork):
    id: str
    film_work_id: str
    person_id: str
    created_at: datetime.datetime | None

    def to_pg(self) -> PersonFilmworkPg:
        return PersonFilmworkPg(
            id=self.id,
            film_work_id=self.film_work_id, person_id=self.person_id,
            role=self.role,
            created=self.created_at,
        )


@dataclass
class TableBatchDump:
    schema_class: SQLiteSchemaClass
    data: list[PgSchema]
