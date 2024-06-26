from rest_framework import serializers
from .models import File, Folder


class FolderBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Folder
        fields = read_only_fields = ['id', 'name', 'create_time']


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
        read_only_fields = [
            'id', 'create_time', 'update_time', 'size', 'uploaded', 'parent'
        ]


class FolderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Folder
        fields = ['id', 'name', 'create_time', 'path', 'parents']
        read_only_fields = ['id', 'create_time', 'path', 'parents']
