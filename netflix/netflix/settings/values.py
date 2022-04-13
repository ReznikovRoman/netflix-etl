from __future__ import annotations

from configurations import values


_NOTSET = object()


_value_classes = {
    str: values.Value,
    int: values.IntegerValue,
    float: values.FloatValue,
    bool: values.BooleanValue,
    list: values.ListValue,
    tuple: values.TupleValue,
    dict: values.DictValue,
}


def from_environ(default=_NOTSET, /, *, name: str | None = None, type=_NOTSET, **kwargs):
    kwargs['environ'] = True
    kwargs.setdefault('environ_prefix', None)
    if default is _NOTSET:
        kwargs['environ_required'] = True
    else:
        kwargs['environ_required'] = False
        kwargs['default'] = default
    if name:
        kwargs['environ_name'] = name
    if type is _NOTSET:
        if default is _NOTSET or default is None:
            type = str
        else:
            type = object.__class__(default)
    return _value_classes[type](**kwargs)
