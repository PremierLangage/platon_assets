import os
import tarfile
import tempfile
import time
import uuid
from typing import AnyStr

from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.http import HttpRequest

from django_sandbox.models import Sandbox


# The PL data will always be passed in the pl.json file, and the context
# must be generated in the file named in result_path
DEFAULT_BUILDER = {
    "commands":    ["python3 builder.py pl.json context.json"],
    "result_path": "context.json",
}

# The grader.py file must output a "feedback" and "grade" fields to the
# context.json file. if the config is custom, the file in result_path
# must contain those fields.
DEFAULT_GRADER = {
    "commands":    ["python3 grader.py pl.json answer.json context.json"],
    "result_path": "context.json",
}



def create_seed() -> int:
    """Creates a seed between 0 and 99"""
    return int(time.time() % 100)



@database_sync_to_async
def async_get_less_used_sandbox() -> Sandbox:
    """Returns the less used sandbox, based on its current usage, for
    async functions"""
    # TODO  do as the doctest says
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
    """Returns a uuid4 as str for an anonymous user. If the user is not yet
    identified, creates its id."""
    if "user_id" not in request.session:
        request.session["user_id"] = str(uuid.uuid4())
    return request.session["user_id"]



@database_sync_to_async
def async_is_user_authenticated(user: User) -> bool:
    """Returns if the user is authenticated for async functions"""
    return user.is_authenticated
