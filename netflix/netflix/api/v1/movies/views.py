from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from netflix.api.pagination import YandexStandardResultsSetPagination
from netflix.api.views import MultiSerializerViewSetMixin
from netflix.movies.models import Filmwork
from netflix.movies.repositories import FilmworkRepository

from . import openapi
from .serializers import FilmworkSerializer


class MovieViewSet(
    MultiSerializerViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Viewset для работы с кинопроизведениями."""

    queryset = Filmwork.objects.none()
    permission_classes = [
        AllowAny,
    ]
    pagination_class = YandexStandardResultsSetPagination
    serializer_classes = {
        "list": FilmworkSerializer,
        "retrieve": FilmworkSerializer,
    }

    def get_queryset(self):
        return FilmworkRepository.get_filmworks_with_related_data()

    @openapi.filmwork_list
    def list(self, request, *args, **kwargs):
        return super(MovieViewSet, self).list(request, *args, **kwargs)

    @openapi.filmwork_detail
    def retrieve(self, request, *args, **kwargs):
        return super(MovieViewSet, self).retrieve(request, *args, **kwargs)
