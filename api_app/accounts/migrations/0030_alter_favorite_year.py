# Generated by Django 4.2.18 on 2025-03-09 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_alter_favorite_options_alter_favorite_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='year',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
