import abc
import json
from typing import Any

from redis import Redis


class BaseStorage:
    """Базовое хранилище состояний."""

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранение состояния в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Получение состояния из хранилища."""


class RedisStorage(BaseStorage):
    """Хранилище с использованием Redis."""

    REDIS_DATA_KEY: str = "data"

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def save_state(self, state: dict) -> None:
        self.redis_client.hmset(self.REDIS_DATA_KEY, json.loads(json.dumps(state)))

    def retrieve_state(self) -> dict:
        return self.redis_client.hgetall(RedisStorage.REDIS_DATA_KEY)


class State:
    """Состояние ETL пайплайна."""

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установка состояния для определённого ключа."""
        state = self.storage.retrieve_state()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        """Получение состояния по определённому ключу."""
        return self.storage.retrieve_state().get(key)
