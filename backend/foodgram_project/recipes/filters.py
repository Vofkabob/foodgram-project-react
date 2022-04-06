from django.contrib.auth import get_user_model
from django_filters import FilterSet, filters
from rest_framework.filters import SearchFilter

from .models import Recipe, Tag

User = get_user_model()


class RecipeFilterSet(FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug')
    is_favourited = filters.BooleanFilter(
        label="Favourited",
        method='filter_is_favourite')
    is_in_shopping_list = filters.BooleanFilter(
        label="Is in shopping list",
        method='filter_is_in_shopping_list')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favourited', 'is_in_shopping_list']

    def filter_is_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user_id=self.request.user)
        return queryset.all()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(purchases__user_id=self.request.user)
        return queryset.all()


class CustomSearchFilter(SearchFilter):
    search_param = "name"
