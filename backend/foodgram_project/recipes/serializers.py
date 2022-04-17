from django.db.models import F
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from .models import (Tag, Ingredient, Recipe, IngredientForRecipe,
                     Favourite, ShoppingCart)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientForRecipeSerializer(
        many=True, source='ingredients_amount')
    image = Base64ImageField(max_length=None, use_url=True)
    author = CustomUserSerializer(read_only=True)
    name = serializers.CharField(required=False)
    text = serializers.CharField(required=False)

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if ingredients == []:
            raise serializers.ValidationError('Выберите хотя бы 1 ингредиент.')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError('Количество не может быть'
                                                  'меньше 1.')
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError('Время приготовления не может'
                                              ' быть меньше минуты.')
        return data

    def create(self, validated_data):
        validated_data.pop('ingredients_amount')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        ingredients_amount = self.get_ingredients_list(
            self.initial_data['ingredients'], recipe)
        recipe.tags.set(tags)
        recipe.ingredients_amount.set(ingredients_amount)
        recipe.save()
        return recipe

    def update(self, recipe, validated_data):
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.image = validated_data.get('image', recipe.image)
        recipe.cooking_time = validated_data.get('cooking_time',
                                                 recipe.cooking_time)
        if 'tags' in self.initial_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
            recipe.save()
        if 'ingredient' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            ingredients = self.get_ingredients_list(ingredients, recipe)
        recipe.save()
        return recipe

    def get_ingredients_list(self, ingredients, recipe_id):
        ingredients_list = []
        ingredients_to_delete = IngredientForRecipe.objects.filter(
            recipe=recipe_id)
        if ingredients_to_delete:
            for ingredient in ingredients_to_delete:
                ingredient.delete()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            ingredient_instance = Ingredient.objects.get(id=ingredient_id)
            if (IngredientForRecipe.objects.
               filter(recipe=recipe_id, ingredient_id=ingredient_id).exists()):
                amount += F('amount')
            ingredient, updated = IngredientForRecipe.objects.update_or_create(
                recipe=recipe_id, ingredient=ingredient_instance,
                defaults={'amount': amount})
            ingredients_list.append(ingredient)
        return ingredients_list

    class Meta:
        model = Recipe
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe_id.name')
    image = Base64ImageField(max_length=None, use_url=True)
    cooking_time = serializers.ReadOnlyField(source='recipe_id.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeFollowSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientForRecipeSerializer(
        source='ingredients_amount', many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favourite.objects.filter(
            recipe_id=obj, user_id=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe_id=obj,
                                           user_id=request.user).exists()

    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'
