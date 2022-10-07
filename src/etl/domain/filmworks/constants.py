from typing import Final

# The name of the key in the `State` service, which stores values of the last pipeline launches
ETL_FILMWORK_LOADED_IDS_KEY: Final[str] = "filmwork:last_ids"

# Index name in Elasticsearch
ETL_FILMWORK_INDEX_NAME: Final[str] = "movies"
