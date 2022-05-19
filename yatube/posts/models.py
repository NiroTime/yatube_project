from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста'
    )
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
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )

    def __str__(self):
        return self.text[:settings.TEXT_MAX_LENGTH]

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']


class Group(models.Model):
    title = models.CharField(
        max_length=200,
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
