from django.contrib import admin

from api.constants import PER_PAGE

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)


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
        'image_tag',
    )
    inlines = [
        IngredientInline,
        TagInline
    ]
    fields = ['image_tag']
    readonly_fields = ['image_tag']
    empty_value_display = 'значение отсутствует'
    list_editable = ('author',)
    list_filter = ('author__username', 'name', 'tags__name')
    list_per_page = PER_PAGE
    search_fields = ('author__username', 'name')

    @admin.display(description='Список ингредиентов')
    def ingredient_list(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()])

    @admin.display(description='Список тегов')
    def tag_list(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Класс настройки соответствия ингредиентов и рецептов."""

    list_display = (
        'pk',
        'ingredient',
        'amount',
        'recipe'
    )
    search_fields = ('ingredient__name', 'recipe__name')
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
    list_filter = ('user__username', 'recipe__name')
    search_fields = ('user__username', 'recipe__name')
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
    list_filter = ('user__username', 'recipe__name')
    search_fields = ('user__username', 'recipe__name')
    list_per_page = PER_PAGE


class RecipeTagAdmin(admin.ModelAdmin):
    """Класс настройки связи рецептов и тегов."""

    list_display = ('recipe', 'tag')
    search_fields = ('recipe__name', 'tag__name')
    list_filter = ('recipe__name', 'tag__name')
