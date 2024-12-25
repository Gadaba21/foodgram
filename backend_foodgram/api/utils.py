import io
from pathlib import Path

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipe.models import Recipe
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import serializers, status
from rest_framework.response import Response

from user.serializers import SubscriptionRecipeShortSerializer


def create_shopping_cart(ingredients_cart):
    """Функция для формирования списка покупок."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        "attachment; filename='shopping_cart.pdf'"
    )
    font_file = Path(__file__).resolve().parent / 'data' / 'arial.ttf'
    pdfmetrics.registerFont(
        TTFont('Arial', font_file, 'UTF-8')
    )
    buffer = io.BytesIO()
    pdf_file = canvas.Canvas(buffer)
    pdf_file.setFont('Arial', 20)
    pdf_file.drawString(200, 800, 'Список покупок.')
    pdf_file.setFont('Arial', 14)
    from_bottom = 750
    for number, ingredient in enumerate(ingredients_cart, start=1):
        pdf_file.drawString(
            50,
            from_bottom,
            f"{number}. {ingredient['ingredient__name']}: "
            f"{ingredient['ingredient_value']} "
            f"{ingredient['ingredient__measurement_unit']}.",
        )
        from_bottom -= 20
        if from_bottom <= 50:
            from_bottom = 800
            pdf_file.showPage()
            pdf_file.setFont('Arial', 14)
    pdf_file.showPage()
    pdf_file.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def handle_post_favorite_or_cart(request, pk, model):
    """Функция для POST запросов фаворит шопин карт."""
    recipe = get_object_or_404(Recipe, pk=pk)
    serializer = model(
        data={'user': request.user.id, 'recipe': recipe.id},
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    recipe_serializer = SubscriptionRecipeShortSerializer(recipe)
    return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)


def handle_delete_favorite_or_cart(request, pk, model):
    """Функция для Delete запросов фаворит шопин карт."""
    recipe = get_object_or_404(Recipe, pk=pk)
    shopping_cart_recipe = model.objects.filter(
        user=request.user.id,
        recipe=recipe.id)
    if not shopping_cart_recipe.exists():
        raise serializers.ValidationError(
            'нельзя удалить подписки которой нет'
        )
    shopping_cart_recipe.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
