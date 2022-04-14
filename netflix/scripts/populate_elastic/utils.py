import logging

from exceptions import ImproperlyConfiguredError


logger = logging.getLogger(__name__)


def RequiredAttributes(*required_attrs):  # noqa
    class RequiredAttributesMeta(type):
        def __init__(cls, name, bases, attrs):
            if not bases:
                return
            if missing_attrs := [attr for attr in required_attrs if not hasattr(cls, attr)]:
                raise ImproperlyConfiguredError(f"{name!r} requires attributes: {missing_attrs}")
    return RequiredAttributesMeta


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
