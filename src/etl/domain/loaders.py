from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from elasticsearch import Elasticsearch, helpers

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from etl.infrastructure.db.state import State


class ElasticLoader:
    """Data `loader` to Elasticsearch."""

    etl_loaded_entities_ids_key: ClassVar[str]

    es_index: ClassVar[dict]
    es_index_name: ClassVar[str]
    es_timeout: ClassVar[str] = "3s"

    entity_id_field: ClassVar[str] = "uuid"

    def __init__(self, elastic_client: Elasticsearch, state: State):
        self._elastic_client = elastic_client
        self._state = state

    def load(self, data: Iterator[dict[str, Any]]) -> None:
        """Load data to Elasticsearch."""
        _data = list(data)

        self.create_index()
        self.update_index(_data)

        self.post_load(data=_data)

    def create_index(self) -> None:
        """Create index in Elasticsearch.

        If index has been already created, errors will be ignored.
        """
        self._elastic_client.indices.create(
            index=self.es_index_name,
            body=self.es_index,
            ignore=[400],
            timeout=self.es_timeout,
        )

    def update_index(self, data: list[dict[str, Any]]) -> tuple[int, int | list]:
        """Update documents in the index."""
        return helpers.bulk(self._elastic_client, data)

    def post_load(self, *args: Any, **kwargs: Any) -> None:
        """`Post-load` signal.

        Method is called after data upload.
        """
        self.update_ids_in_state(kwargs["data"])

    def update_ids_in_state(self, data: Iterable[dict[str, Any]]) -> None:
        """Update current state with IDs of uploaded documents."""
        ids = ",".join([str(entity_data["_source"][self.entity_id_field]) for entity_data in data])
        self._state.set_state(self.etl_loaded_entities_ids_key, ids)
