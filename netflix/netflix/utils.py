import os
import uuid
from datetime import datetime
from functools import partial


class cached_property:  # noqa: N801

    def __init__(self, func):
        self.func = func

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


def set_attrs(obj=None, /, **attrs):
    if obj is None:
        return partial(set_attrs, **attrs)
    for name, value in attrs.items():
        setattr(obj, name, value)
    return obj


def get_file_path(instance, filename, *, directory: str) -> str:
    ext = filename.split('.')[-1]
    filename = uuid.uuid4()
    now = datetime.now()
    return os.path.join(directory, datetime.strftime(now, '%Y/%m/'), f'{filename}.{ext}')


def filename_normalize(filename: str) -> str:
    return filename.replace('ё', 'ё').replace('й', 'й').replace('Ё', 'Ё').replace('Й', 'Й')
