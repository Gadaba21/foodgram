from api.constants import PER_PAGE
from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс настройки раздела тегов."""

    list_display = (
        'pk',
        'name',
        'slug'
    )
    empty_value_display = 'значение отсутствует'
    list_filter = ('name',)
    list_per_page = PER_PAGE
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс настройки раздела ингредиентов."""

    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    empty_value_display = 'значение отсутствует'
    list_filter = ('name',)
    list_per_page = PER_PAGE
    search_fields = ('name',)


class IngredientAmountInline(admin.TabularInline):

    model = IngredientRecipe
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс настройки раздела рецептов."""

    list_display = (
        'pk',
        'name',
        'author',
        'text',
        'cooking_time',
        'image',
        'pub_date',
    )
    inlines = [
        IngredientAmountInline,
    ]

    empty_value_display = 'значение отсутствует'
    list_editable = ('author',)
    list_filter = ('author', 'name', 'tags')
    list_per_page = PER_PAGE
    search_fields = ('author', 'name')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Класс настройки соответствия ингредиентов и рецептов."""

    list_display = (
        'pk',
        'ingredient',
        'amount',
        'recipe'
    )
    empty_value_display = 'значение отсутствует'
    list_per_page = PER_PAGE


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Класс настройки раздела избранного."""

    list_display = (
        'pk',
        'user',
        'recipe',
    )

    empty_value_display = 'значение отсутствует'
    list_editable = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)
    list_per_page = PER_PAGE


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс настройки раздела рецептов, которые добавлены в список покупок."""

    list_display = (
        'pk',
        'recipe_cart',
        'user_cart',
    )

    empty_value_display = 'значение отсутствует'
    list_editable = ('recipe_cart', 'user_cart')
    list_filter = ('user_cart',)
    search_fields = ('user_cart',)
    list_per_page = PER_PAGE
