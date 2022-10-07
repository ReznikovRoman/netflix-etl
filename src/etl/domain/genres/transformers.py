from etl.domain.transformers import ElasticTransformer

from .constants import ETL_GENRE_INDEX_NAME
from .schemas import GenreDetail


class GenreTransformer(ElasticTransformer):
    """Genres' data `Transformer`."""

    etl_schema_class = GenreDetail

    es_index_name = ETL_GENRE_INDEX_NAME
    es_type = "_doc"
