# Generated by Django 4.2.18 on 2025-02-24 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_favorite'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='watchlist',
            new_name='watchlist_past',
        ),
        migrations.AddField(
            model_name='profile',
            name='watchlist_future',
            field=models.JSONField(default=dict),
        ),
    ]
