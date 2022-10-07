from etl.domain.loaders import ElasticLoader

from .constants import ETL_GENRE_INDEX_NAME, ETL_GENRE_LOADED_IDS_KEY


class GenreLoader(ElasticLoader):
    """Genres `Loader`."""

    etl_loaded_entities_ids_key = ETL_GENRE_LOADED_IDS_KEY

    es_index = {
        "settings": {
            "refresh_interval": "1s",
            "analysis": {
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_",
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english",
                    },
                    "english_possessive_stemmer": {
                        "type": "stemmer",
                        "language": "possessive_english",
                    },
                    "russian_stop": {
                        "type": "stop",
                        "stopwords": "_russian_",
                    },
                    "russian_stemmer": {
                        "type": "stemmer",
                        "language": "russian",
                    },
                },
                "analyzer": {
                    "ru_en": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer",
                            "english_possessive_stemmer",
                            "russian_stop",
                            "russian_stemmer",
                        ],
                    },
                },
            },
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword",
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword",
                        },
                    },
                },
            },
        },
    }
    es_index_name = ETL_GENRE_INDEX_NAME
