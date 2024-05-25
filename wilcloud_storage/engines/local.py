from wilcloud_storage.models import Storage


def get_upload_url(file):
    return f'/upload/?file_id={file.id}'


def get_download_url(file):
    return f'/download/download/?file_id={file.id}'
