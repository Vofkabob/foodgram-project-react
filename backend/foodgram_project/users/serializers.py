from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from .models import Follow
from rest_framework import serializers


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()

    class Meta:
        model = User
        fields = (settings.LOGIN_FIELD,
                  'email', 'first_name', 'last_name', 'is_subscribed')
        read_only_fields = (settings.LOGIN_FIELD, )


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            'first_name',
            'last_name',
            "password",
        )


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    recipes = RecipeSerializer(many=True)
    is_subscribed = serializers.SerializerMethodField()
    count = serializers.IntegerField(read_only=True)

    def get_follower(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()

    class Meta:
        model = Follow
        fields = ('username', 'id',  'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'count')
