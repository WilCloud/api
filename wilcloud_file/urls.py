from django.urls import path, include
from rest_framework.routers import DefaultRouter

from wilcloud_file import views

router = DefaultRouter()
router.register(r'upload', views.UploadViewSet, basename='upload')
router.register(r'folder', views.FolderViewSet, basename='folder')
# router.register(r'', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
