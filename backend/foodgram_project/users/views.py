from django.contrib.auth import get_user_model
from django.db.models import Count
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


from .models import Follow
from .serializers import FollowSerializer

User = get_user_model()


class MyUserViewSet(UserViewSet):

    @action(detail=False, methods=('GET',))
    def follower(self, request):
        user = self.request.user
        following = user.following.all().values_list(
            'following_id', flat=True)
        queryset = User.objects.filter(id__in=following).annotate(
            count=Count('recipes__id'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=('GET',))
    def follow(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user.id == id:
            raise ValidationError('Нельзя подписаться на себя')
        if int(id) in user.following.all().values_list(
                'following', flat=True):
            raise ValidationError('Вы уже подписаны на этого автора')
        else:
            follow = Follow.objects.create(
                follower=user,
                following=author
            )
            follow.save()
            serializer = FollowSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @follow.mapping.delete
    def delete_follow(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        follow = get_object_or_404(
            Follow,
            follower=user,
            following=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'follower':
            user = self.request.user
            following = user.following.all().values_list(
                'following_id', flat=True)
            queryset = User.objects.filter(id__in=following).annotate(
                count=Count('recipes__id'))
            return queryset
        return queryset
