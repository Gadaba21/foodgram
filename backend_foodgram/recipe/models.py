import secrets
import string

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


from api.constants import (
    HASH_LENGTH,
    MAX_LENGTH,
    MAX_SLAG,
    MAX_VALUE,
    MIN_VALUE
)
from user.models import User

from .validators import validate_slug


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=MAX_SLAG,
        unique=True,
        validators=(validate_slug,)
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиент',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message=f'Время готовки должно быть больше {MIN_VALUE} минуты'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message=f'Время готовки должно быть меньше {MAX_VALUE} минут'
            )
        ],
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        verbose_name='Картинка',
    )
    text = models.TextField(verbose_name='описание')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
        db_index=True
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_recipe',
        verbose_name='рецепт'
    )
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower_recipe',
                             verbose_name='Пользователь')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        )
        ordering = ('id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message=f'Количество не может быть меньше {MIN_VALUE}'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message=f'Количество не может быть больше {MAX_VALUE}'
            )
        ],
    )

    class Meta:
        verbose_name = 'Соответствие ингредиента и рецепта'
        verbose_name_plural = 'Таблица соответствия ингредиентов и рецептов'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.recipe} содержит ингредиент/ты {self.ingredient}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_user',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Рецепт пользователя для списка покупок'
        verbose_name_plural = 'Рецепты пользователей для списка покупок'
        ordering = ('user',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'


class LinkMapped(models.Model):
    def generate_hash():
        length = HASH_LENGTH
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    url_hash = models.CharField(
        max_length=MAX_LENGTH, default=generate_hash, unique=True
    )
    original_url = models.CharField(max_length=MAX_LENGTH)

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return f'{self.original_url} -> {self.url_hash}'
