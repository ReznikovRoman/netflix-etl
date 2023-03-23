from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    from collections.abc import Iterable

    from redis import Redis

    StorageItemT: TypeAlias = str | None
    StorageItemListT: TypeAlias = Iterable[str] | None


class BaseStorage:
    """Base state storage."""

    @abc.abstractmethod
    def save(self, key: str, value: Any) -> bool | None:
        """Save item in storage."""

    @abc.abstractmethod
    def retrieve(self, key: str) -> StorageItemT:
        """Retrieve item from storage."""

    @abc.abstractmethod
    def save_list(self, key: str, *values: Any) -> int:
        """Save list of items in storage."""

    @abc.abstractmethod
    def retrieve_list(self, key: str) -> StorageItemListT:
        """Retrieve list of items from storage."""

    @abc.abstractmethod
    def remove(self, key: str) -> int:
        """Delete item from storage."""


class RedisStorage(BaseStorage):
    """Storage with Redis backend."""

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def save(self, key: str, value: Any) -> bool | None:
        return self.redis_client.set(key, value)

    def retrieve(self, key: str, /) -> StorageItemT:
        return self.redis_client.get(key)

    def save_list(self, key: str, *values: Any) -> int:
        return self.redis_client.sadd(key, *values)

    def retrieve_list(self, key: str, /) -> StorageItemListT:
        return self.redis_client.smembers(key)

    def remove(self, key: str, /) -> int:
        return self.redis_client.delete(key)
