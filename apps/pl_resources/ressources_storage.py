import os
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile


class RessourceStorage(FileSystemStorage):

    @staticmethod
    def update(file, content):
        with file.open("w+") as f:
            f.write(content)
