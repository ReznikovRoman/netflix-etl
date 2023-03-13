from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import redis

if TYPE_CHECKING:
    from collections.abc import Iterator


def init_redis(host: str, port: int, decode_responses: Literal[True] | Literal[False] = True) -> Iterator[redis.Redis]:
    """Setup Redis client."""
    redis_client = redis.Redis(host=host, port=port, decode_responses=decode_responses)
    yield redis_client
    redis_client.close()
