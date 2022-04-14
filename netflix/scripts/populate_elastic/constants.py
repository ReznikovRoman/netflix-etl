from typing import Final


# Время обновления ETL пайплайна (повторный запуск)
ETL_REFRESH_TIME_SECONDS: Final[int] = 30

# Название ключей в сервисе состояния, в которых хранятся значения последних запусков пайплайна
ETL_FILMWORK_LOADED_IDS_KEY: Final[str] = "filmwork:last_ids"

# Названия индексов в Elasticsearch
ETL_FILMWORK_INDEX_NAME: Final[str] = "movies"
