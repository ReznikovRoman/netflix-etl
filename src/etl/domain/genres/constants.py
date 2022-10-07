from typing import Final

# The name of the key in the `State` service, which stores values of the last pipeline launches
ETL_GENRE_LOADED_IDS_KEY: Final[str] = "genre:last_ids"

# Index name in Elasticsearch
ETL_GENRE_INDEX_NAME: Final[str] = "genre"
