from typing import Type, Union

from netflix_etl.schemas import GenreDetail, GenreList, MovieDetail, PersonFullDetail, PersonList


PgSchema = Union[
    GenreDetail,
    MovieDetail,
    PersonList,
    GenreList,
    PersonFullDetail,
]
PgSchemaClass = Union[
    Type[GenreDetail],
    Type[MovieDetail],
    Type[PersonList],
    Type[GenreList],
    Type[PersonFullDetail],
]
