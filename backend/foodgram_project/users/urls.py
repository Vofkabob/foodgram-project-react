from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import MyUserViewSet, FollowView, FollowListView

router = DefaultRouter()
router.register('users', MyUserViewSet, 'users')

urlpatterns = [
    path(
        'users/<user_id>/subscribe/',
        FollowView.as_view(),
        name='subscribe'),
    path('users/subscriptions/',
         FollowListView.as_view({'get': 'list'}),
         name='subscriptions'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
