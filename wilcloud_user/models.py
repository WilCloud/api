from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible

from wilcloud_storage.models import Storage


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w-_]+\Z'
    flags = 0


class UserGroup(models.Model):
    name = models.CharField(max_length=32, unique=True)
    space = models.BigIntegerField()

    storages = models.ManyToManyField(Storage)

    allow_source_link = models.BooleanField(default=True)
    allow_share = models.BooleanField(default=True)
    allow_api = models.BooleanField(default=True)


class User(AbstractBaseUser, UserManager):
    username = models.CharField(max_length=32,
                                unique=True,
                                validators=[UsernameValidator])
    avatar = models.CharField(max_length=200,
                              default='',
                              null=True,
                              blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    totp_secret = models.CharField(max_length=16, null=True, blank=True)
    preference = models.JSONField(default=dict)
    group = models.ForeignKey(UserGroup,
                              on_delete=models.PROTECT,
                              related_name='users')
    used_space = models.BigIntegerField(default=0)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class Apikey(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="apikeys")
    token = models.CharField(max_length=32, unique=True)
    expire_time = models.DateTimeField(null=True, blank=True)
    permissions = models.JSONField(default=list)
