# Generated by Django 3.2.15 on 2024-06-04 04:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('metadata', '0181_recordrule_resulttableflow'),
    ]

    operations = [
        migrations.AddField(
            model_name='esstorage',
            name='index_set',
            field=models.TextField(blank=True, null=True, verbose_name='索引集'),
        ),
        migrations.AddField(
            model_name='esstorage',
            name='source_type',
            field=models.CharField(
                default='log', help_text='数据源类型，仅对日志内置集群索引进行生命周期管理', max_length=16, verbose_name='数据源类型'
            ),
        ),
        migrations.AlterField(
            model_name='esstorage',
            name='index_settings',
            field=models.TextField(blank=True, null=True, verbose_name='索引配置信息'),
        ),
        migrations.AlterField(
            model_name='esstorage',
            name='mapping_settings',
            field=models.TextField(blank=True, null=True, verbose_name='别名配置信息'),
        ),
    ]
