import random
import string

from django.core.cache import cache
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
import wilcloud.drf_mixins as mixins
from wilcloud.permissions import IsSuperUserOrReadOnly
from .models import Storage, StorageTypeChoices


class StorageViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Storage.objects.all()
