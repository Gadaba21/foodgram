from django.contrib import admin
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    load_url
)
from user.views import UserViewSet


router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('users', UserViewSet, basename='users')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router_v1.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('s/<str:url_hash>/', load_url, name='load_url'),
]
