from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, TagViewSet,
                    FavouriteShoppingCartView)

router = DefaultRouter()
router.register('tags', TagViewSet, 'Tag')
router.register('recipes', RecipeViewSet, 'recipe')
router.register('ingredients', IngredientsViewSet, 'ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'recipes/<recipe_id>/shopping_cart/',
        FavouriteShoppingCartView.as_view(),
        name='shopping_cart'
    ),
    path(
        'recipes/<recipe_id>/favourite/',
        FavouriteShoppingCartView.as_view(),
        name='favourite'
    ),
]
