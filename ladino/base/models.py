# -*- coding: utf-8 -*-

import datetime
from lxml import html
import re
import requests
import time

from django.db import models


class Author(models.Model):
    """
    """

    class Meta:
        app_label = 'base'
        verbose_name = u'Autor'
        verbose_name_plural = u'Autores'

    def __repr__(self):
        return '{}: {}' % (self._id, self.nickname)
    _id = models.PositiveIntegerField(u'id', unique=True, default=0)

    nickname = models.CharField(max_length=64)

    link = models.URLField(u'Link')

    join_date = models.DateField(u'Join Date', null=True, blank=True)

    stories = models.IntegerField(u'Fics', null=True, blank=True)

    favorite_stories = models.IntegerField(u'Fav fics', null=True, blank=True)

    favorite_authors = models.IntegerField(u'Fav authros', null=True, blank=True)


class Category(models.Model):
    class Meta:
        app_label = 'base'
        verbose_name = u'Categoria'

    def __unicode__(self):
        return self.title

    title = models.CharField(max_length=64)


class SubCategory(models.Model):
    class Meta:
        app_label = 'base'
        verbose_name = u'Autor'

    def __unicode__(self):
        return u'%s / %s' % (self.category.title, self.title)

    title = models.CharField(max_length=300)

    category = models.ForeignKey('Category', verbose_name=u'Categoria')

    fanfic_qty = models.CharField('Qtde.', max_length=8, blank=True)

    link = models.TextField(u'Link')

    @classmethod
    def crawl_subcategories(cls):
        base_url = 'http://fanfiction.net/'
        subcategories = []
        for category in Category.objects.all():
            url = base_url + category.title
            page = requests.get(url)
            tree = html.fromstring(page.text)
            print u'Categoria:', category.title
            table = tree.get_element_by_id('list_output')
            tr = table[0][0]
            for td in tr:
                for line in td:
                    raw = line.text_content()
                    s = re.search("(?P<title>.+) \((?P<qty>.+)\)", raw)
                    title = s.groupdict()['title']
                    qty = s.groupdict()['qty']
                    link = base_url + line[0].values()[0]
                    subcategory = SubCategory(title=title,
                                              category=category,
                                              fanfic_qty=qty,
                                              link=link)
                    subcategories.append(subcategory)

        return subcategories


class FanFiction(models.Model):
    """
    """

    class Meta:
        app_label = 'base'
        ordering = ['title']
        verbose_name = u'FanFic'

    def __unicode__(self):
        return '(%s) %s' % (self.category, self.title)

    title = models.CharField(u'Título', max_length=128)

    publish_date = models.DateField(u'Data Publicação',
                                    null=True, blank=True)

    author = models.ForeignKey('Author', verbose_name='Autor', null=True, blank=True)

    category = models.ForeignKey('SubCategory', verbose_name=u'SubCategoria',
                                 null=True, blank=True)

    rated = models.CharField(u'Rated', max_length=32, null=True, blank=True)

    language = models.CharField(u'Idioma', max_length=16, null=True, blank=True)

    chapters = models.PositiveIntegerField(u'Capítulos', null=True, blank=True)

    words = models.PositiveIntegerField(u'Palavras', null=True, blank=True)

    reviews = models.PositiveIntegerField(u'Reviews', null=True, blank=True)

    favorites = models.PositiveIntegerField(u'Favorites', null=True, blank=True)

    follows = models.PositiveIntegerField(u'Follows', null=True, blank=True)

    first_paragraph = models.TextField(u'1o Parágrafo', null=True, blank=True)

    last_paragraph = models.TextField(u'Último Parágrafo', null=True, blank=True)

    genre = models.TextField(u'Gênero', null=True, blank=True)

    ship = models.TextField(u'Ship', null=True, blank=True)

    status = models.TextField(u'Status', null=True, blank=True)

    link = models.URLField(u'Link')

    is_complete = models.BooleanField(default=False)

    @classmethod
    def crawl_categories(cls, categories=[]):
        search = '/?&srt=1&r=10'
        if not categories:
            categories = SubCategory.objects.all()

        for category in categories:
            # search = re.search('p=(?P<page_number>\d+)', category.link)
            # if search:
            #     page_number = int(search.groupdict()['page_number'])

            page_number = 1
            found = True
            while found:
                if page_number > 1:
                    current_url = category.link + search + ('&p=%d' % page_number)
                else:
                    current_url = category.link + search
                try:
                    page = requests.get(current_url)
                except requests.exceptions.ConnectionError:
                    print u'Connection Error'
                    time.sleep(10)
                    continue
                tree = html.fromstring(page.text)
                links = tree.xpath('//a[@class="stitle"]')
                if not links:
                    found = False
                    print 'Nao achei, chente'
                links = {link.get('href'): link[0].tail for link in links}
                fics = []
                for link, title in links.items():
                    fic = FanFiction(title=title, link=link, category=category)
                    fics.append(fic)
                FanFiction.objects.bulk_create(fics)
                print 'Parsing page %d' % page_number
                print fic
                page_number += 1

    def crawl_fic(self):
        if self.is_complete:
            return (self, False)

        page = requests.get('http://fanfiction.net' + self.link)
        tree = html.fromstring(page.text)
        span = tree.find('body//span[@class="xgray xcontrast_txt"]')
        fic_meta = span.text_content()
        regex = ('Rated: (?P<rated>[\\w ]+) - (?P<language>\\w+) - (?P<genre>[\\w/]+) - '
               '(?P<ship>[\[\]\\w., ]+) - Words: (?P<words>.*) - Reviews: '
               '(?P<reviews>[\\d\\w,]+) - Favs: (?P<favorites>[\\d\\w ]+) - '
               '(Follows: (?P<follows>[\\d\\w ]+) - )?'
               'Published: (?P<publish_date>[\\w\\d/ ]+) - '
               'Status: (?P<status>\w+) - id')
        try:
            fic_meta = re.search(regex, fic_meta).groupdict()
            pub_date = fic_meta['publish_date']
            fic_meta['publish_date'] = datetime.datetime.strptime(pub_date, '%d/%m/%Y')
            fic_meta['words'] = fic_meta['words'].replace(',', '')
            fic_meta['reviews'] = fic_meta['reviews'].replace(',', '')
            fic_meta['favorites'] = fic_meta['favorites'].replace(',', '')
            fic_meta['follows'] = fic_meta['follows'].replace(',', '')
        except AttributeError:
            return (self, False)

        b = tree.find('body//b[@class="xcontrast_txt"]')
        fic_meta['title'] = b.text_content()

        for attr, val in fic_meta.items():
            setattr(self, attr, val)

        a = tree.find('body//div[@id="profile_top"]//a[@class="xcontrast_txt"]')
        nickname = a.text_content()
        link = a.values()[1]
        s = re.search('/u/(?P<id>\d+)/', link)
        _id = s.groupdict()['id']

        if not self.author:
            try:
                author = Author.objects.get(_id=_id)
            except Author.DoesNotExist:
                author = Author(_id=_id, nickname=nickname, link=link)
                author.save()

        self.author = author
        self.save()

        return (self, True)
