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


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    verbose_name = 'Тег'
    verbose_name_plural = 'Теги'


class IngredientInline(admin.StackedInline):
    model = IngredientRecipe
    extra = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс настройки раздела рецептов."""

    list_display = (
        'pk',
        'name',
        'author',
        'text',
        'cooking_time',
        'pub_date',
        'ingredient_list',
        'tag_list',
    )
    inlines = [
        IngredientInline,
        TagInline
    ]
    fields = ['image_tag']
    readonly_fields = ['image_tag']
    empty_value_display = 'значение отсутствует'
    list_editable = ('author',)
    list_filter = ('author', 'name', 'tags')
    list_per_page = PER_PAGE
    search_fields = ('author', 'name')

    def ingredient_list(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()])

    def tag_list(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    ingredient_list.short_description = 'Список ингредиентов'
    tag_list.short_description = 'Список тегов'


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
        'recipe',
        'user',
    )

    empty_value_display = 'значение отсутствует'
    list_editable = ('recipe', 'user')
    list_filter = ('user',)
    search_fields = ('user',)
    list_per_page = PER_PAGE
