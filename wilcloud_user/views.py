import random
import string

from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth import login, logout
from pyotp import TOTP
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
import wilcloud.drf_mixins as mixins
from .models import User, Apikey
from .serializers import UserSerializer, UserDetailSerializer, ApikeySerializer


def random_string(length=4):
    return ''.join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(length))


def random_number(length=6):
    return ''.join(random.choice(string.digits) for _ in range(length))


class UserViewSet(GenericViewSet, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    @action(url_path='login',
            methods=['POST'],
            detail=False,
            authentication_classes=[])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username)
        if not user.exists():
            user = User.objects.filter(email=username)
        if not user.exists():
            return Response({
                'status': 'forbidden',
                'message': 'user.not_found'
            })
        user = user.first()
        if not user.is_active:
            return Response({
                'status': 'forbidden',
                'message': 'user.not_active'
            })

        flag = False
        if user.check_password(password):
            flag = True
        if not flag:
            return Response({
                'status': 'forbidden',
                'message': 'user.wrong_password'
            })

        login(request, user)

        user.last_login = timezone.now()
        user.save()

        return Response({
            'status': 'success',
            'message': 'user.login_success',
            'data': UserDetailSerializer(user).data,
        })

    @action(url_path='logout', methods=['POST'], detail=False)
    def logout(self, request):
        logout(request)
        return Response({'status': 'success', 'message': 'user.logout_success'})

    @action(url_path='register',
            methods=['POST'],
            detail=False,
            authentication_classes=[])
    def register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if User.objects.filter(username=username).exists():
            return Response({
                'status': 'forbidden',
                'message': 'user.username_in_use'
            })
        elif User.objects.filter(email=email).exists():
            return Response({
                'status': 'forbidden',
                'message': 'user.email_in_use'
            })

        user = User.create_user(username=username,
                                password=password,
                                email=email)

        login(request, user)

        return Response({
            'status': 'success',
            'message': 'user.register_success',
        })

    @action(url_path='info', methods=['GET', 'PUT'], detail=False)
    def info(self, request):
        user = request.user

        if request.method == 'PUT':
            if not user.is_authenticated:
                return Response({
                    'status': 'forbidden',
                    'message': 'user.not_authenticated'
                })
            if request.data.get('new_password'):
                old_password = request.data.get('old_password')
                if not user.check_password(old_password):
                    return Response({
                        'status': 'forbidden',
                        'message': 'user.wrong_password'
                    })
                user.set_password(request.data['new_password'])
            serializer = UserDetailSerializer(user,
                                              data=request.data,
                                              partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = serializer.data

        elif user.is_authenticated:
            data = UserDetailSerializer(user)

        else:
            data = None

        return Response({'status': 'success', 'data': data})


class ApikeyViewSet(GenericViewSet, mixins.ListModelMixin):
    serializer_class = ApikeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Apikey.objects.filter(user=self.request.user).order_by('id')

    def create(self, request, *args, **kwargs):
        serializer = ApikeySerializer(
            data=request.data.update({'token': random_string(32)}))
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({
            'status': 'success',
            'data': serializer.data,
        })
