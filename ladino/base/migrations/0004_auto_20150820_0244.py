# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20150820_0232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='link',
            field=models.TextField(verbose_name='Link'),
        ),
        migrations.AlterField(
            model_name='fanfiction',
            name='link',
            field=models.TextField(verbose_name='Link'),
        ),
        migrations.AlterField(
            model_name='fanfiction',
            name='title',
            field=models.TextField(verbose_name='T\xedtulo'),
        ),
    ]
