import datetime
import logging
from typing import ClassVar, Iterator

from netflix_etl.db import get_elastic_connection, get_postgres_connection, get_redis_connection
from netflix_etl.extractors import FilmworkExtractor, GenreExtractor, PersonExtractor, PgExtractor
from netflix_etl.loaders import ElasticLoader, FilmworkLoader, GenreLoader, PersonLoader
from netflix_etl.movies_types import PgSchema
from netflix_etl.state import RedisStorage, State
from netflix_etl.transformers import ElasticTransformer, FilmworkTransformer, GenreTransformer, PersonTransformer
from netflix_etl.utils import RequiredAttributes


logger = logging.getLogger(__name__)


class ETLPipeline(metaclass=RequiredAttributes("loader", "transformer", "extractor", "state")):
    """Базовый класс для всех ETL пайплайнов."""

    loader: ClassVar[ElasticLoader]
    transformer: ClassVar[ElasticTransformer]
    extractor: ClassVar[PgExtractor]
    state: ClassVar[State]

    def extract(self) -> Iterator[list[PgSchema]]:
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
        self.state.set_state(self.extractor.etl_timestamp_key, timestamp)

    def remove_ids_from_state(self):
        self.state.set_state(self.extractor.etl_loaded_entities_ids_key, "")


class FilmworkPipeline(ETLPipeline):
    """Пайплайн для синхронизации Фильмов с Elasticsearch."""

    state = State
    loader = FilmworkLoader
    transformer = FilmworkTransformer
    extractor = FilmworkExtractor

    def __init__(self):
        self.state = State(storage=RedisStorage(redis_adapter=get_redis_connection()))
        self.loader = FilmworkLoader(es=get_elastic_connection(), state=self.state, logger=logger.debug)
        self.transformer = FilmworkTransformer(logger=logger.debug)
        self.extractor = FilmworkExtractor(pg_conn=get_postgres_connection(), state=self.state, logger=logger.debug)


class GenrePipeline(ETLPipeline):
    """Пайплайн для синхронизации Жанров с Elasticsearch."""

    state = State
    loader = GenreLoader
    transformer = GenreTransformer
    extractor = GenreExtractor

    def __init__(self):
        self.state = State(storage=RedisStorage(redis_adapter=get_redis_connection()))
        self.loader = GenreLoader(es=get_elastic_connection(), state=self.state, logger=logger.debug)
        self.transformer = GenreTransformer(logger=logger.debug)
        self.extractor = GenreExtractor(pg_conn=get_postgres_connection(), state=self.state, logger=logger.debug)


class PersonPipeline(ETLPipeline):
    """Пайплайн для синхронизации Участников с Elasticsearch."""

    state = State
    loader = PersonLoader
    transformer = PersonTransformer
    extractor = PersonExtractor

    def __init__(self):
        self.state = State(storage=RedisStorage(redis_adapter=get_redis_connection()))
        self.loader = PersonLoader(es=get_elastic_connection(), state=self.state, logger=logger.debug)
        self.transformer = PersonTransformer(logger=logger.debug)
        self.extractor = PersonExtractor(pg_conn=get_postgres_connection(), state=self.state, logger=logger.debug)
