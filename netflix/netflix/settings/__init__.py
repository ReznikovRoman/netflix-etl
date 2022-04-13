from .base import Base
from .external import External


try:
    from .local import Local
except ImportError:
    LOCAL_CONFIGURATION_EXISTS = False
else:
    LOCAL_CONFIGURATION_EXISTS = True

__all__ = [
    'Base',
    'External',
]

if LOCAL_CONFIGURATION_EXISTS:
    __all__ += ['Local']
