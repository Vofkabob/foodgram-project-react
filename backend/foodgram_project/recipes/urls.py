from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientsViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, 'Tag')
router.register('recipes', RecipeViewSet, 'recipe')
router.register('ingredients', IngredientsViewSet, 'ingredients')
urlpatterns = [
    path('', include(router.urls)),
]
