import io

from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins, generics
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets

from .filters import RecipeFilterSet, CustomSearchFilter
from .models import (Recipe, Tag, Ingredient, Favourite,
                     ShoppingList, IngredientForRecipe)
from .permissions import Author, ReadOnly
from .serializers import (RecipeSerializer, TagSerializer, 
                          IngredientListSerializer, RecipeFollowSerializer,
                          ShoppingListSerializer, IngredientSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['GET'])
    def shopping_list(self, request, pk=None):
        in_purchases = ShoppingList.objects.filter(
            recipe_id=int(pk),
            user_id=request.user
        )
        if in_purchases.exists():
            raise ValidationError('Рецепт уже добавлен в корзину')
        recipe = Recipe.objects.get(id=int(pk))
        purchases = ShoppingList.objects.create(
            recipe_id=recipe,
            user_id=self.request.user
        )
        purchases.save()
        serializer = ShoppingListSerializer(purchases)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @shopping_list.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        in_purchases = get_object_or_404(
            ShoppingList,
            recipe_id=int(pk),
        user_id=self.request.user)
        in_purchases.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def favourite(self, request, pk=None):
        user = request.user
        in_favourites = Favourite.objects.filter(
            user_id=user.id,
            recipe_id=pk)
        if in_favourites:
            raise ValidationError(
                detail='Рецепт уже находится в избранном')
        recipe = get_object_or_404(Recipe, id=int(pk))
        favourite = Favourite.objects.create(
            user_id=user,
            recipe_id=recipe)
        favourite.save()
        serializer = RecipeFollowSerializer(recipe)
        return Response(serializer.data)

    @favourite.mapping.delete
    def delete_favourite(self, request, pk=None):
        user = self.request.user
        in_favourites = get_object_or_404(
            Favourite,
            user_id=user.id,
            recipe_id=pk
        )
        in_favourites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_list(self, request):
        queryset = ShoppingList.objects.filter(
            user_id=self.request.user).values(
            'recipe_id__ingredients_amount__ingredient__name',
            'recipe_id__ingredients_amount__ingredient__measurement_unit').annotate(
                Sum('recipe_id__ingredients_amount__amount'))
        buffer = get_pdf_file(queryset)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

    def get_permissions(self):
        if self.action in ['shopping_list', 'favourite',
                           'download_shopping_list']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [Author | ReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeSerializer
        return RecipeFollowSerializer


class IngredientsViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [CustomSearchFilter, ]
    search_fields = ['^name']
    pagination_class = None


class IngredientsAmountView(generics.ListAPIView):
    queryset = IngredientForRecipe.objects.all()
    serializer_class = IngredientListSerializer


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


def get_pdf_file(queryset):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setLineWidth(.3)
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    p.setFont('FreeSans', 14)
    t = p.beginText(30, 750, direction=0)
    t.textLine('Список покупок')
    p.line(30, 747, 580, 747)
    t.textLine(' ')
    for qs in queryset:
        title = qs['recipe_id__ingredients_amount__ingredient__name']
        amount = qs['recipe_id__ingredients_amount__amount__sum']
        mu = qs['recipe_id__ingredients_amount__ingredient__unit_of_measurement']
        t.textLine(f'{title} ({mu}) - {amount}')
    p.drawText(t)
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
