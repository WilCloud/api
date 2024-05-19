from django.db import models


class StorageTypeChoices(models.TextChoices):
    LOCAL = 'local'
    ONEDRIVE = 'onedrive'


class Storage(models.Model):
    name = models.CharField(max_length=32)
    type = models.CharField(max_length=20, choices=StorageTypeChoices.choices)
    dir_name_rule = models.CharField(max_length=256)
    file_name_rule = models.CharField(max_length=256)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
