from __future__ import annotations

import os
from typing import TYPE_CHECKING

import elasticsearch.exceptions
import psycopg2
import redis
from elasticsearch import Elasticsearch, RequestsHttpConnection
from psycopg2.extras import RealDictCursor

from netflix_etl.utils import retry


if TYPE_CHECKING:
    from psycopg2._psycopg import connection


@retry(
    times=5,
    exceptions=[redis.exceptions.ConnectionError],
)
def get_redis_connection() -> redis.Redis:
    redis_dsl = {
        "host": os.environ.get("NE_REDIS_HOST"),
        "port": os.environ.get("NE_REDIS_PORT"),
        "decode_responses": bool(int(os.environ.get("NE_REDIS_DECODE_RESPONSES", 0))),
    }
    return redis.Redis(**redis_dsl)


@retry(
    times=5,
    exceptions=[psycopg2.OperationalError],
)
def get_postgres_connection() -> connection:
    postgres_dsl = {
        "dbname": os.environ.get("NA_DB_NAME"),
        "user": os.environ.get("NA_DB_USER"),
        "password": os.environ.get("NA_DB_PASSWORD"),
        "host": os.environ.get("NA_DB_HOST", "127.0.0.1"),
        "port": int(os.environ.get("NA_DB_PORT", 5432)),
    }
    return psycopg2.connect(**postgres_dsl, cursor_factory=RealDictCursor)


@retry(
    times=5,
    exceptions=[elasticsearch.exceptions.ConnectionError],
)
def get_elastic_connection() -> Elasticsearch:
    es = Elasticsearch(
        hosts=[
            {"host": os.environ.get("NE_ES_HOST", "localhost"), "port": os.environ.get("NE_ES_PORT", 9200)},
        ],
        connection_class=RequestsHttpConnection,
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    return es
