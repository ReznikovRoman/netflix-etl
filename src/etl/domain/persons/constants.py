from typing import Final

# Название ключа в сервисе состояния, в котором хранятся значения последних запусков пайплайна
ETL_PERSON_LOADED_IDS_KEY: Final[str] = "person:last_ids"

# Название индекса в Elasticsearch
ETL_PERSON_INDEX_NAME: Final[str] = "person"
