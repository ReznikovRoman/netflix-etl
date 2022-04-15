from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any, ClassVar, Iterator, Sequence

import psycopg2
from psycopg2.extras import RealDictCursor

from netflix_etl.constants import ETL_FILMWORK_LOADED_IDS_KEY, ETL_GENRE_LOADED_IDS_KEY
from netflix_etl.movies_types import PgSchema, PgSchemaClass
from netflix_etl.schemas import GenreDetail, MovieDetail
from netflix_etl.state import State
from netflix_etl.utils import RequiredAttributes


if TYPE_CHECKING:
    from psycopg2._psycopg import connection

    SQL = str


class PgExtractor(
    metaclass=RequiredAttributes(
        "etl_schema_class",
        "etl_timestamp_key", "etl_loaded_entities_ids_key",
        "sql_all_entities", "sql_entities_to_sync",
    ),
):
    """Базовый класс для всех `экстракторов` данных из Postgres."""

    BATCH_SIZE: ClassVar[int] = 100

    etl_schema_class: ClassVar[PgSchemaClass]

    # Ключи в сервисе состояния
    etl_timestamp_key: ClassVar[str]
    etl_loaded_entities_ids_key: ClassVar[str]

    # SQL запросы
    sql_all_entities: ClassVar[SQL]
    sql_entities_to_sync: ClassVar[SQL]

    # настройка запросов
    entities_to_select_params: ClassVar[list] = None
    entity_exclude_time_stamp_param: ClassVar[str] = "time_stamp"
    entity_exclude_field: ClassVar[str] = "id"
    entity_id_field: ClassVar[str] = "id"

    def __init__(self, pg_conn: connection, state: State, logger: logging):
        self._pg_conn = pg_conn
        self._state = state
        self._logger = logger

    def _get_paginated_results(self, cursor: RealDictCursor, schema_class: PgSchemaClass) -> Iterator[list[PgSchema]]:
        """Получение данных из Postgres пачками по `BATCH_SIZE`."""
        data: list[PgSchema] = []
        while True:
            results = cursor.fetchmany(self.BATCH_SIZE)
            if not results:
                break
            for row in results:
                data.append(schema_class.from_dict(row))
            yield data
            data = []

    def _load_data(
        self,
        sql: SQL,
        schema_class: PgSchemaClass,
        params: Sequence[Any] | None = None,
    ) -> Iterator[list[PgSchema]]:
        if params is None:
            params = []

        cursor: RealDictCursor = self._pg_conn.cursor()
        try:
            cursor.execute(sql, vars=params)
        except psycopg2.OperationalError as e:
            self._logger(f"Postgres operational error: `{e}`")
            raise
        else:
            yield from self._get_paginated_results(cursor, schema_class)
        finally:
            cursor.close()

    def load_data(
        self,
        sql: SQL,
        schema_class: PgSchemaClass,
        params: Sequence[Any] | None = None,
    ) -> Iterator[list[PgSchema]]:
        """Получение данных с переданными параметрами `params` и SQL `sql`."""
        yield from self._load_data(sql, schema_class, params)

    def get_etl_timestamp(self) -> datetime.datetime:
        """Получение времени последней синхронизации сущности."""
        timestamp: str | None = self._state.get_state(self.etl_timestamp_key)
        if timestamp is None:
            return datetime.datetime.min
        return datetime.datetime.fromtimestamp(int(timestamp))

    def get_loaded_entities_ids(self) -> tuple[str, ...] | None:
        """Получение id объектов, которые уже были синхронизированы и не будут использоваться в ETL процессе."""
        # TODO: использовать Redis Set для хранения ID объектов, а не обычную Строку
        loaded_entities_ids: str | None = self._state.get_state(self.etl_loaded_entities_ids_key)
        if loaded_entities_ids:
            return tuple(loaded_entities_ids.split(","))
        return loaded_entities_ids

    def get_sql_with_excluded_entities(self, initial_sql: SQL) -> tuple[SQL, dict]:
        """Получение данных для запроса с исключенными объектами."""
        loaded_entities_ids = self.get_loaded_entities_ids()
        if loaded_entities_ids:
            initial_sql += f"""
            AND {self.entity_exclude_field} NOT IN %(loaded_entities)s
            """
        params = {
            "loaded_entities": loaded_entities_ids,
            self.entity_exclude_time_stamp_param: self.get_etl_timestamp(),
        }
        return initial_sql, params

    def get_entities_ids_to_update(self) -> Sequence[str] | tuple[None]:
        """Получение списка id объектов, которые будут использоваться в ETL процессе."""
        sql, params = self.get_sql_with_excluded_entities(initial_sql=self.sql_entities_to_sync)
        with self._pg_conn.cursor() as cursor:
            cursor: RealDictCursor
            cursor.execute(query=sql, vars=params)
            entities_ids = tuple([row[self.entity_id_field] for row in cursor.fetchall()])
            if not len(entities_ids):
                return (None,)
            return entities_ids

    def load_batches(self) -> Iterator[PgSchema]:
        """Получение пачек данных из Postgres."""
        entities_ids = self.get_entities_ids_to_update()

        params = [entities_ids]
        if self.entities_to_select_params is not None:
            params.extend(self.entities_to_select_params)

        batches = self.load_data(self.sql_all_entities, self.etl_schema_class, params=params)
        for batch in batches:
            yield batch

    def extract(self) -> Iterator[PgSchema]:
        """Основной метод выгрузки данных из Postgres."""
        yield from self.load_batches()


class FilmworkExtractor(PgExtractor):
    """`Экстрактор` Фильмов из Postgres."""

    etl_schema_class = MovieDetail

    etl_timestamp_key = "filmwork:last_run_at"
    etl_loaded_entities_ids_key = ETL_FILMWORK_LOADED_IDS_KEY

    sql_all_entities = """
        SELECT
            fw.id, fw.title, fw.rating AS imdb_rating, fw.description,
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
            fw.id
        FROM content.film_work as fw
        LEFT OUTER JOIN content.genre_film_work gfw on fw.id = gfw.film_work_id
        LEFT OUTER JOIN content.genre g on g.id = gfw.genre_id
        LEFT OUTER JOIN content.person_film_work pfw on fw.id = pfw.film_work_id
        LEFT OUTER JOIN content.person p on p.id = pfw.person_id
        WHERE
            (fw.modified > %(time_stamp)s OR g.modified > %(time_stamp)s OR p.modified > %(time_stamp)s)
    """

    entity_exclude_field = "fw.id"


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
