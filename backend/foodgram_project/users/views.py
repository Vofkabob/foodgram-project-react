from django.contrib.auth import get_user_model
from django.db.models import Count
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, views
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from django.shortcuts import get_list_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .paginator import LimitPageNumberPagination
from recipes.mixins import ListViewSet
from .models import Follow
from .serializers import FollowSerializer

User = get_user_model()


class MyUserViewSet(UserViewSet):

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

    @action(detail=False, methods=('GET',),
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        author_users = User.objects.filter(following__user=request.user)
        serializer = self.get_serializer(author_users, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class FollowView(views.APIView):
    pagination_class = LimitPageNumberPagination
    permission_classes = [IsAuthenticated]

    @action(detail=True, permission_classes=[IsAuthenticated])
    def post(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        if user == author:
            error = {'errors': 'Невозможно подписаться на самого себя'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        elif Follow.objects.filter(user=user, author=author).exists():
            error = {'errors': 'Вы уже подписаны на этого пользователя'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            follow,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @post.mapping.delete
    def delete(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        if user == author:
            error = {'errors': 'Вы не можете отписываться от самого себя'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        error = {'errors': 'Вы уже отписались'}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class FollowListView(ListViewSet):
    serializer = FollowSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [IsAuthenticated]
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        return get_list_or_404(User, following__user=self.request.user)
