from etl.domain.extractors import PgExtractor

from .constants import ETL_GENRE_LOADED_IDS_KEY
from .schemas import GenreDetail


class GenreExtractor(PgExtractor):
    """`Экстрактор` Жанров из Postgres."""

    etl_schema_class = GenreDetail

    etl_timestamp_key = "genre:last_run_at"
    etl_loaded_entities_ids_key = ETL_GENRE_LOADED_IDS_KEY

    sql_all_entities = """
        SELECT
            g.id, g.name
        FROM content.genre AS g
        WHERE g.id IN %s
    """
    sql_entities_to_sync = """
        SELECT
            g.id
        FROM content.genre as g
        WHERE
            g.modified > %(time_stamp)s
    """

    entity_exclude_field = "g.id"
