import django, os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wilcloud.settings')
django.setup()

from wilcloud_storage.models import Storage, StorageTypeChoices
from wilcloud_user.models import UserGroup, User

if not Storage.objects.exists():
    storage = Storage.objects.create(id=1,
                                     name='Local Storage',
                                     type=StorageTypeChoices.LOCAL,
                                     dir_name_rule='{username}/{file_path}',
                                     file_name_rule='{file_name}')
else:
    storage = Storage.objects.order_by('id').first()

if not UserGroup.objects.exists():
    group = UserGroup.objects.create(name='Default Group',
                                     space=1024 * 1024 * 1024)
    group.storages.add(storage)
    group.save()
else:
    group = UserGroup.objects.order_by('id').first()

if not User.objects.exists():
    user = User.objects.create(username='admin',
                               is_superuser=True,
                               email='admin@wilcloud.org',
                               group=group)
    user.set_password('admin')
    user.save()
