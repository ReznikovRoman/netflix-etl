from typing import Type, Union

from schemas import GenreDetail, GenreList, MovieDetail, PersonList


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
