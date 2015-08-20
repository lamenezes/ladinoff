# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20150820_0113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fanfiction',
            name='rated',
            field=models.CharField(max_length=32, null=True, verbose_name='Rated', blank=True),
        ),
    ]
