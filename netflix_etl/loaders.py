from __future__ import annotations

import logging
from typing import ClassVar, Iterator

from elasticsearch import Elasticsearch, helpers

from netflix_etl.constants import (
    ETL_FILMWORK_INDEX_NAME, ETL_FILMWORK_LOADED_IDS_KEY, ETL_GENRE_INDEX_NAME, ETL_GENRE_LOADED_IDS_KEY,
    ETL_PERSON_INDEX_NAME, ETL_PERSON_LOADED_IDS_KEY,
)
from netflix_etl.state import State
from netflix_etl.utils import RequiredAttributes


class ElasticLoader(metaclass=RequiredAttributes("etl_loaded_entities_ids_key", "es_index", "es_index_name")):
    """`Загрузчик` данных в Elasticsearch."""

    etl_loaded_entities_ids_key: ClassVar[str]

    es_index: ClassVar[dict]
    es_index_name: ClassVar[str]
    es_timeout: ClassVar[str] = "3s"

    entity_id_field: ClassVar[str] = "uuid"

    def __init__(self, es: Elasticsearch, state: State, logger: logging):
        self._es = es
        self._state = state
        self._logger = logger

    def create_index(self):
        self._es.indices.create(
            index=self.es_index_name,
            body=self.es_index,
            ignore=[400],
            timeout=self.es_timeout,
        )

    def update_index(self, data: Iterator[dict]) -> tuple[int, int | list]:
        return helpers.bulk(self._es, data)

    def load(self, data: Iterator[dict]) -> None:
        data = list(data)

        self.create_index()
        self.update_index(data)

        self.post_load(data=data)

    def post_load(self, *args, **kwargs) -> None:
        self.update_ids_in_state(kwargs["data"])

    def update_ids_in_state(self, data) -> None:
        ids = ",".join([str(entity_data["_source"][self.entity_id_field]) for entity_data in data])
        self._state.set_state(self.etl_loaded_entities_ids_key, ids)


class FilmworkLoader(ElasticLoader):
    """`Загрузчик` данных о Фильмах."""

    etl_loaded_entities_ids_key = ETL_FILMWORK_LOADED_IDS_KEY

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
                "imdb_rating": {
                    "type": "float",
                },
                "age_rating": {
                    "type": "text",
                },
                "release_date": {
                    "type": "date",
                },
                "genre": {
                    "type": "nested",
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
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword",
                        },
                    },
                },
                "description": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
                "genres_names": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
                "actors_names": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
                "writers_names": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
                "directors_names": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
                "actors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword",
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en",
                        },
                    },
                },
                "writers": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword",
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en",
                        },
                    },
                },
                "directors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword",
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en",
                        },
                    },
                },
            },
        },
    }
    es_index_name = ETL_FILMWORK_INDEX_NAME


class GenreLoader(ElasticLoader):
    """`Загрузчик` данных о Жанрах."""

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
