import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # noqa: VNE003

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    """Жанр у фильма в онлайн-кинотеатре."""

    name = models.CharField(_('name'), max_length=255, unique=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class FilmworkType(models.TextChoices):
    """Тип фильма в онлайн-кинотеатре."""

    MOVIE = 'MV', _('Film')
    TV_SHOW = 'TV', _('TV show')


class Filmwork(UUIDMixin, TimeStampedMixin):
    """Фильм в онлайн-кинотеатре."""

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('release date'), null=True, blank=True, db_index=True)
    rating = models.FloatField(
        _('rating'),
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    type = models.CharField(  # noqa: VNE003
        _("film's type"), max_length=2, choices=FilmworkType.choices, default=FilmworkType.MOVIE)
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField("Person", through="PersonFilmwork")

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('film')
        verbose_name_plural = _('films')

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    """Промежуточная таблица для связи жанров и фильмов."""

    film_work = models.ForeignKey('Filmwork', verbose_name=_('film'), on_delete=models.CASCADE)
    genre = models.ForeignKey(
        'Genre', verbose_name=_('genre'), on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _("film's genre")
        verbose_name_plural = _("film's genres")
        unique_together = (
            ('film_work', 'genre'),
        )


class Person(UUIDMixin, TimeStampedMixin):
    """Участник съемочной группы в фильме."""

    full_name = models.TextField(_("full name"), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _("crew member")
        verbose_name_plural = _("crew members")

    def __str__(self):
        return self.full_name


class PersonRole(models.TextChoices):
    """Роль участника съемочной команды."""

    ACTOR = 'actor', _('actor')
    DIRECTOR = 'director', _('director')
    WRITER = 'writer', _('writer')


class PersonFilmwork(UUIDMixin):
    """Промежуточная таблица для связи участников съемочной группы и фильмов."""

    film_work = models.ForeignKey('Filmwork', verbose_name=_("film"), on_delete=models.CASCADE)
    person = models.ForeignKey(
        'Person', verbose_name=_("crew member"), on_delete=models.CASCADE)
    role = models.TextField(_("role"), choices=PersonRole.choices, default=PersonRole.ACTOR)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _("film crew member")
        verbose_name_plural = _("film crew members")
        index_together = (
            ('film_work', 'person'),
        )
