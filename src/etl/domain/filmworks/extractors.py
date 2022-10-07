from etl.domain.extractors import PgExtractor

from .constants import ETL_FILMWORK_LOADED_IDS_KEY
from .schemas import MovieDetail


class FilmworkExtractor(PgExtractor):
    """Movies `Extractor`."""

    etl_schema_class = MovieDetail

    etl_timestamp_key = "filmwork:last_run_at"
    etl_loaded_entities_ids_key = ETL_FILMWORK_LOADED_IDS_KEY

    sql_all_entities = """
        SELECT
            fw.id, fw.title, fw.rating AS imdb_rating, fw.description, fw.age_rating, fw.release_date, fw.access_type,
            array_agg(DISTINCT g.name) AS genres_names,
            array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director') AS directors_names,
            array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor') AS actors_names,
            array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer') AS writers_names,
            json_agg(DISTINCT jsonb_build_object('id', g.id, 'name', g.name)) AS genre,
            json_agg(
                DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
                FILTER (WHERE pfw.role = 'actor'
            ) AS actors,
            json_agg(
                DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
                FILTER (WHERE pfw.role = 'writer'
            ) AS writers,
            json_agg(
                DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
                FILTER (WHERE pfw.role = 'director'
            ) AS directors
        FROM content.film_work as fw
        LEFT OUTER JOIN content.genre_film_work gfw on fw.id = gfw.film_work_id
        LEFT OUTER JOIN content.genre g on g.id = gfw.genre_id
        LEFT OUTER JOIN content.person_film_work pfw on fw.id = pfw.film_work_id
        LEFT OUTER JOIN content.person p on p.id = pfw.person_id
        WHERE fw.id IN %s
        GROUP BY fw.id
    """
    sql_entities_to_sync = """
        SELECT
            DISTINCT fw.id
        FROM content.film_work as fw
        LEFT OUTER JOIN content.genre_film_work gfw on fw.id = gfw.film_work_id
        LEFT OUTER JOIN content.genre g on g.id = gfw.genre_id
        LEFT OUTER JOIN content.person_film_work pfw on fw.id = pfw.film_work_id
        LEFT OUTER JOIN content.person p on p.id = pfw.person_id
        WHERE
            (fw.modified > %(time_stamp)s OR g.modified > %(time_stamp)s OR p.modified > %(time_stamp)s)
    """

    entity_exclude_field = "fw.id"
