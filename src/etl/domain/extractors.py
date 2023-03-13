from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any, ClassVar

import psycopg2

from etl.utils import RequiredAttributes

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from psycopg2._psycopg import connection
    from psycopg2.extras import RealDictCursor

    from etl.infrastructure.db.state import State

    from .types import PgSchema, PgSchemaClass

if TYPE_CHECKING:
    SQL = str


class PgExtractor(
    metaclass=RequiredAttributes(
        "etl_schema_class",
        "etl_timestamp_key", "etl_loaded_entities_ids_key",
        "sql_all_entities", "sql_entities_to_sync",
    ),
):
    """Base class for all `data extractors` from Postgres."""

    BATCH_SIZE: ClassVar[int] = 100

    etl_schema_class: ClassVar[PgSchemaClass]

    # Keys in a state storage
    etl_timestamp_key: ClassVar[str]
    etl_loaded_entities_ids_key: ClassVar[str]

    # SQL queries
    sql_all_entities: ClassVar[SQL]
    sql_entities_to_sync: ClassVar[SQL]

    # queries config
    entities_to_select_params: ClassVar[list | None] = None
    entity_exclude_time_stamp_param: ClassVar[str] = "time_stamp"
    entity_exclude_field: ClassVar[str] = "id"
    entity_id_field: ClassVar[str] = "id"

    def __init__(self, pg_conn: connection, state: State):
        self._pg_conn = pg_conn
        self._state = state

    def extract(self) -> Iterator[PgSchema]:
        """Primary method of extracting data from Postgres."""
        yield from self.load_batches()

    def load_batches(self) -> Iterator[PgSchema]:
        """Load batches of data from Postgres."""
        entities_ids = self.get_entities_ids_to_update()

        params = [entities_ids]
        if self.entities_to_select_params is not None:
            params.extend(self.entities_to_select_params)

        batches = self.load_data(self.sql_all_entities, self.etl_schema_class, params=params)
        yield from batches

    def get_entities_ids_to_update(self) -> Sequence[str] | tuple[None]:
        """Get list of entities ids for ETL pipeline."""
        sql, params = self.get_sql_with_excluded_entities(initial_sql=self.sql_entities_to_sync)
        cursor: RealDictCursor
        with self._pg_conn.cursor() as cursor:
            cursor.execute(query=sql, vars=params)
            entities_ids = tuple([row[self.entity_id_field] for row in cursor.fetchall()])
            if not len(entities_ids):
                return (None,)
            return entities_ids

    def get_sql_with_excluded_entities(self, initial_sql: SQL) -> tuple[SQL, dict]:
        """Get data for configuring SQL query with excluded entities."""
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

    def get_loaded_entities_ids(self) -> tuple[str, ...] | None:
        """Get IDs of entities that have been already synced and will not be used in the ETL pipeline."""
        # TODO: use Redis Set for storing IDs instead of plain python string
        loaded_entities_ids: str | None = self._state.get_state(self.etl_loaded_entities_ids_key)
        if loaded_entities_ids:
            return tuple(loaded_entities_ids.split(","))
        return loaded_entities_ids

    def get_etl_timestamp(self) -> datetime.datetime:
        """Get timestamp of the last entity's sync."""
        timestamp: str | None = self._state.get_state(self.etl_timestamp_key)
        if timestamp is None:
            return datetime.datetime.min
        return datetime.datetime.fromtimestamp(int(timestamp), tz=datetime.timezone.utc)

    def load_data(
        self, sql: SQL, schema_class: PgSchemaClass, params: Sequence[Any] | None = None,
    ) -> Iterator[list[PgSchema]]:
        """Fetch data using given `params` and `sql`."""
        yield from self._load_data(sql, schema_class, params)

    def _get_paginated_results(self, cursor: RealDictCursor, schema_class: PgSchemaClass) -> Iterator[list[PgSchema]]:
        """Fetch data from Postgres in `BATCH_SIZE` batches."""
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
        self, sql: SQL, schema_class: PgSchemaClass, params: Sequence[Any] | None = None,
    ) -> Iterator[list[PgSchema]]:
        """Fetch paginated data from Postgres."""
        if params is None:
            params = []

        cursor: RealDictCursor = self._pg_conn.cursor()
        try:
            cursor.execute(sql, vars=params)
        except psycopg2.OperationalError:
            logging.error("Postgres operational error.")
            raise
        else:
            yield from self._get_paginated_results(cursor, schema_class)
        finally:
            cursor.close()
