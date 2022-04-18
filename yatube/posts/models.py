from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Пользователь',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Группа',
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']
        # не смог найти команду, которая ограничит
        # по символам поле text в админке


class Group(models.Model):
    title = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Группа',
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name='URL',
    )
    description = models.TextField(verbose_name='Описание Группы')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группу'
        verbose_name_plural = 'Группы'
        ordering = ['title']
