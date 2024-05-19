from django.core import validators
from django.db import models
from django.utils.deconstruct import deconstructible

from wilcloud_user.models import User
from wilcloud_storage.models import Storage


@deconstructible
class FileNameValidator(validators.BaseValidator):
    sets = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

    def __call__(self, value):
        for c in self.sets:
            if c in value:
                raise validators.ValidationError


class Folder(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    path = models.JSONField()
    parents = models.JSONField()
    parent = models.ForeignKey('self',
                               on_delete=models.PROTECT,
                               related_name='child_folders',
                               null=True)
    name = models.CharField(max_length=128, validators=[FileNameValidator])

    create_time = models.DateTimeField(auto_now_add=True)

    deleted = models.BooleanField(default=False)


class FolderShare(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shared_folders')
    folder = models.ForeignKey(Folder,
                               on_delete=models.CASCADE,
                               related_name='shared_users')
    read_only = models.BooleanField()


class File(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    parent = models.ForeignKey(Folder,
                               on_delete=models.PROTECT,
                               related_name='files')
    name = models.CharField(max_length=128, validators=[FileNameValidator])
    size = models.BigIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    uploaded = models.BooleanField(default=False)

    storage = models.ForeignKey(Storage, on_delete=models.PROTECT)
    source = models.CharField(max_length=4096)

    deleted = models.BooleanField(default=False)
