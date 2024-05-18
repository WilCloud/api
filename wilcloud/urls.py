from django.urls import path, include

urlpatterns = [
    path('user/', include('wilcloud_user.urls')),
]
