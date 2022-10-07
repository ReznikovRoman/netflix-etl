from dependency_injector import containers, providers

from etl.config.logging import configure_logger
from etl.domain import filmworks, genres, persons, pipelines
from etl.infrastructure.db import elastic, postgres, redis, state


class Container(containers.DeclarativeContainer):
    """DI container."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "__main__",
        ],
    )

    config = providers.Configuration()

    logging = providers.Resource(configure_logger)

    # Infrastructure

    elastic_connection = providers.Resource(
        elastic.init_elastic,
        host=config.ES_HOST,
        port=config.ES_PORT,
        retry_on_timeout=config.ES_RETRY_ON_TIMEOUT,
    )

    postgres_connection = providers.Resource(
        postgres.init_postgres,
        db_name=config.DB_NAME,
        db_user=config.DB_USER,
        db_password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
    )

    redis_connection = providers.Resource(
        redis.init_redis,
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        decode_responses=config.REDIS_DECODE_RESPONSES,
    )

    redis_storage = providers.Singleton(
        state.RedisStorage,
        redis_client=redis_connection,
    )

    state = providers.Singleton(
        state.State,
        storage=redis_storage,
    )

    # ETL -> Extractors

    filmwork_extractor = providers.Singleton(
        filmworks.FilmworkExtractor,
        pg_conn=postgres_connection,
        state=state,
    )

    genre_extractor = providers.Singleton(
        genres.GenreExtractor,
        pg_conn=postgres_connection,
        state=state,
    )

    person_extractor = providers.Singleton(
        persons.PersonExtractor,
        pg_conn=postgres_connection,
        state=state,
    )

    # ETL -> Transformers

    filmwork_transformer = providers.Singleton(filmworks.FilmworkTransformer)

    genre_transformer = providers.Singleton(genres.GenreTransformer)

    person_transformer = providers.Singleton(persons.PersonTransformer)

    # ETL -> Loaders

    filmwork_loader = providers.Singleton(
        filmworks.FilmworkLoader,
        elastic_client=elastic_connection,
        state=state,
    )

    genre_loader = providers.Singleton(
        genres.GenreLoader,
        elastic_client=elastic_connection,
        state=state,
    )

    person_loader = providers.Singleton(
        persons.PersonLoader,
        elastic_client=elastic_connection,
        state=state,
    )

    # ETL -> Pipelines

    filmwork_pipeline = providers.Singleton(
        pipelines.ETLPipeline,
        loader=filmwork_loader,
        transformer=filmwork_transformer,
        extractor=filmwork_extractor,
        state=state,
    )

    genre_pipeline = providers.Singleton(
        pipelines.ETLPipeline,
        loader=genre_loader,
        transformer=genre_transformer,
        extractor=genre_extractor,
        state=state,
    )

    person_pipeline = providers.Singleton(
        pipelines.ETLPipeline,
        loader=person_loader,
        transformer=person_transformer,
        extractor=person_extractor,
        state=state,
    )

    pipelines_to_run = providers.List(filmwork_pipeline, genre_pipeline, person_pipeline)
