from typing import Any, TypeVar

from django.db.models import Model


Id = int | str

_FieldLookup = str
_FieldValue = Any

ORMFilters = dict[_FieldLookup, _FieldValue]

_Model = TypeVar("_Model", bound=Model)
