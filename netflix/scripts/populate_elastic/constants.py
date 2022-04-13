from typing import Final


# Время обновления ETL пайплайна (повторный запуск)
ETL_REFRESH_TIME_SECONDS: Final[int] = 5

# Название индекса в Elasticsearch
ES_INDEX_NAME: Final[str] = "movies"

# Название ключа в сервисе состояния, в котором хранится значение последнего запуска пайплайна
ETL_TIMESTAMP_KEY: Final[str] = "last_run_at"

# Название ключа в сервисе состояния, в котором хранятся индексы последних добавленных объектов в Elasticsearch
ETL_LAST_INDEXES_KEY: Final[str] = "last_indexes"
