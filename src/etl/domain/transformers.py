from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from etl.utils import RequiredAttributes

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .types import PgSchema


class ElasticTransformer(metaclass=RequiredAttributes("etl_schema_class", "es_index_name", "es_type")):
    """Base class for all `data transformers` to the required format for Elasticsearch."""

    etl_schema_class: ClassVar[PgSchema]

    # Elasticsearch document config
    es_index_name: ClassVar[str]
    es_type: ClassVar[str]

    def transform(self, data: Iterator[PgSchema]) -> Iterator[dict]:
        """Transform data to the required format for Elasticsearch."""
        actions = (
            {"_index": self.es_index_name, "_type": self.es_type, "_id": es_id, "_source": es_source}
            for es_id, es_source in self._prepare_values(data)
        )
        yield from actions

    def _prepare_values(self, data: Iterator[PgSchema]) -> Iterator[tuple[str, dict]]:
        for entity in data:
            yield self._prepare_es_id(entity), self._prepare_entity(entity)

    @staticmethod
    def _prepare_entity(entity: PgSchema) -> dict:
        return entity.to_dict()

    @staticmethod
    def _prepare_es_id(entity: PgSchema) -> str:
        return entity.id
