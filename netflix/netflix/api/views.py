from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type


if TYPE_CHECKING:
    from rest_framework.serializers import Serializer


class MultiSerializerViewSetMixin:
    """Миксин для выбора нужного сериалайзера из `serializer_classes`."""

    serializer_classes: Optional[dict[str, Type[Serializer]]] = None

    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except KeyError:
            return super().get_serializer_class()
