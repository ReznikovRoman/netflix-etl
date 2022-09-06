from typing import Iterator

import elasticsearch
from elasticsearch.connection.http_requests import RequestsHttpConnection


def init_elastic(host: str, port: int, retry_on_timeout: bool = True) -> Iterator[elasticsearch.Elasticsearch]:
    """Инициализация клиента Elasticsearch."""
    elastic_client = elasticsearch.Elasticsearch(
        hosts=[
            {"host": host, "port": port},
        ],
        connection_class=RequestsHttpConnection,
        max_retries=30,
        retry_on_timeout=retry_on_timeout,
        request_timeout=30,
    )
    yield elastic_client
    elastic_client.close()
