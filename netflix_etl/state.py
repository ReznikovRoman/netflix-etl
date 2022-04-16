import abc
import json
from typing import Any

from redis import Redis


class BaseStorage:
    """Базовое хранилище состояний."""

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища."""


class RedisStorage(BaseStorage):
    REDIS_DATA_KEY: str = "data"

    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def save_state(self, state: dict) -> None:
        self.redis_adapter.hmset(self.REDIS_DATA_KEY, json.loads(json.dumps(state)))

    def retrieve_state(self) -> dict:
        return self.redis_adapter.hgetall(RedisStorage.REDIS_DATA_KEY)


class State:
    """Состояние при работе с данными, чтобы постоянно не перечитывать данные с начала."""

    def __init__(self, storage: RedisStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        state = self.storage.retrieve_state()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""
        return self.storage.retrieve_state().get(key)
