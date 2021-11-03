import os
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
