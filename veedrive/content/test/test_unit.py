import os.path
import unittest

from ... import config
from ...utils.exceptions import WrongObjectType
from .. import content_manager, fs_manager


class TestPath(unittest.TestCase):
    def setUp(self):
        self.sandboxpath = config.SANDBOX_PATH  # '/tests/sandbox_folder/'

    def test_exceptions(self):

        with self.assertRaises(PermissionError):
            fs_manager.validate_path("/tmp", "dir")
        with self.assertRaises(PermissionError):
            fs_manager.validate_path(os.path.join(config.SANDBOX_PATH, "../../"), "dir")
        with self.assertRaises(PermissionError):
            fs_manager.validate_path(os.path.join(config.SANDBOX_PATH, "/../"), "file")
        with self.assertRaises(PermissionError):
            fs_manager.validate_path(os.path.join(config.SANDBOX_PATH, "../"), "file")
        with self.assertRaises(FileNotFoundError):
            fs_manager.validate_path(
                os.path.join(config.SANDBOX_PATH, "folder1", "file_not_exisiting"),
                "file",
            )
        with self.assertRaises(WrongObjectType):
            fs_manager.validate_path(
                os.path.join(config.SANDBOX_PATH, "folder1"), "file"
            )
        with self.assertRaises(WrongObjectType):
            fs_manager.validate_path(
                os.path.join(config.SANDBOX_PATH, "folder1", "file1"), "dir"
            )


class TestWsHandlers(unittest.TestCase):
    def setUp(self):
        self.sandboxpath = config.SANDBOX_PATH  # '/tests/sandbox_folder/'

    def test_create_file_response(self):
        path = "file1"
        obj = content_manager._create_file_url_response(path)
        assert obj["url"] == f"{config.STATIC_CONTENT_URL}/{path}"
        assert obj["thumbnail"] == f"{config.CONTENT_URL}/thumb/{path}"


class TestThumbnail(unittest.TestCase):
    # TODO Add TestThumbnail
    # def test_correct_thumbnail_size():
    pass


if __name__ == "__main__":
    unittest.main()
