from django.conf import settings
from django.core.cache import cache
from django.http.response import FileResponse
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
import wilcloud.drf_mixins as mixins
from wilcloud.permissions import IsSuperUserOrReadOnly
from wilcloud_storage.models import Storage
from wilcloud_storage.engines import local
from wilcloud_storage.utils import update_source_name
from .models import File, Folder
from .serializers import FileSerializer, FolderSerializer, FileBriefSerializer, FolderBriefSerializer
from wilcloud.pagination import WilCloudPagination


class UploadViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['POST'], url_path='init')
    def upload_init(self, request):
        data = request.data
        user = request.user

        size = data['size']
        if size + user.used_space > user.group.space:
            return Response({'status': 'error'})

        storage = Storage.objects.get(id=data['storage_id'])
        if not user.group.storages.filter(id=storage.id).exists():
            return Response({'status': 'error'})

        parent = Folder.objects.get(id=data['parent_id'])
        if not parent.owner == user:
            return Response({'status': 'error'})

        file = File.objects.create(
            owner=request.user,
            name=data['name'],
            size=size,
            parent=parent,
            storage=storage,
        )
        update_source_name(file)
        file.save()

        upload_url = local.get_upload_url(file)

        return Response({
            'status': 'success',
            'data': {
                'file_id': file.id,
                'upload_url': upload_url,
            },
        })

    # For local storage only
    def create(self, request):
        file = File.objects.get(id=request.GET['file_id'])
        f = request.FILES['file']
        target_file = settings.UPLOAD_PATH / file.source
        try:
            target_file.resolve().relative_to(settings.UPLOAD_PATH.resolve())
        except:
            return Response({'status': 'error'})
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, 'wb+') as des:
            for chunk in f.chunks():
                des.write(chunk)
        return Response({'status': 'success'})


class DownloadViewSet(GenericViewSet):
    permission_classes = []

    @action(detail=False,
            methods=['GET'],
            url_path='download',
            permission_classes=[IsAuthenticated])
    def download(self, request):
        file = File.objects.get(id=request.GET['file_id'])
        user = request.user
        if file.owner != user:
            return Response({'status': 'error'})
        target_file = settings.UPLOAD_PATH / file.source
        try:
            target_file.resolve().relative_to(settings.UPLOAD_PATH.resolve())
        except:
            return Response({'status': 'error'})
        resp = FileResponse(open(target_file, 'rb'),
                            as_attachment=True,
                            filename=file.name)
        return resp


class FileViewSet(GenericViewSet, mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FileSerializer

    def get_queryset(self):
        return File.objects.filter(owner=self.request.user, deleted=False)

    def create(self, request):
        ...

    @action(detail=True, methods=['GET'], url_path='download')
    def download(self, request, pk=None):
        file = self.get_object()
        return Response({
            'status': 'success',
            'data': local.get_download_url(file),
        })


class FolderViewSet(GenericViewSet, mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FolderSerializer

    def get_queryset(self):
        return Folder.objects.filter(owner=self.request.user, deleted=False)

    def get_object(self):
        try:
            obj = super().get_object()
            if obj:
                return obj
        except AssertionError:
            ...

        request = self.request
        user = request.user
        if request.GET.get('path'):
            path = request.GET.get('path', '').strip('/').split('/')
            if path[0] != '':
                path = [''] + path
            q = self.get_queryset().filter(
                path=path[:-1],
                name=path[-1],
            )
            if not q.exists():
                return None
            return q.first()

    def list(self, request):
        # Retrieve folder by path
        folder = self.get_object()
        return Response({
            'status': 'success',
            'data': FolderSerializer(folder).data,
        })

    @action(detail=False, methods=['GET'], url_path='list')
    def list_children(self, request):
        folder = self.get_object()
        if folder is None:
            return Response({
                'status': 'error',
                'message': ['error.not_found'],
            })

        page = int(request.GET.get('page', 1))
        page_size = int(
            request.GET.get('page_size', WilCloudPagination.page_size))
        if page_size < 1 or page_size > WilCloudPagination.max_page_size:
            page_size = WilCloudPagination.page_size

        order_by = request.GET.get('order_by', '-id')

        child_folders = Folder.objects.filter(parent=folder,
                                              deleted=False).order_by(order_by)
        child_files = File.objects.filter(parent=folder,
                                          deleted=False).order_by(order_by)

        child_folder_cnt = child_folders.count()
        child_file_cnt = child_files.count()
        total_cnt = child_folder_cnt + child_file_cnt

        start = (page - 1) * page_size
        end = start + page_size

        if total_cnt != 0 and start >= total_cnt:
            return Response({
                'status': 'error',
                'message': ['error.not_found'],
            })

        if start >= child_folder_cnt:
            start -= child_folder_cnt
            end -= child_folder_cnt

            child_folders = []
            child_files = child_files[start:min(end, child_file_cnt)]
        elif end <= child_folder_cnt:
            child_folders = child_folders[start:end]
            child_files = []
        else:
            child_folders = child_folders[start:]
            child_files = child_files[:end - child_folder_cnt]

        folder_data = FolderBriefSerializer(child_folders, many=True).data
        file_data = FileBriefSerializer(child_files, many=True).data

        for i in folder_data:
            i['type'] = 'folder'

        for i in file_data:
            i['type'] = 'file'

        data = folder_data + file_data

        return Response({
            'status': 'success',
            'data': {
                'count': total_cnt,
                'results': data,
            },
        })

    def create(self, request):
        user = request.user
        parent = Folder.objects.get(id=request.data['parent_id'])
        if not parent.owner == user:
            return Response({'status': 'forbidden'})
        name = request.data['name']
        Folder.objects.create(owner=user,
                              parent=parent,
                              name=name,
                              path=parent.path + [parent.name],
                              parents=parent.parents + [parent.id])
        return Response({'status': 'success'})
