from django.db.models import F
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from .models import (Tag, Ingredient, Recipe, IngredientForRecipe,
                     Favorite, ShoppingCart)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientListSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField()


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientListSerializer(
        many=True, source='ingredients_amount')
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
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


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = IngredientListSerializer(
        many=True, source='ingredients_amount')
    name = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    author = CustomUserSerializer(read_only=True)

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

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        ingredients_data = validated_data.pop('ingredients_amount', None)
        tags_data = validated_data.pop('tags', None)
        if tags_data:
            instance.tags.set(tags_data)
        if ingredients_data:
            ingred = self.initial_data['ingredients']
            ingredients = self.get_ingredients_list(
                ingred,
                instance)
            instance.ingredients_amount.set(ingredients)
        instance.save()
        return instance

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


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe, context=context).data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'status': 'Рецепт уже есть в избранном!'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe, context=context).data
