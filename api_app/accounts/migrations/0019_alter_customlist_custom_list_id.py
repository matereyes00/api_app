# Generated by Django 4.2.18 on 2025-03-07 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_remove_customlist_id_customlist_custom_list_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customlist',
            name='custom_list_id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
