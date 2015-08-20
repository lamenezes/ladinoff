# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='_id',
            field=models.PositiveIntegerField(default=0, unique=True, verbose_name='id'),
        ),
        migrations.AddField(
            model_name='fanfiction',
            name='genre',
            field=models.TextField(null=True, verbose_name='G\xeanero', blank=True),
        ),
        migrations.AddField(
            model_name='fanfiction',
            name='ship',
            field=models.TextField(null=True, verbose_name='Ship', blank=True),
        ),
        migrations.AddField(
            model_name='fanfiction',
            name='status',
            field=models.TextField(null=True, verbose_name='Status', blank=True),
        ),
    ]
