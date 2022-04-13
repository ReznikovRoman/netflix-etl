from rest_framework import serializers

from netflix.movies.models import Filmwork


class NameListField(serializers.ListField):
    """Поле для списка имен/названий."""

    name = serializers.CharField(read_only=True)


class FilmworkSerializer(serializers.ModelSerializer):
    """Сериалайзер для кинопроизведений."""

    genres = NameListField(read_only=True)
    actors = NameListField(read_only=True)
    directors = NameListField(read_only=True)
    writers = NameListField(read_only=True)

    class Meta:
        model = Filmwork
        fields = [
            "id", "title", "description", "creation_date", "rating", "type", "genres", "actors", "directors", "writers",
        ]
