# -*- coding: utf-8 -*-

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

    author = models.ForeignKey('Author', verbose_name='Autor',
                               null=True, blank=True)

    category = models.ForeignKey('SubCategory', verbose_name=u'SubCategoria',
                                 null=True, blank=True)

    rated = models.PositiveSmallIntegerField(u'Rated',
                                    null=True, blank=True)

    language = models.CharField(u'Idioma', max_length=16,
                                    null=True, blank=True)

    chapters = models.PositiveIntegerField(u'Capítulos',
                                    null=True, blank=True)

    words = models.PositiveIntegerField(u'Palavras',
                                    null=True, blank=True)

    reviews = models.PositiveIntegerField(u'Reviews',
                                    null=True, blank=True)

    favorites = models.PositiveIntegerField(u'Favorites',
                                    null=True, blank=True)

    follows = models.PositiveIntegerField(u'Follows',
                                    null=True, blank=True)

    first_paragraph = models.TextField(u'1o Parágrafo',
                                    null=True, blank=True)

    last_paragraph = models.TextField(u'Último Parágrafo',
                                    null=True, blank=True)

    link = models.URLField(u'Link')

    is_complete = models.BooleanField(default=False)

    @classmethod
    def crawl_categories(cls, category_url, category):
        current_url = ''
        fics = {}
        found = True
        page_number = 1

        search = re.search('p=(?P<page_number>\d+)', category_url)
        if search:
            page_number = int(search.groupdict()['page_number'])

        while found:
            if page_number > 1:
                current_url = category_url + ('&p=%d' % page_number)
            else:
                current_url = category_url
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
            links = {link.get('href'): link[0].tail for link in links}
            fics = []
            for link, title in links.items():
                fic = FanFiction(title=title, link=link, category=category)
                fics.append(fic)
            FanFiction.objects.bulk_create(fics)
            print 'Parsing page %d' % page_number
            page_number += 1

    def crawl_fic(self):
        if self.is_complete:
            return
