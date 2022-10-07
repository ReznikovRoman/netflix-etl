from __future__ import annotations

from typing import Iterator

import redis


def init_redis(host: str, port: int, decode_responses: bool = True) -> Iterator[redis.Redis]:
    """Setup Redis client."""
    redis_dsl = {
        "host": host,
        "port": port,
        "decode_responses": decode_responses,
    }
    return redis.Redis(**redis_dsl)
