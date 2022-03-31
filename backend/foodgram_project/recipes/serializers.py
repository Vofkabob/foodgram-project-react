from django.db.models import F
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from .models import (Recipe, Tag, Ingredient, IngredientForRecipe,
                     Favourite, ShoppingList)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    recipe = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientForRecipeSerializer(
        source='ingredients_amount', many=True)
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
                raise serializers.ValidationError('Количество не может быть меньше 1.')
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError('Время приготовления не может'
                                  ' быть меньше минуты.')
        return data

    def create(self, validated_data):
        validated_data.pop('ingredients_amount')
        recipe= super().create(validated_data)
        tags = validated_data.pop('tags')
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
        ingredients_data = validated_data.pop('ingredients_amount')
        tags_data = validated_data.pop('tags')
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

    def get_ingredients_list(self, ingredients, recipe):
        ingredients_list = []
        ingredients_to_delete = IngredientForRecipe.objects.filter(
            recipe_id=recipe)
        if ingredients_to_delete:
            for ingredient in ingredients_to_delete:
                ingredient.delete()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            ingred_instance = Ingredient.objects.get(id=ingredient_id)
            if IngredientForRecipe.objects.\
               filter(recipe_id=recipe, ingred_id=ingredient_id).exists():
                amount += F('amount')
            ingred, updated = IngredientForRecipe.objects.update_or_create(
                recipe_id=recipe, ingred=ingred_instance,
                defaults={'amount': amount})
            ingredients_list.append(ingred)
        return ingredients_list

    class Meta:
        model = Recipe
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe_id.name')
    image = Base64ImageField(max_length=None, use_url=True)
    cooking_time = serializers.ReadOnlyField(source='recipe_id.cooking_time')

    class Meta:
        model = ShoppingList
        fields = '__all__'

class RecipeFollowSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientForRecipeSerializer(
        source='ingredients_amount', many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_list = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favourite.objects.filter(
            recipe_id=obj, user_id=request.user).exists()

    def get_is_in_shopping_list(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(recipe_id=obj,
                                           user_id=request.user).exists()

    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'

class IngredientListSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    unit_of_measurement = serializers.CharField(
        source='ingredient.unit_of_measurement', read_only=True)
    amount = serializers.IntegerField()
