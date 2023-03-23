import dataclasses
import datetime
from collections.abc import Iterator
from typing import Any

from etl.infrastructure.db.storage import BaseStorage

from .extractors import PgExtractor
from .loaders import ElasticLoader
from .schemas import PgSchema
from .transformers import ElasticTransformer


@dataclasses.dataclass
class ETLPipeline:
    """Base class for all ETL pipelines."""

    loader: ElasticLoader
    transformer: ElasticTransformer
    extractor: PgExtractor
    storage: BaseStorage

    def extract(self) -> Iterator[list[PgSchema]]:
        yield from self.extractor.extract()

    def transform(self, data: list[PgSchema]) -> Iterator[dict[str, Any]]:
        return self.transformer.transform(data)

    def load(self, data: Iterator[dict[str, Any]]) -> None:
        self.loader.load(data)

    def execute(self) -> None:
        for batch in self.extract():
            self.load(self.transform(batch))
        self.post_execute()

    def post_execute(self, *args: Any, **kwargs: Any) -> None:
        self.update_timestamp_state()
        self.remove_ids_from_state()

    def update_timestamp_state(self) -> None:
        timestamp = str(datetime.datetime.now(tz=datetime.UTC).timestamp()).rsplit(".", 1)[0]
        self.storage.save(self.extractor.etl_timestamp_key, timestamp)

    def remove_ids_from_state(self) -> None:
        self.storage.remove(self.extractor.etl_loaded_entities_ids_key)
