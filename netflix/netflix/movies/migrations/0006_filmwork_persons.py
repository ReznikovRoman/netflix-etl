# Generated by Django 3.2.12 on 2022-03-02 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_remove_filmwork_certificate'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmwork',
            name='persons',
            field=models.ManyToManyField(through='movies.PersonFilmwork', to='movies.Person'),
        ),
    ]
