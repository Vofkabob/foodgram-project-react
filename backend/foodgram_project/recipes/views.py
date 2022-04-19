from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, generics

from .filters import RecipeFilterSet, CustomSearchFilter
from .models import (Tag, Ingredient, Recipe, IngredientForRecipe,
                     Favorite, ShoppingCart)
from .permissions import Author, ReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer,
                          ShoppingCartSerializer,
                          RecipeCreateSerializer,
                          IngredientListSerializer,
                          FavoriteSerializer)
from .mixins import ListRetriveViewSet


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=Favorite)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        final_list = {}
        ingredients_in_recipe = IngredientForRecipe.objects.filter(
            recipe__purchases__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount')
        for item in ingredients_in_recipe:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                final_list[name]['amount'] += item[2]
        pdfmetrics.registerFont(
            TTFont('FreeSans', 'media/fonts/FreeSans.ttf'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = Canvas(response)
        page.setFont('FreeSans', size=24)
        page.drawString(200, 800, 'Список ингредиентов')
        page.setFont('FreeSans', size=16)
        height = 750
        for i, (name, data) in enumerate(final_list.items(), start=1):
            page.drawString(75, height, (f'{i}) {name} - {data["amount"]} '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response

    def get_permissions(self):
        if self.action in ['shopping_cart', 'download_shopping_cart']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [Author | ReadOnly]
        return [permission() for permission in permission_classes]


class IngredientsViewSet(ListRetriveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [CustomSearchFilter, ]
    search_fields = ['^name']
    pagination_class = None


class IngredientsAmountView(generics.ListAPIView):
    queryset = IngredientForRecipe.objects.all()
    serializer_class = IngredientListSerializer


class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
