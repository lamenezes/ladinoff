# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nickname', models.CharField(max_length=64)),
                ('link', models.URLField(verbose_name='Link')),
                ('join_date', models.DateField(null=True, verbose_name='Join Date', blank=True)),
                ('stories', models.IntegerField(null=True, verbose_name='Fics', blank=True)),
                ('favorite_stories', models.IntegerField(null=True, verbose_name='Fav fics', blank=True)),
                ('favorite_authors', models.IntegerField(null=True, verbose_name='Fav authros', blank=True)),
            ],
            options={
                'verbose_name': 'Autor',
                'verbose_name_plural': 'Autores',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': 'Categoria',
            },
        ),
        migrations.CreateModel(
            name='FanFiction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='T\xedtulo')),
                ('publish_date', models.DateField(null=True, verbose_name='Data Publica\xe7\xe3o', blank=True)),
                ('rated', models.PositiveSmallIntegerField(null=True, verbose_name='Rated', blank=True)),
                ('language', models.CharField(max_length=16, null=True, verbose_name='Idioma', blank=True)),
                ('chapters', models.PositiveIntegerField(null=True, verbose_name='Cap\xedtulos', blank=True)),
                ('words', models.PositiveIntegerField(null=True, verbose_name='Palavras', blank=True)),
                ('reviews', models.PositiveIntegerField(null=True, verbose_name='Reviews', blank=True)),
                ('favorites', models.PositiveIntegerField(null=True, verbose_name='Favorites', blank=True)),
                ('follows', models.PositiveIntegerField(null=True, verbose_name='Follows', blank=True)),
                ('first_paragraph', models.TextField(null=True, verbose_name='1o Par\xe1grafo', blank=True)),
                ('last_paragraph', models.TextField(null=True, verbose_name='\xdaltimo Par\xe1grafo', blank=True)),
                ('link', models.URLField(verbose_name='Link')),
                ('is_complete', models.BooleanField(default=False)),
                ('author', models.ForeignKey(verbose_name=b'Autor', blank=True, to='base.Author', null=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'FanFic',
            },
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=300)),
                ('fanfic_qty', models.CharField(max_length=8, verbose_name=b'Qtde.', blank=True)),
                ('link', models.TextField(verbose_name='Link')),
                ('category', models.ForeignKey(verbose_name='Categoria', to='base.Category')),
            ],
            options={
                'verbose_name': 'Autor',
            },
        ),
        migrations.AddField(
            model_name='fanfiction',
            name='category',
            field=models.ForeignKey(verbose_name='SubCategoria', blank=True, to='base.SubCategory', null=True),
        ),
    ]
