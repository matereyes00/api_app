# Generated by Django 4.2.18 on 2025-03-09 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_fourfavorite'),
    ]

    operations = [
        migrations.RenameField(
            model_name='favorite',
            old_name='image_url',
            new_name='image',
        ),
        migrations.RenameField(
            model_name='fourfavorite',
            old_name='image_url',
            new_name='image',
        ),
    ]
