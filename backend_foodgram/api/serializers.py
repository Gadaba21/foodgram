from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueTogetherValidator

from recipe.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    LinkMapped,
    Recipe,
    ShoppingCart,
    Tag
)
from user.serializers import Base64ImageField, UserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientFullSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeGETSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientFullSerializer(source='ingredientrecipe_set',
                                           many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time'
                  )

    def get_is_favorited(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower_recipe.filter(recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart_user.filter(
            recipe=object).exists()


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(many=True, required=True)
    image = Base64ImageField(use_url=True, max_length=None, required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Добавьте хотя бы 1 ингредиент.')
        ingredients_data = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise serializers.ValidationError(
                'Ингредиенты рецепта должны быть уникальными'
            )
        return ingredients

    def validate_tags(self, tags):
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги рецепта должны быть уникальными'
            )
        return tags

    @staticmethod
    def add_ingredients(ingredients_data, recipe):
        if ingredients_data is not None:
            IngredientRecipe.objects.bulk_create([
                IngredientRecipe(
                    ingredient=ingredient.get('id'),
                    recipe=recipe,
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients_data
            ])
        else:
            raise serializers.ValidationError(
                'Ингредиенты рецепта должны быть'
            )

    @transaction.atomic
    def create(self, validated_data):
        if 'image' not in validated_data or not validated_data['image']:
            raise ValidationError({'image': 'Поле `image` обязательно'})
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'image' not in validated_data or not validated_data['image']:
            raise ValidationError({'image': 'Поле `image` обязательно'})
        if 'tags' not in validated_data or not validated_data['tags']:
            raise ValidationError({'tags': 'Поле `tags` обязательно'})
        if ('ingredients' not in validated_data) or (not validated_data
                                                     ['ingredients']):
            raise ValidationError(
                {'ingredients': 'Поле `ingredients` обязательно'})
        tags_data = validated_data.pop('tags', None)
        instance.tags.set(tags_data)
        ingredients_data = validated_data.pop('ingredients', None)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.add_ingredients(ingredients_data, instance)
        instance = super().update(instance, validated_data)
        instance.save()
        return instance

    def to_representation(self, recipe):
        serializer = RecipeGETSerializer(recipe)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавляли это рецепт в избранное'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('recipe', 'user'),
                message='Вы уже добавляли это рецепт в список покупок'
            )
        ]


class ShortenerSerializer(serializers.ModelSerializer):

    class Meta:
        model = LinkMapped
        fields = ('original_url',)
        write_only_fields = ('original_url',)

    def get_short_link(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(
            reverse('load_url', args=[obj.url_hash])
        )

    def create(self, validated_data):
        instance, _ = LinkMapped.objects.get_or_create(**validated_data)
        return instance

    def to_representation(self, instance):
        return {'short-link': self.get_short_link(instance)}
