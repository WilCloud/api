from django.urls import path, include

from django.urls import path, include
from rest_framework.routers import DefaultRouter

import wilcloud_user.views
import wilcloud_file.views

router = DefaultRouter()
router.register(r'user', wilcloud_user.views.UserViewSet, basename='user')
router.register(r'apikey',
                wilcloud_user.views.ApikeyViewSet,
                basename='apikey')
router.register(r'folder',
                wilcloud_file.views.FolderViewSet,
                basename='folder')
router.register(r'file', wilcloud_file.views.FileViewSet, basename='file')
router.register(r'upload',
                wilcloud_file.views.UploadViewSet,
                basename='upload')
router.register(r'download',
                wilcloud_file.views.DownloadViewSet,
                basename='download')

urlpatterns = [
    path('', include(router.urls)),
]
