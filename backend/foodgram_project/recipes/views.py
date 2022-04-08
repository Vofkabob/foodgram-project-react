import itertools

from django.http.response import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, generics, views

from .filters import RecipeFilterSet, CustomSearchFilter
from .models import (Tag, Ingredient, Recipe, IngredientForRecipe,
                     Favourite, ShoppingCart)
from .permissions import Author, ReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer,
                          IngredientForRecipeSerializer,
                          RecipeFollowSerializer)
from .mixins import ListRetriveViewSet


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_shopping_cart(self, recipes):
        ingredients_dict = {}
        for recipe in recipes:
            ingredients = recipe.ingredients.all()
            for ingredient in ingredients:
                name = ingredient.name
                measurement_unit = ingredient.measurement_unit
                ingredients_amount = ingredient.ingredients_amount
                key = f'{name} ({measurement_unit})'
                if key not in ingredients_dict.keys():
                    ingredients_dict[key] = ingredients_amount
                else:
                    ingredients_dict[key] += ingredients_amount
        return ingredients_dict

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        user_recipes = Recipe.objects.filter(purchases__user=request.user)
        if not user_recipes:
            error = {'errors': 'Список рецептов пуст'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        ingredients = self.get_shopping_cart(user_recipes)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.pdf"')
        canvas = Canvas(response)
        pdfmetrics.registerFont(TTFont('FontPDF', 'FontPDF.otf'))
        canvas.setFont('FontPDF', 50)
        canvas.drawString(100, 750, 'Список покупок:')
        canvas.setFont('FontPDF', 30)
        counter = itertools.count(650, -50)
        for k, v in ingredients.items():
            if int(round(v, 2) % 1 * 100) == 0:
                v = int(v)
            height = next(counter)
            canvas.drawString(50, height, f'-  {k} - {v}')
        canvas.save()
        return response

    def get_permissions(self):
        if self.action in ['shopping_cart', 'download_shopping_cart']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [Author | ReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeSerializer
        return RecipeFollowSerializer


class IngredientsViewSet(ListRetriveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [CustomSearchFilter, ]
    search_fields = ['^name']
    pagination_class = None


class IngredientsAmountView(generics.ListAPIView):
    queryset = IngredientForRecipe.objects.all()
    serializer_class = IngredientForRecipeSerializer


class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class FavouriteShoppingCartView(views.APIView):
    permission_classes = [IsAuthenticated]
    queryset = {
        'favourite': Favourite.objects,
        'shopping_cart': ShoppingCart.objects
    }

    def post(self, request, recipe_id):
        name_url = request.resolver_match.url_name
        recipe = get_object_or_404(Recipe, id=recipe_id)
        double = self.queryset[name_url].filter(
            user=request.user,
            recipe=recipe
        ).exists()
        if double:
            error = {'errors': 'Рецепт уже добавлен'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.queryset[name_url].create(user=request.user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        name_url = request.resolver_match.url_name
        recipe = get_object_or_404(Recipe, id=recipe_id)
        try:
            obj = self.queryset[name_url].get(user=request.user, recipe=recipe)
        except ObjectDoesNotExist:
            error = {'errors': 'Рецепт не найден в списке'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
