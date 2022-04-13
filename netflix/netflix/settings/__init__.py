from .base import Base


try:
    from .local import Local
except ImportError:
    LOCAL_CONFIGURATION_EXISTS = False
else:
    LOCAL_CONFIGURATION_EXISTS = True

__all__ = [
    'Base',
]

if LOCAL_CONFIGURATION_EXISTS:
    __all__ += ['Local']
