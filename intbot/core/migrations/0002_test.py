# Generated by Django 5.1.4 on 2025-01-09 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webhook',
            name='meta',
            field=models.JSONField(default=dict),
        ),
    ]
