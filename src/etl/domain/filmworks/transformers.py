from etl.domain.transformers import ElasticTransformer

from .constants import ETL_FILMWORK_INDEX_NAME
from .schemas import MovieDetail


class FilmworkTransformer(ElasticTransformer):
    """`Преобразователь` данных Фильмов."""

    etl_schema_class = MovieDetail

    es_index_name = ETL_FILMWORK_INDEX_NAME
    es_type = "_doc"
