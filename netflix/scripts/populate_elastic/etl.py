from __future__ import annotations

import datetime
import logging
import os
from functools import cached_property
from time import sleep
from typing import TYPE_CHECKING, Any, Final, Iterator, Sequence

import elasticsearch.exceptions
import psycopg2
import redis
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
from psycopg2.extras import RealDictCursor

from constants import (
    ES_INDEX_NAME, ETL_LAST_INDEXES_KEY, ETL_REFRESH_TIME_SECONDS, ETL_TIMESTAMP_KEY,
)
from movies_types import PgSchema, PgSchemaClass
from schemas import MovieDetail
from state import RedisStorage, State
from utils import retry


if TYPE_CHECKING:
    from psycopg2._psycopg import connection

    SQL = str


class PostgresExtractor:
    """`Экстрактор` данных из Postgres."""

    BATCH_SIZE: Final[int] = int(os.environ.get("DB_POSTGRES_BATCH_SIZE", 500))

    def __init__(self, pg_conn: connection, state: State, logger: logging):
        self._pg_conn = pg_conn
        self._state = state
        self._logger = logger

    @staticmethod
    def _get_paginated_results(cursor: RealDictCursor, schema_class: PgSchemaClass):
        data = []
        while True:
            results = cursor.fetchmany(PostgresExtractor.BATCH_SIZE)
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
            self._logger(f'Postgres operational error: `{e}`')
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
        yield from self._load_data(sql, schema_class, params)

    def get_etl_timestamp(self) -> datetime.datetime:
        timestamp: str | None = self._state.get_state(ETL_TIMESTAMP_KEY)
        if timestamp is None:
            return datetime.datetime.min
        return datetime.datetime.fromtimestamp(int(timestamp))

    def get_loaded_films_ids(self) -> tuple[str, ...] | None:
        loaded_films_ids: str | None = self._state.get_state(ETL_LAST_INDEXES_KEY)
        if loaded_films_ids:
            return tuple(loaded_films_ids.split(","))
        return loaded_films_ids

    def get_movies_ids_to_update(self) -> Sequence[str] | tuple[None]:
        movies_to_update_sql = """
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
        loaded_films_ids = self.get_loaded_films_ids()
        if loaded_films_ids:
            movies_to_update_sql += """
            AND fw.id NOT IN %(loaded_films)s
            """
        with self._pg_conn.cursor() as cursor:
            cursor: RealDictCursor
            cursor.execute(
                query=movies_to_update_sql,
                vars={"time_stamp": self.get_etl_timestamp(), "loaded_films": loaded_films_ids},
            )
            movies_ids = tuple([row['id'] for row in cursor.fetchall()])
            if not len(movies_ids):
                return (None,)
            return movies_ids

    def load_movies_batches(self) -> Iterator[MovieDetail]:
        movies_sql = """
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
        movies_ids = self.get_movies_ids_to_update()
        batches = self.load_data(movies_sql, MovieDetail, params=[movies_ids])
        for batch in batches:
            yield batch

    def extract(self) -> Iterator[MovieDetail]:
        yield from self.load_movies_batches()


class DTOTransformer:
    """`Преобразователь` данных в DTO."""

    def __init__(self, logger: logging):
        self._logger = logger

    @staticmethod
    def _prepare_movie(movie: MovieDetail) -> dict:
        return movie.to_dict()

    @staticmethod
    def _prepare_es_id(movie: MovieDetail) -> str:
        return movie.id

    @staticmethod
    def _prepare_values(data: Iterator[MovieDetail]) -> Iterator[tuple[str, dict]]:
        for movie in data:
            yield DTOTransformer._prepare_es_id(movie), DTOTransformer._prepare_movie(movie)

    def transform(self, data: Iterator[MovieDetail]) -> Iterator[dict]:
        actions = (
            {"_index": ES_INDEX_NAME, "_type": "_doc", "_id": es_id, "_source": es_source}
            for es_id, es_source in DTOTransformer._prepare_values(data)
        )
        yield from actions


class ElasticLoader:
    """`Загрузчик` данных в Elasticsearch."""

    ES_TIMEOUT = os.environ.get("ES_TIMEOUT", '3s')

    def __init__(self, es: Elasticsearch, state: State, logger: logging):
        self._es = es
        self._state = state
        self._logger = logger

    @cached_property
    def movies_index(self) -> dict[str, Any]:
        index = {
            "settings": {
                "refresh_interval": "1s",
                "analysis": {
                    "filter": {
                        "english_stop": {
                            "type": "stop",
                            "stopwords": "_english_",
                        },
                        "english_stemmer": {
                            "type": "stemmer",
                            "language": "english",
                        },
                        "english_possessive_stemmer": {
                            "type": "stemmer",
                            "language": "possessive_english",
                        },
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_",
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian",
                        },
                    },
                    "analyzer": {
                        "ru_en": {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "english_stop",
                                "english_stemmer",
                                "english_possessive_stemmer",
                                "russian_stop",
                                "russian_stemmer",
                            ],
                        },
                    },
                },
            },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "uuid": {
                        "type": "keyword",
                    },
                    "imdb_rating": {
                        "type": "float",
                    },
                    "genre": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "uuid": {
                                "type": "keyword",
                            },
                            "name": {
                                "type": "text",
                                "analyzer": "ru_en",
                                "fields": {
                                    "raw": {
                                        "type": "keyword",
                                    },
                                },
                            },
                        },
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "ru_en",
                        "fields": {
                            "raw": {
                                "type": "keyword",
                            },
                        },
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "ru_en",
                    },
                    "genres_names": {
                        "type": "text",
                        "analyzer": "ru_en",
                    },
                    "actors_names": {
                        "type": "text",
                        "analyzer": "ru_en",
                    },
                    "writers_names": {
                        "type": "text",
                        "analyzer": "ru_en",
                    },
                    "directors_names": {
                        "type": "text",
                        "analyzer": "ru_en",
                    },
                    "actors": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "uuid": {
                                "type": "keyword",
                            },
                            "full_name": {
                                "type": "text",
                                "analyzer": "ru_en",
                            },
                        },
                    },
                    "writers": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "uuid": {
                                "type": "keyword",
                            },
                            "full_name": {
                                "type": "text",
                                "analyzer": "ru_en",
                            },
                        },
                    },
                    "directors": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "uuid": {
                                "type": "keyword",
                            },
                            "full_name": {
                                "type": "text",
                                "analyzer": "ru_en",
                            },
                        },
                    },
                },
            },
        }
        return index

    def create_index(self):
        self._es.indices.create(
            index=ES_INDEX_NAME,
            body=self.movies_index,
            ignore=[400],
            timeout=ElasticLoader.ES_TIMEOUT,
        )

    def update_index(self, data) -> tuple[int, int | list]:
        return helpers.bulk(self._es, data)

    def load(self, data: Iterator[dict]) -> None:
        data = list(data)

        self.create_index()
        self.update_index(data)

        self.post_load(data=data)

    def post_load(self, *args, **kwargs) -> None:
        self.update_ids_in_state(kwargs['data'])

    def update_ids_in_state(self, data) -> None:
        ids = ','.join([str(movie_data['_source']['uuid']) for movie_data in data])
        self._state.set_state(ETL_LAST_INDEXES_KEY, ids)


class MoviesETLPipeline:
    """Пайплайн для загрузки данных из Postgres в Elasticsearch."""

    def __init__(
        self,
        loader: ElasticLoader,
        transformer: DTOTransformer,
        extractor: PostgresExtractor,
        state: State,
    ):
        self.loader = loader
        self.transformer = transformer
        self.extractor = extractor
        self._state = state

    def extract(self) -> Iterator[list[MovieDetail]]:
        yield from self.extractor.extract()

    def transform(self, data) -> Iterator[dict]:
        return self.transformer.transform(data)

    def load(self, data) -> None:
        self.loader.load(data)

    def execute(self) -> None:
        for batch in self.extract():
            self.load(self.transform(batch))

        self.post_execute()

    def post_execute(self, *args, **kwargs) -> None:
        self.update_timestamp_state()
        self.remove_ids_from_state()

    def update_timestamp_state(self) -> None:
        timestamp = str(datetime.datetime.now().timestamp()).rsplit(".", 1)[0]
        self._state.set_state(ETL_TIMESTAMP_KEY, timestamp)

    def remove_ids_from_state(self):
        self._state.set_state(ETL_LAST_INDEXES_KEY, "")


@retry(
    times=5,
    exceptions=[psycopg2.OperationalError],
)
def get_postgres_connection() -> connection:
    postgres_dsl = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'port': int(os.environ.get('DB_PORT', 5432)),
    }
    return psycopg2.connect(**postgres_dsl, cursor_factory=RealDictCursor)


@retry(
    times=5,
    exceptions=[elasticsearch.exceptions.ConnectionError],
)
def get_elastic_connection() -> Elasticsearch:
    es = Elasticsearch(
        hosts=[
            {"host": os.environ.get("ES_HOST", "localhost"), "port": os.environ.get("ES_PORT", 9200)},
        ],
        connection_class=RequestsHttpConnection,
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    return es


def main():
    logging.debug("--- Start ETL pipeline")

    redis_dsl = {
        "host": os.environ.get("REDIS_HOST"),
        "port": os.environ.get("REDIS_PORT"),
        "decode_responses": bool(int(os.environ.get("REDIS_DECODE_RESPONSES", 0))),
    }
    redis_client = redis.Redis(**redis_dsl)

    storage = RedisStorage(redis_adapter=redis_client)
    state = State(storage)

    pg_conn = get_postgres_connection()
    extractor = PostgresExtractor(pg_conn=pg_conn, state=state, logger=logging.debug)

    transformer = DTOTransformer(logger=logging.debug)

    es = get_elastic_connection()
    loader = ElasticLoader(es=es, state=state, logger=logging.debug)

    etl = MoviesETLPipeline(loader, transformer, extractor, state=state)
    etl.execute()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

    while True:
        main()
        sleep(ETL_REFRESH_TIME_SECONDS)
