import os
import re

import scandir

from .. import config
from ..utils.exceptions import WrongObjectType


def list_directory(path):
    """

    :param path: relative to sandboxpath path of the file
    :type path: str
    :type path: list(str)
    :return: a dict with two lists of dicts
    :rtype: dict{list, (dict)}
    """
    absolute_dir_path = os.path.join(config.SANDBOX_PATH, path)
    validate_path(absolute_dir_path, "dir")

    dirs = []
    files = []
    directory_entries = os.listdir(absolute_dir_path)

    for f in directory_entries:
        file_absolute_path = os.path.join(config.SANDBOX_PATH, path, f)
        if os.path.isdir(file_absolute_path):
            dirs.append(f)
        else:
            files.append({"name": f, "size": os.path.getsize(file_absolute_path)})
    return {"directories": dirs, "files": files}


def sarch_file_system(name):
    found_dirs = []
    found_files = []
    regex = re.compile(name, re.IGNORECASE)
    file_list = scandir.walk(config.SANDBOX_PATH)
    try:
        for path, directories, files in file_list:
            # relative path in order to keep user's requests sandboxed
            relative_path = os.path.relpath(path, config.SANDBOX_PATH)

            for directory in directories:
                if regex.search(directory):
                    found_dirs.append(os.path.join(relative_path, directory))
            for file in files:
                if regex.search(file):
                    found_files.append(
                        {
                            "name": os.path.join(relative_path, file),
                            "size": os.path.getsize(os.path.join(path, file)),
                        }
                    )
    except Exception as e:
        raise
    return {"directories": found_dirs, "files": found_files}


def validate_path(absolute_path, required_type="file"):
    if config.SANDBOX_PATH not in os.path.abspath(absolute_path):
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
