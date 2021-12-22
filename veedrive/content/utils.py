import hashlib
import os
import string
from functools import wraps
from pathlib import Path

from .. import config
from ..utils.exceptions import WrongObjectType


def sanitize_path(func):
    """Sanitize a path passed to a function."""

    @wraps(func)
    def validate(*args):
        path = fix_root_slash(args[0])
        return func(path, *args[1:])

    return validate


def fix_root_slash(path):
    """Transform '/' path into SANDBOX_PATH."""
    if path == "/":
        path = config.SANDBOX_PATH
    elif path.startswith("/"):
        path = path[1:]
    return path


def validate_path(absolute_path, required_type="file"):
    """Validate if a path is in a configured sandbox, can be accessed and if it is of a specific type."""
    sandbox_path = Path(config.SANDBOX_PATH)
    path_to_validate = Path(os.path.abspath(absolute_path))

    path_in_sandbox = (
        sandbox_path in path_to_validate.parents or sandbox_path == path_to_validate
    )

    if not path_in_sandbox:
        raise PermissionError("Path not in configured sandbox")
    if not os.path.exists(absolute_path):
        raise FileNotFoundError("Not found")
    if not os.access(absolute_path, os.R_OK):
        raise PermissionError("Permission denied")
    if required_type == "file":
        if not os.path.isfile(absolute_path):
            raise WrongObjectType("Not a file")
    elif required_type == "dir":
        if not os.path.isdir(absolute_path):
            raise WrongObjectType("Not a directory")
    else:
        raise WrongObjectType()


def get_hash(e):
    return hashlib.md5(e.encode()).hexdigest()


def get_dir_file_hash_pair(file):
    hashed_path = get_hash(file)
    return hashed_path[:2], hashed_path[2:]


def create_cache_subfolders(cache_path):
    cache_dirs = [
        val1.lower() + val2.lower()
        for val1 in string.hexdigits
        for val2 in string.hexdigits
    ]
    absolute_dirs = [os.path.join(cache_path, dd) for dd in cache_dirs]
    [os.makedirs(dir_to_create, exist_ok=True) for dir_to_create in absolute_dirs]
