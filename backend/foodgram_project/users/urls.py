from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import MyUserViewSet, FollowView

router = DefaultRouter()
router.register('users', MyUserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path(
        'users/<user_id>/subscribe/',
        FollowView.as_view(),
        name='subscriptions'
    ),
]
