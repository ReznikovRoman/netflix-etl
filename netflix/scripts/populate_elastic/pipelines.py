import datetime
import logging
from typing import ClassVar, Iterator

from db import get_elastic_connection, get_postgres_connection, get_redis_connection
from extractors import FilmworkExtractor, PgExtractor
from loaders import ElasticLoader, FilmworkLoader
from movies_types import PgSchema
from state import RedisStorage, State
from transformers import ElasticTransformer, FilmworkTransformer
from utils import RequiredAttributes


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
    """Пайплайн для синхронизации фильмов с Elasticsearch."""

    state = State(storage=RedisStorage(redis_adapter=get_redis_connection()))
    loader = FilmworkLoader(es=get_elastic_connection(), state=state, logger=logger.debug)
    transformer = FilmworkTransformer(logger=logger.debug)
    extractor = FilmworkExtractor(pg_conn=get_postgres_connection(), state=state, logger=logger.debug)