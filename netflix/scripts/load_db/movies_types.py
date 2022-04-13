from typing import Type, Union

from schemas import (
    FilmworkPg, FilmworkSQLite, GenreFilmworkPg, GenreFilmworkSQLite, GenrePg, GenreSQLite, PersonFilmworkPg,
    PersonFilmworkSQLite, PersonPg, PersonSQLite,
)


PgSchema = Union[FilmworkPg, GenreFilmworkPg, GenrePg, PersonFilmworkPg, PersonPg]
PgSchemaClass = Union[
    Type[FilmworkPg],
    Type[GenreFilmworkPg],
    Type[GenrePg],
    Type[PersonFilmworkPg],
    Type[PersonPg],
]
SQLiteSchemaClass = Union[
    Type[FilmworkSQLite],
    Type[GenreFilmworkSQLite],
    Type[GenreSQLite],
    Type[PersonFilmworkSQLite],
    Type[PersonSQLite],
]
