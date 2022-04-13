import logging


logger = logging.getLogger(__name__)


def retry(times, exceptions):
    def decorator(func):
        def fn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logger.info('Exception thrown when attempting to run %s, attempt %d of %d' % (func, attempt, times))
                    attempt += 1
            return func(*args, **kwargs)
        return fn
    return decorator
