from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from djoser.views import UserViewSet
from rest_framework import status, views
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


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
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        following_user = get_object_or_404(User, id=user_id)
        double_subscribe = Follow.objects.filter(
            user=request.user,
            author=following_user
        ).exists()
        if request.user.id == int(user_id):
            error = {'errors': 'Невозможно подписаться на самого себя'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        elif double_subscribe:
            error = {'errors': 'Вы уже подписаны на этого пользователя'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(
            user=request.user,
            author=following_user
        )
        serializer = FollowSerializer(
            following_user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        following_user = get_object_or_404(User, id=user_id)
        try:
            author = Follow.objects.get(
                user=request.user,
                author=following_user
            )
        except ObjectDoesNotExist:
            error = {'errors': 'Вы не подписаны на этого пользователя'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        author.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
