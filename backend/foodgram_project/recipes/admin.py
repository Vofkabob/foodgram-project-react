from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, IngredientForRecipe,
                     Favorite, ShoppingCart)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    fields = ['name', 'color', 'slug']


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ['name']


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientForRecipe


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        IngredientRecipeInline,
    ]
    list_display = ('id', 'name', 'author', 'get_ingredients')
    list_filter = ('name', 'author', 'tags')

    def get_ingredients(self, obj):
        return '\n'.join(
            [str(ingredients) for ingredients in obj.ingredients.all()])


class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    fields = ['ingredient', 'recipe', 'amount']


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientForRecipe, IngredientForRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
