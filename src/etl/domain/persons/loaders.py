from etl.domain.loaders import ElasticLoader

from .constants import ETL_PERSON_INDEX_NAME, ETL_PERSON_LOADED_IDS_KEY


class PersonLoader(ElasticLoader):
    """`Загрузчик` данных о Персонах."""

    etl_loaded_entities_ids_key = ETL_PERSON_LOADED_IDS_KEY

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
                "full_name": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword",
                        },
                    },
                },
                "films_ids": {
                    "type": "keyword",
                },
                "roles": {
                    "type": "nested",
                    "properties": {
                        "role": {
                            "type": "text",
                            "analyzer": "ru_en",
                            "fields": {
                                "raw": {
                                    "type": "keyword",
                                },
                            },
                        },
                        "films": {
                            "type": "nested",
                            "properties": {
                                "uuid": {
                                    "type": "keyword",
                                },
                                "title": {
                                    "type": "text",
                                    "analyzer": "ru_en",
                                    "fields": {
                                        "raw": {
                                            "type": "keyword",
                                        },
                                    },
                                },
                                "imdb_rating": {
                                    "type": "float",
                                },
                                "age_rating": {
                                    "type": "text",
                                },
                                "access_type": {
                                    "type": "text",
                                },
                                "release_date": {
                                    "type": "date",
                                },
                            },
                        },
                    },
                },
            },
        },
    }

    es_index_name = ETL_PERSON_INDEX_NAME
