from typing import Type, Union

from scripts.populate_elastic.schemas import MovieDetail, PersonDetail


PgSchema = Union[MovieDetail, PersonDetail]
PgSchemaClass = Union[
    Type[MovieDetail],
    Type[PersonDetail],
]
