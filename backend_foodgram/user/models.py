from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constants import (
    MAX_EMAIL_FIELD, MAX_NAME_FIELD,
    LENGTH_TEXT, HELP_TEXT_NAME, UNIQUE_FIELDS, MAX_PAS
)
from .validators import UsernameValidator, validate_username


class User(AbstractUser):
    """Расширенная стандартная Django модель"""

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        max_length=MAX_NAME_FIELD,
        unique=True,
        db_index=True,
        verbose_name='Имя пользователя',
        help_text=HELP_TEXT_NAME,
        validators=(UsernameValidator(), validate_username,),
        error_messages={
            'unique': UNIQUE_FIELDS[0],
        },
    )
    first_name = models.CharField(
        max_length=MAX_NAME_FIELD,
        verbose_name='Имя',
        help_text='Заполните Имя',
    )
    last_name = models.CharField(
        max_length=MAX_NAME_FIELD,
        verbose_name='Фамилия',
        help_text='Заполните Фамилию',
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_FIELD,
        unique=True,
        db_index=True,
        verbose_name='Электронная почта',
        help_text='Введите свой email',
        error_messages={
            'unique': UNIQUE_FIELDS[0],
        },
    )
    role = models.CharField(
        max_length=max(len(role) for role, _ in Role.choices),
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль пользователя',
        help_text='Уровень доступа пользователя'
    )
    password = models.CharField(
        max_length=MAX_PAS,
        verbose_name='пароль'
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    @property
    def is_admin(self):
        return (
            self.role == self.Role.ADMIN
            or self.is_superuser
            or self.is_staff
        )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username[:LENGTH_TEXT]


class Subscription(models.Model):
    follower = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name='follower',
                                 verbose_name='подписчик')
    following = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name='following',
                                  verbose_name='Автор')

    class Meta:
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_subscription'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.follower.username} подписан {self.following.username}'
