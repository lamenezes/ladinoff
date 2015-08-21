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

    link = models.TextField(u'Link')

    join_date = models.DateField(u'Join Date', null=True, blank=True)

    stories = models.IntegerField(u'Fics', null=True, blank=True)

    favorite_stories = models.IntegerField(u'Fav fics', null=True, blank=True)

    favorite_authors = models.IntegerField(u'Fav authros', null=True, blank=True)


class Category(models.Model):
    class Meta:
        app_label = 'base'
        verbose_name = u'Categoria'

    def __repr__(self):
        return self.title

    title = models.CharField(max_length=64)


class SubCategory(models.Model):
    class Meta:
        app_label = 'base'
        verbose_name = u'Autor'

    def __repr__(self):
        return u'%s / %s' % (self.category.title, self.title)

    title = models.CharField(max_length=300)

    category = models.ForeignKey('Category', verbose_name=u'Categoria')

    fanfic_qty = models.CharField('Qtde.', max_length=8, blank=True)

    link = models.TextField(u'Link')


class FanFiction(models.Model):
    """
    """

    class Meta:
        app_label = 'base'
        ordering = ['title']
        verbose_name = u'FanFic'

    def __repr__(self):
        return '(%s) %s' % (self.category, self.title)

    title = models.TextField(u'Título')

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

    link = models.TextField(u'Link')

    is_complete = models.BooleanField(default=False)
