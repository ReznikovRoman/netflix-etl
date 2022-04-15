from typing import Type, Union

from netflix_etl.schemas import GenreDetail, GenreList, MovieDetail, PersonList


PgSchema = Union[
    GenreDetail,
    MovieDetail,
    PersonList,
    GenreList,
]
PgSchemaClass = Union[
    Type[GenreDetail],
    Type[MovieDetail],
    Type[PersonList],
    Type[GenreList],
]
