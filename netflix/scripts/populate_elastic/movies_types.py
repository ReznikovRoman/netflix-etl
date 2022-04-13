from typing import Type, Union

from schemas import MovieDetail, PersonDetail


PgSchema = Union[MovieDetail, PersonDetail]
PgSchemaClass = Union[
    Type[MovieDetail],
    Type[PersonDetail],
]
