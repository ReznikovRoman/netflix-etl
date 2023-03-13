from __future__ import annotations

from typing import TYPE_CHECKING

import psycopg2
from psycopg2.extras import RealDictCursor

if TYPE_CHECKING:
    from collections.abc import Iterator

    from psycopg2._psycopg import connection


def init_postgres(db_name: str, db_user: str, db_password: str, host: str, port: int) -> Iterator[connection]:
    """Setup PostgreSQL client."""
    postgres_dsl = {
        "dbname": db_name,
        "user": db_user,
        "password": db_password,
        "host": host,
        "port": port,
    }
    postgres_connection: connection = psycopg2.connect(**postgres_dsl, cursor_factory=RealDictCursor)
    register_postgres_extensions()
    yield postgres_connection
    postgres_connection.close()


def register_postgres_extensions() -> None:
    """Register Postgres extensions."""
    psycopg2.extras.register_uuid()
