from typing import Final

# Время обновления ETL пайплайна (повторный запуск)
ETL_REFRESH_TIME_SECONDS: Final[int] = 30

# Название ключей в сервисе состояния, в которых хранятся значения последних запусков пайплайна
ETL_FILMWORK_LOADED_IDS_KEY: Final[str] = "filmwork:last_ids"
ETL_GENRE_LOADED_IDS_KEY: Final[str] = "genre:last_ids"
ETL_PERSON_LOADED_IDS_KEY: Final[str] = "person:last_ids"

# Названия индексов в Elasticsearch
ETL_FILMWORK_INDEX_NAME: Final[str] = "movies"
ETL_GENRE_INDEX_NAME: Final[str] = "genre"
ETL_PERSON_INDEX_NAME: Final[str] = "person"
