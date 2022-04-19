from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, FollowListView, FollowViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet, 'users')

urlpatterns = [
    path(
        'users/subscriptions/',
        FollowListView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        FollowViewSet.as_view(),
        name='subscribe'
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
