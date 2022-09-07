from typing import Final

# Название ключа в сервисе состояния, в котором хранятся значения последних запусков пайплайна
ETL_FILMWORK_LOADED_IDS_KEY: Final[str] = "filmwork:last_ids"

# Название индекса в Elasticsearch
ETL_FILMWORK_INDEX_NAME: Final[str] = "movies"
