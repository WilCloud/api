from django.urls import path, include
from rest_framework.routers import DefaultRouter

from wilcloud_user import views

router = DefaultRouter()
router.register(r'apikey', views.ApikeyViewSet, basename='apikey')
router.register(r'', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
