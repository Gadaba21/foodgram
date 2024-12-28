from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipe.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    LinkMapped,
    Recipe,
    ShoppingCart,
    Tag
)

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import AnonimReadOnly, IsSuperUserIsAdminIsAuthor
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeGETSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    ShortenerSerializer,
    TagSerializer
)
from .utils import (
    create_shopping_cart,
    handle_delete_favorite_or_cart,
    handle_post_favorite_or_cart
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = (AllowAny,)
        else:
            permission_classes = (AnonimReadOnly | IsSuperUserIsAdminIsAuthor,
                                  IsAuthenticated)
        return [permission() for permission in permission_classes]

    @action(
        detail=True,
        methods=('post',),
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        return handle_post_favorite_or_cart(request, pk, FavoriteSerializer)

    @get_favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return handle_delete_favorite_or_cart(request, pk, Favorite)

    @action(
        detail=True,
        methods=('post',),
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        return handle_post_favorite_or_cart(request, pk,
                                            ShoppingCartSerializer)

    @get_shopping_cart.mapping.delete
    def delete_hopping_cart(self, request, pk):
        return handle_delete_favorite_or_cart(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients_cart = (
            IngredientRecipe.objects.filter(
                recipe__shopping_cart__user=user
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
        methods=('get',),
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk):
        original_url = request.META.get('HTTP_REFERER')
        if original_url:
            url = reverse('api:recipes-detail', kwargs={'pk': pk})
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


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientSearchFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


@require_GET
def load_url(request, url_hash: str):
    original_url = get_object_or_404(
        LinkMapped, url_hash=url_hash
    ).original_url
    return redirect(original_url)
