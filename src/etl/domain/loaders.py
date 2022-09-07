from __future__ import annotations

from typing import ClassVar, Iterator

from elasticsearch import Elasticsearch, helpers

from etl.infrastructure.db.state import State
from etl.utils import RequiredAttributes


class ElasticLoader(metaclass=RequiredAttributes("etl_loaded_entities_ids_key", "es_index", "es_index_name")):
    """`Загрузчик` данных в Elasticsearch."""

    etl_loaded_entities_ids_key: ClassVar[str]

    es_index: ClassVar[dict]
    es_index_name: ClassVar[str]
    es_timeout: ClassVar[str] = "3s"

    entity_id_field: ClassVar[str] = "uuid"

    def __init__(self, elastic_client: Elasticsearch, state: State):
        self._elastic_client = elastic_client
        self._state = state

    def load(self, data: Iterator[dict]) -> None:
        """Загрузка данных в Elasticsearch."""
        data = list(data)

        self.create_index()
        self.update_index(data)

        self.post_load(data=data)

    def create_index(self):
        """Создание индекса в Elasticsearch.

        Если индекс уже создан, то ошибки будут проигнорированы.
        """
        self._elastic_client.indices.create(
            index=self.es_index_name,
            body=self.es_index,
            ignore=[400],
            timeout=self.es_timeout,
        )

    def update_index(self, data: Iterator[dict]) -> tuple[int, int | list]:
        """Обновление документов в индексе."""
        return helpers.bulk(self._elastic_client, data)

    def post_load(self, *args, **kwargs) -> None:
        """Сигнал, вызываемый после загрузки данных."""
        self.update_ids_in_state(kwargs["data"])

    def update_ids_in_state(self, data) -> None:
        """Обновление текущего состояния с помощью ID загруженных документов."""
        ids = ",".join([str(entity_data["_source"][self.entity_id_field]) for entity_data in data])
        self._state.set_state(self.etl_loaded_entities_ids_key, ids)
