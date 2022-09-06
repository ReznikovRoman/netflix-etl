import dataclasses
import datetime
from typing import Iterator

from etl.infrastructure.db.state import State

from .extractors import PgExtractor
from .loaders import ElasticLoader
from .movies_types import PgSchema
from .transformers import ElasticTransformer


@dataclasses.dataclass
class ETLPipeline:
    """Базовый класс для всех ETL пайплайнов."""

    loader: ElasticLoader
    transformer: ElasticTransformer
    extractor: PgExtractor
    state: State

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
