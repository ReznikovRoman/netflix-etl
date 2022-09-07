from typing import Final

# Название ключа в сервисе состояния, в котором хранятся значения последних запусков пайплайна
ETL_GENRE_LOADED_IDS_KEY: Final[str] = "genre:last_ids"

# Название индекса в Elasticsearch
ETL_GENRE_INDEX_NAME: Final[str] = "genre"
