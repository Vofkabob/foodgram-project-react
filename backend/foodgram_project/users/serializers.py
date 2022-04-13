from drf_extra_fields.fields import Base64ImageField
from djoser.conf import settings
from djoser.serializers import (
    UserCreateSerializer as BaseUserRegistrationSerializer)
from rest_framework import serializers, validators

from recipes.models import Recipe
from .models import Follow, User


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )])

    class Meta:
        model = User
        fields = (settings.LOGIN_FIELD, 'id',
                  'username', 'first_name', 'last_name', 'is_subscribed')
        read_only_fields = (settings.LOGIN_FIELD, )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes',
                            'recipes_count')

    def get_is_subscribed(self, subscribe):
        user = self.context['request'].user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=user,
                subscribe=subscribe
            ).exists()
        return False

    def get_recipes_count(self, subscribe):
        return subscribe.recipes.count()


class FollowListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(
            user=user,
            subscriptions=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()
