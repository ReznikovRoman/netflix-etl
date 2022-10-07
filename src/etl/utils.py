from etl.common.exceptions import ImproperlyConfiguredError


def RequiredAttributes(*required_attrs):  # noqa
    """Metaclass for specifying required class attributes."""

    class RequiredAttributesMeta(type):
        def __init__(cls, name, bases, attrs) -> None:
            if not bases:
                return
            if missing_attrs := [attr for attr in required_attrs if not hasattr(cls, attr)]:
                raise ImproperlyConfiguredError(f"{name!r} requires attributes: {missing_attrs}")

    return RequiredAttributesMeta
