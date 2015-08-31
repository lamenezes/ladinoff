# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20150820_0244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fanfiction',
            name='author',
            field=models.ForeignKey(to='base.Author', blank=True, null=True, verbose_name='Autor'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='fanfic_qty',
            field=models.CharField(verbose_name='Qtde.', max_length=8, blank=True),
        ),
    ]
