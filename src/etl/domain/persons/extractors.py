from etl.domain.extractors import PgExtractor

from .constants import ETL_PERSON_LOADED_IDS_KEY
from .schemas import PersonFullDetail


class PersonExtractor(PgExtractor):
    """Persons `Extractor`."""

    etl_schema_class = PersonFullDetail

    etl_timestamp_key = "person:last_run_at"
    etl_loaded_entities_ids_key = ETL_PERSON_LOADED_IDS_KEY

    sql_all_entities = """
        SELECT
            p.id, p.full_name,
            array_agg(DISTINCT fw.id) AS films_ids,
            json_agg(
                DISTINCT jsonb_build_object(
                'id', fw.id, 'title', fw.title, 'imdb_rating', fw.rating,
                'age_rating', fw.age_rating, 'release_date', fw.release_date, 'access_type', fw.access_type
                ))
                FILTER (WHERE pfw.role = 'actor'
            ) AS actor,
            json_agg(
                DISTINCT jsonb_build_object(
                'id', fw.id, 'title', fw.title, 'imdb_rating', fw.rating,
                'age_rating', fw.age_rating, 'release_date', fw.release_date, 'access_type', fw.access_type
                ))
                FILTER (WHERE pfw.role = 'writer'
            ) AS writer,
            json_agg(
                DISTINCT jsonb_build_object(
                'id', fw.id, 'title', fw.title, 'imdb_rating', fw.rating,
                'age_rating', fw.age_rating, 'release_date', fw.release_date, 'access_type', fw.access_type
                ))
                FILTER (WHERE pfw.role = 'director'
            ) AS director
        FROM content.person AS p
        LEFT JOIN content.person_film_work pfw on p.id = pfw.person_id
        LEFT OUTER JOIN content.film_work fw on fw.id = pfw.film_work_id
        WHERE p.id IN %s
        GROUP BY p.id
    """
    sql_entities_to_sync = """
        SELECT
            DISTINCT p.id
        FROM content.person as p
        LEFT JOIN content.person_film_work pfw on pfw.person_id = p.id
        LEFT JOIN content.film_work fw on pfw.film_work_id = fw.id
        WHERE
            (p.modified > %(time_stamp)s or fw.modified > %(time_stamp)s)
    """

    entity_exclude_field = "p.id"
