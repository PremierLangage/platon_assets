import os
import tarfile
import tempfile
import time
import uuid
from typing import AnyStr

from channels.db import database_sync_to_async
from django.db import models
from django.http import HttpRequest

from django_sandbox.models import Sandbox


DEFAULT_BUILDER = {
    "commands":    ["python3 builder.py pl.json context.json"],
    "result_path": "context.json",
}

DEFAULT_GRADER = {
    "commands":    ["python3 grader.py pl.json context.json"],
    "result_path": "context.json",
}



def create_seed() -> int:
    return int(time.time() % 100)



@database_sync_to_async
def async_get_less_used_sandbox() -> Sandbox:
    """Returns the less used sandbox, base on its current usage"""
    # TODO
    return Sandbox.objects.all()[0]



def tar_from_dic(files: dict) -> AnyStr:
    """Returns binaries of a tar gz file with the given file dictionnary
    Each entry of files is: "file_name": "file_content"
    """
    with tempfile.TemporaryDirectory() as tmp_dir, tempfile.TemporaryDirectory() as env_dir:
        with tarfile.open(tmp_dir + "/environment.tgz", "w:gz") as tar:
            for key in files:
                with open(os.path.join(env_dir, key), "w") as f:
                    print(files[key], file=f)
            
            tar.add(env_dir, arcname=os.path.sep)
        
        with open(tmp_dir + "/environment.tgz", 'rb') as tar:
            tar_stream = tar.read()
    
    return tar_stream



def get_anonymous_user_id(request: HttpRequest) -> str:
    if "user_id" not in request.session:
        request.session["user_id"] = str(uuid.uuid4())
    return request.session["user_id"]



@database_sync_to_async
def async_is_user_authenticated(user):
    return user.is_authenticated
