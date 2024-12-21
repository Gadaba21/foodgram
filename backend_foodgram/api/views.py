from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import (Favorite, Ingredient, IngredientRecipe, LinkMapped,
                           Recipe, ShoppingCart, Tag)
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from user.serializers import SubscriptionRecipeShortSerializer

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import AnonimReadOnly, IsSuperUserIsAdminIsAuthor
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGETSerializer, RecipeSerializer,
                          ShoppingCartSerializer, ShortenerSerializer,
                          TagSerializer)
from .utils import create_shopping_cart


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    permission_classes = (AnonimReadOnly | IsSuperUserIsAdminIsAuthor,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = RecipeFilter

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = SubscriptionRecipeShortSerializer(recipe)
            return Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED
            )
        favorite_recipe = Favorite.objects.filter(user=request.user,
                                                  recipe=recipe)
        if not favorite_recipe.exists():
            raise serializers.ValidationError(
                'нельзя удалить подписки которой нет'
            )
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user_cart': request.user.id, 'recipe_cart': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            shopping_cart_serializer = SubscriptionRecipeShortSerializer(
                recipe)
            return Response(
                shopping_cart_serializer.data, status=status.HTTP_201_CREATED
            )
        shopping_cart_recipe = ShoppingCart.objects.filter(
            user_cart=request.user.id,
            recipe_cart=recipe.id)
        if not shopping_cart_recipe.exists():
            raise serializers.ValidationError(
                'нельзя удалить подписки которой нет'
            )
        shopping_cart_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients_cart = (
            IngredientRecipe.objects.filter(
                recipe__shopping_cart__user_cart=user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).order_by(
                'ingredient__name'
            ).annotate(ingredient_value=Sum('amount'))
        )
        return create_shopping_cart(ingredients_cart)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk):
        self.get_object()
        original_url = request.META.get('HTTP_REFERER')
        if original_url is None:
            url = reverse('recipes-detail', kwargs={'pk': pk})
            original_url = request.build_absolute_uri(url)
        serializer = ShortenerSerializer(
            data={'original_url': original_url},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipeSerializer


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientSearchFilter
    filter_backends = (DjangoFilterBackend,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@require_GET
def load_url(request, url_hash: str):
    original_url = get_object_or_404(
        LinkMapped, url_hash=url_hash
    ).original_url
    return redirect(original_url)
