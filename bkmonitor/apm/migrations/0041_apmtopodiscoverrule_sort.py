# Generated by Django 3.2.15 on 2024-07-24 13:17

from django.db import migrations, models


def update_discover_rules(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("apm", "0040_profileservice_is_large"),
    ]

    operations = [
        migrations.AddField(
            model_name="apmtopodiscoverrule",
            name="sort",
            field=models.IntegerField(default=0, verbose_name="排序"),
        ),
        migrations.RunPython(update_discover_rules),
    ]
