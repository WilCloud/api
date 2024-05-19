from wilcloud_storage.models import Storage


def get_upload_url(file):
    return f'/file/upload/upload/?file_id={file.id}'
