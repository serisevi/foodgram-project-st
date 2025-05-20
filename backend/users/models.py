from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram.constants import NAME_MAX_LENGTH


class User(AbstractUser):
    """Модель пользователя."""

    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    USERNAME_FIELD = 'email'

    username = models.CharField(
        unique=True,
        max_length=NAME_MAX_LENGTH,
        validators=[UnicodeUsernameValidator(), ],
        verbose_name='Никнейм',
        help_text='Укажите никнейм'
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Имя',
        help_text='Укажите имя'
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Фамилия',
        help_text='Укажите фамилию'
    )
    email = models.EmailField(
        unique=True,
        max_length=NAME_MAX_LENGTH,
        verbose_name='E-mail',
        help_text='Укажите e-mail'
    )
    avatar = models.ImageField(
        upload_to='avatar/images/',
        verbose_name='Аватар',
        blank=True,
        null=True,
    )

    class Meta:
        """Метаданные модели."""
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Строковое представление модели."""
        return self.username


class Subscribers(models.Model):
    """Модель для хранения подписок пользователей."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор',
        help_text='Укажите автора'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик',
        help_text='Укажите подписчика'
    )

    class Meta:
        """Метаданные модели."""
        ordering = ('author',)
        verbose_name = 'Подписки'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author_user'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='author_and_user_different',
            )
        ]

    def __str__(self):
        """Строковое представление модели."""
        return f"{self.author} - {self.user}"
