from rest_framework import serializers
from .models import File, Folder


class FolderBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Folder
        fields = read_only_fields = ['id', 'name', 'path', 'parents']


class FileBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ['id', 'name', 'size', 'create_time', 'update_time']


class FileSerializer(serializers.ModelSerializer):
    parent = FolderBriefSerializer()

    class Meta:
        model = File
        fields = [
            'id', 'name', 'create_time', 'update_time', 'size', 'uploaded',
            'parent'
        ]


class FolderSerializer(serializers.ModelSerializer):
    files = FileBriefSerializer(many=True)

    class Meta:
        model = Folder
        fields = read_only_fields = ['id', 'name', 'path', 'parents', 'files']
