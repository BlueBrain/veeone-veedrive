import asyncio
import datetime
import hashlib
import logging
import os
import re
import threading
import time

import scandir

from .. import config
from .utils import sanitize_path, validate_path

logger = logging.getLogger(__name__)

fs_search_results = {}


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
    absolute_dir_path = os.path.normpath(os.path.join(config.SANDBOX_PATH, path))
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


def search_file(name, starting_path=""):
    absolute_path = os.path.join(config.SANDBOX_PATH, starting_path)
    search_id = hashlib.md5(absolute_path.encode()).hexdigest()

    try:
        absolute_path = os.path.join(config.SANDBOX_PATH, starting_path)
        validate_path(absolute_path, required_type="dir")
    except Exception as e:
        raise

    if search_id not in fs_search_results:
        FileSystemCrawler(name, search_id, absolute_path).start()

    return search_id


async def purge_search_results():
    def purge_done(result):
        finish_time = result["finished_at"]
        delta = datetime.datetime.now() - finish_time
        if delta > datetime.timedelta(seconds=config.SEARCH_FS_KEEP_FINISHED_INTERVAL):
            fs_search_results.pop(e)
            logger.debug(
                f"Purging Search result: {e} finished_at {finish_time} "
                "and not retrieved by a client"
            )

    def purge_running(result):
        start_time = result["started_at"]
        delta = datetime.datetime.now() - start_time
        if delta > datetime.timedelta(seconds=config.SEARCH_FS_THREAD_TIMEOUT):
            for th in threading.enumerate():
                if e == th.getName():
                    th.stop()
                    fs_search_results.pop(e)
                    logger.debug(
                        f"Killed Search thread: {th.getName()}, started at {start_time}"
                    )

    try:
        while True:
            for e in fs_search_results.copy():
                search_result = fs_search_results[e]
                if search_result["done"]:
                    purge_done(search_result)
                else:
                    purge_running(search_result)

            await asyncio.sleep(config.SEARCH_FS_PURGE_LOOP_INTERVAL)
    except Exception as e:
        logger.error(f"Purge search issue: {e}")


class FileSystemCrawler(threading.Thread):
    def __init__(self, searched_name, search_id, starting_path):
        super(FileSystemCrawler, self).__init__(name=search_id)
        self.searched_name = searched_name
        self.search_id = search_id
        self.stating_paht = starting_path
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        name = self.searched_name
        starting_path = self.stating_paht
        search_id = self.search_id

        found_dirs = []
        found_files = []
        regex = re.compile(name, re.IGNORECASE)
        file_list = scandir.walk(starting_path)

        t1 = time.perf_counter()

        search_result = {"done": False, "files": found_files, "directories": found_dirs}

        import datetime

        search_result["started_at"] = datetime.datetime.now()

        fs_search_results[search_id] = search_result
        try:
            for path, directories, files in file_list:
                if self._stop_event.isSet():
                    return

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
            t2 = time.perf_counter()
            search_result["done"] = True
            search_result["finished_at"] = datetime.datetime.now()
            logger.debug(
                f"Search for '{name}' at path '{starting_path}' took {t2 - t1:.2f} s."
            )
        except Exception as e:
            raise
