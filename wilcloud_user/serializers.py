from rest_framework import serializers
from .models import User, Apikey


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = read_only_fields = ['id', 'username', 'avatar']


class UserDetailSerializer(serializers.ModelSerializer):
    totp = serializers.BooleanField(source='totp_secret', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'avatar', 'preference', 'is_superuser', 'totp'
        ]
        read_only_fields = ['id', 'username', 'is_superuser', 'totp']


class ApikeySerializer(serializers.ModelSerializer):

    class Meta:
        model = Apikey
        fields = ['id', 'token', 'secret', 'expire_time', 'permissions']
