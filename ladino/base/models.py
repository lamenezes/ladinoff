from django.db import models


class Author(models.Model):
    """
    """

    class Meta:
        app_label = 'base'
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'

    def __repr__(self):
        return '{}: {}'.format(self._id, self.nickname)

    _id = models.PositiveIntegerField('id', unique=True, default=0)

    nickname = models.CharField(max_length=128)

    link = models.TextField('Link')

    join_date = models.DateField('Join Date', null=True, blank=True)

    stories = models.IntegerField('Fics', null=True, blank=True)

    favorite_stories = models.IntegerField('Fav fics', null=True, blank=True)

    favorite_authors = models.IntegerField('Fav authros', null=True, blank=True)


class Category(models.Model):
    class Meta:
        app_label = 'base'
        verbose_name = 'Categoria'

    def __repr__(self):
        return self.title

    title = models.CharField(max_length=128)


class SubCategory(models.Model):
    class Meta:
        app_label = 'base'
        verbose_name = 'Autor'

    def __repr__(self):
        return '{} / {}'.format(self.category.title, self.title)

    title = models.CharField(max_length=300)

    category = models.ForeignKey('Category', verbose_name='Categoria')

    fanfic_qty = models.CharField('Qtde.', max_length=8, blank=True)

    link = models.TextField('Link')


class FanFiction(models.Model):
    """
    """

    class Meta:
        app_label = 'base'
        ordering = ['title']
        verbose_name = 'FanFic'

    def __repr__(self):
        return '({}) {}'.format(self.category, self.title)

    title = models.TextField('Título')

    publish_date = models.DateField('Data Publicação',
                                    null=True, blank=True)

    author = models.ForeignKey('Author', verbose_name='Autor', null=True, blank=True)

    category = models.ForeignKey('SubCategory', verbose_name='SubCategoria',
                                 null=True, blank=True)

    rated = models.CharField('Rated', max_length=32, null=True, blank=True)

    language = models.CharField('Idioma', max_length=16, null=True, blank=True)

    chapters = models.PositiveIntegerField('Capítulos', null=True, blank=True)

    words = models.PositiveIntegerField('Palavras', null=True, blank=True)

    reviews = models.PositiveIntegerField('Reviews', null=True, blank=True)

    favorites = models.PositiveIntegerField('Favorites', null=True, blank=True)

    follows = models.PositiveIntegerField('Follows', null=True, blank=True)

    first_paragraph = models.TextField('1o Parágrafo', null=True, blank=True)

    last_paragraph = models.TextField('Último Parágrafo', null=True, blank=True)

    genre = models.TextField('Gênero', null=True, blank=True)

    ship = models.TextField('Ship', null=True, blank=True)

    status = models.TextField('Status', null=True, blank=True)

    link = models.TextField('Link')

    is_complete = models.BooleanField(default=False)
