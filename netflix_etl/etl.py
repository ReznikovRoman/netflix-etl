import logging
from time import sleep

from netflix_etl.constants import ETL_REFRESH_TIME_SECONDS
from netflix_etl.pipelines import FilmworkPipeline, GenrePipeline, PersonPipeline


def main():
    logging.debug("--- Start ETL pipelines")

    pipelines_to_run = (FilmworkPipeline, GenrePipeline)
    for pipeline in pipelines_to_run:
        pipeline().execute()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.DEBUG)

    while True:
        main()
        sleep(ETL_REFRESH_TIME_SECONDS)
