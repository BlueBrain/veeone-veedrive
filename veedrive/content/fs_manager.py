import os
import re

import scandir

from .. import config
from .utils import sanitize_path, validate_path


@sanitize_path
def list_directory(path):
    """
    List content (files and directories) of a specified directory.

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
