# Generated by Django 4.2.18 on 2025-02-28 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_remove_profile_watchlist_future_futurewatchlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='futurewatchlist',
            name='category',
            field=models.CharField(choices=[('movie', 'Movie'), ('tv', 'TV Show'), ('book', 'Book'), ('boardgame', 'Board Game'), ('videogame', 'Video Game')], max_length=20),
        ),
    ]
