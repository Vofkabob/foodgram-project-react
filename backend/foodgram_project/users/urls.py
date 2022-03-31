from django.urls import include, path
from rest_framework.routers import DefaultRouter
#from rest_framework.authtoken import views 

from .views import MyUserViewSet

router = DefaultRouter()
router.register('users', MyUserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    #path('auth/', views.obtain_auth_token)
    #path('/auth/', include('djoser.urls.authtoken'))
    #path('/auth/', include('djoser.urls.jwt'))
]
