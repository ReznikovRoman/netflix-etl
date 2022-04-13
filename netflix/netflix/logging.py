import logging


class LoggerDescriptor:

    def __init__(self, prefix=None):
        self._prefix = prefix

    def __get__(self, instance, owner) -> logging.Logger:
        name = owner.__qualname__
        if self._prefix:
            name = f'{self._prefix}.{name}'
        logger = logging.getLogger(name)
        setattr(owner, self._logger_attr_name, logger)
        return logger

    def __set_name__(self, owner, name):
        self._logger_attr_name = name
