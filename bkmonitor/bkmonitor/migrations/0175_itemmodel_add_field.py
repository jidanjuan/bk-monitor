# Generated by Django 3.2.25 on 2025-02-07 08:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bkmonitor', '0174_auto_20250205_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemmodel',
            name='time_delay',
            field=models.IntegerField(default=0, verbose_name='策略等待时间'),
        ),
    ]
