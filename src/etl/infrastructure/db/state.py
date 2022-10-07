import abc
import json
from typing import Any

from redis import Redis


class BaseStorage:
    """Base state storage."""

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Save state in storage."""

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Retrieve state from storage."""


class RedisStorage(BaseStorage):
    """Storage with Redis backend."""

    REDIS_DATA_KEY: str = "data"

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def save_state(self, state: dict) -> None:
        self.redis_client.hmset(self.REDIS_DATA_KEY, json.loads(json.dumps(state)))

    def retrieve_state(self) -> dict:
        return self.redis_client.hgetall(RedisStorage.REDIS_DATA_KEY)


class State:
    """State of ETL pipeline."""

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Set state for a specific key."""
        state = self.storage.retrieve_state()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        """Retrieve state by a key."""
        return self.storage.retrieve_state().get(key)
