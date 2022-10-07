from typing import Final

# The name of the key in the `State` service, which stores values of the last pipeline launches
ETL_PERSON_LOADED_IDS_KEY: Final[str] = "person:last_ids"

# Index name in Elasticsearch
ETL_PERSON_INDEX_NAME: Final[str] = "person"
