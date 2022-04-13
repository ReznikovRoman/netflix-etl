from __future__ import annotations

import logging
import os
import sqlite3
from typing import TYPE_CHECKING, Final, Iterator

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_values
from schemas import (
    FilmworkPg, FilmworkSQLite, GenreFilmworkPg, GenreFilmworkSQLite, GenrePg, GenreSQLite, PersonFilmworkPg,
    PersonFilmworkSQLite, PersonPg, PersonSQLite, TableBatchDump,
)


if TYPE_CHECKING:
    from movies_types import PgSchema, PgSchemaClass, SQLiteSchemaClass
    SQL = str


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)


class SQLiteLoader:
    """Загрузчик данных из `sqlite`."""

    BATCH_SIZE: Final[int] = int(os.environ.get("DB_SQLITE_BATCH_SIZE", 500))

    def __init__(self, sqlite_conn: sqlite3.Connection) -> None:
        self._sqlite_conn = sqlite_conn
        self._sqlite_conn.row_factory = sqlite3.Row

    @staticmethod
    def _get_paginated_results(cursor: sqlite3.Cursor, schema_class: SQLiteSchemaClass) -> Iterator[list[PgSchema]]:
        data = []
        while True:
            results = cursor.fetchmany(SQLiteLoader.BATCH_SIZE)
            if not results:
                break
            for row in results:
                data.append(schema_class(**row).to_pg())
            yield data
            data = []

    def _load_table(self, sql: SQL, schema_class: SQLiteSchemaClass) -> Iterator[list[PgSchema]]:
        cursor = self._sqlite_conn.cursor()
        try:
            cursor.execute(sql)
        except sqlite3.OperationalError as e:
            logging.error(f'SQLite operational error: `{e}`')
            raise
        else:
            yield from self._get_paginated_results(cursor, schema_class)
        finally:
            cursor.close()

    def load_table(self, sql: SQL, schema_class: SQLiteSchemaClass) -> Iterator[list[PgSchema]]:
        yield from self._load_table(sql, schema_class)

    def load_batches(self) -> Iterator[TableBatchDump]:
        """Выгружает данные из sqlite пачками по `SQLiteLoader.BATCH_SIZE`."""
        schema_sql_map: dict[SQLiteSchemaClass, SQL] = {
            FilmworkSQLite: """SELECT * FROM film_work""",
            PersonSQLite: """SELECT * FROM person""",
            GenreSQLite: """SELECT * FROM genre""",
            GenreFilmworkSQLite: """SELECT * FROM genre_film_work""",
            PersonFilmworkSQLite: """SELECT * FROM person_film_work""",
        }
        for schema, sql in schema_sql_map.items():
            for batch in self.load_table(sql, schema):
                yield TableBatchDump(schema_class=schema, data=batch)


class PostgresSaver:
    """Загрузчик данных в `postgres`."""

    BATCH_SIZE: Final[int] = int(os.environ.get("DB_POSTGRES_BATCH_SIZE", 50))

    def __init__(self, pg_conn: _connection) -> None:
        self._pg_conn = pg_conn

    @staticmethod
    def _get_column_names(columns: tuple[str, ...]) -> str:
        column_names = ", ".join(columns)
        return column_names.rstrip()

    def _save_table(self, table_data: list[PgSchema], schema_class: PgSchemaClass) -> None:
        with self._pg_conn.cursor() as cursor:
            data = [row.to_tuple() for row in table_data]
            sql = f"""
            INSERT INTO {schema_class.db_tablename()}
            ({self._get_column_names(schema_class.db_fieldnames())})
            VALUES %s
            ON CONFLICT (id) DO NOTHING
            """
            try:
                execute_values(cursor, sql, data, page_size=PostgresSaver.BATCH_SIZE)
            except psycopg2.OperationalError as e:
                logging.error(f'psycopg2 operational error: `{e}`')
                cursor.close()
                raise

    def save_table(self, table_data: list[PgSchema], schema_class: PgSchemaClass) -> None:
        self._save_table(table_data, schema_class)

    def save_batch(self, batch: TableBatchDump) -> None:
        sqlite_to_pg_schema_map: dict[SQLiteSchemaClass, PgSchemaClass] = {
            FilmworkSQLite: FilmworkPg,
            GenreFilmworkSQLite: GenreFilmworkPg,
            GenreSQLite: GenrePg,
            PersonFilmworkSQLite: PersonFilmworkPg,
            PersonSQLite: PersonPg,
        }
        pg_schema_class = sqlite_to_pg_schema_map[batch.schema_class]
        logging.debug(f'Save data to postgres, table: {pg_schema_class.db_tablename()}')
        self.save_table(table_data=batch.data, schema_class=pg_schema_class)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection) -> None:
    """Основной метод загрузки данных из SQLite в Postgres."""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    logging.debug('Load data from sqlite')
    for batch in sqlite_loader.load_batches():
        postgres_saver.save_batch(batch)


if __name__ == '__main__':
    dsl = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'port': int(os.environ.get('DB_PORT', 5432)),
    }
    with sqlite3.connect('db.sqlite') as sqlite_conn_, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn_:
        load_from_sqlite(sqlite_conn_, pg_conn_)
