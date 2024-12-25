from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import User


@admin.register(User)
class UsersAdmin(UserAdmin):
    """Админка для пользователя"""

    list_display = ('id', 'username', 'email', 'role', 'subscribers_count',
                    'recipes_count')
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по `username` и `email`'
    list_display_links = ('id', 'username', 'email')

    @admin.display(description='Подписчики')
    def subscribers_count(self, obj):
        return obj.following.count()

    @admin.display(description='Рецепты')
    def recipes_count(self, obj):
        return obj.recipes.count()


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)