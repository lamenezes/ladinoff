# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20150825_0200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='nickname',
            field=models.CharField(max_length=128),
        ),
    ]
