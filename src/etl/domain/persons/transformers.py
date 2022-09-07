from etl.domain.transformers import ElasticTransformer

from .constants import ETL_PERSON_INDEX_NAME
from .schemas import PersonFullDetail


class PersonTransformer(ElasticTransformer):
    """`Преобразователь` данных Персон."""

    etl_schema_class = PersonFullDetail

    es_index_name = ETL_PERSON_INDEX_NAME
    es_type = "_doc"
