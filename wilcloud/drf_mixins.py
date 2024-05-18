from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import CreateModelMixin as _CreateModelMixin, ListModelMixin as _ListModelMixin, RetrieveModelMixin as _RetrieveModelMixin, UpdateModelMixin as _UpdateModelMixin


def add_status(response, status='success'):
    response.data = {'status': status, 'data': response.data}
    return response


class CreateModelMixin(_CreateModelMixin):

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return add_status(response)


class ListModelMixin(_ListModelMixin):

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return add_status(response)


class RetrieveModelMixin(_RetrieveModelMixin):

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return add_status(response)


class UpdateModelMixin(_UpdateModelMixin):

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return add_status(response)
