from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w-_]+\Z'
    flags = 0


class User(AbstractBaseUser, UserManager):
    username = models.CharField(max_length=32,
                                unique=True,
                                validators=[UsernameValidator])
    avatar = models.CharField(max_length=200,
                              default='',
                              null=True,
                              blank=True)
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    totp_secret = models.CharField(max_length=16, null=True, blank=True)
    preference = models.JSONField(default=dict)

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
