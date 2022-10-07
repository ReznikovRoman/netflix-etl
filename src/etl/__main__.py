from __future__ import annotations

import logging
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING, Sequence

from dependency_injector.wiring import Provide, inject

from etl.config.settings import get_settings

from .constants import ETL_REFRESH_TIME_SECONDS
from .containers import Container

if TYPE_CHECKING:
    from etl.domain.pipelines import ETLPipeline

settings = get_settings()


@inject
def main(pipelines_to_run: Sequence[ETLPipeline] = Provide[Container.pipelines_to_run]) -> None:
    """Launch all ETL pipelines."""
    logging.info("Start ETL pipelines")

    threads = []
    for pipeline in pipelines_to_run:
        process = Thread(target=pipeline.execute)
        process.start()
        threads.append(process)

    for process in threads:
        process.join()


if __name__ == "__main__":
    container = Container()
    container.config.from_pydantic(settings=settings)
    container.init_resources()
    container.check_dependencies()

    while True:
        main()
        sleep(ETL_REFRESH_TIME_SECONDS)
