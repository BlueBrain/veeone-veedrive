import os.path
import unittest

import cv2

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
        with self.assertRaises(PermissionError):
            fs_manager.validate_path(os.path.join(config.SANDBOX_PATH, "/"), "file")
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
        path = "chess.jpg"
        obj = content_manager._create_file_url_response(path)
        assert obj["url"] == f"{config.STATIC_CONTENT_URL}/{path}"
        assert obj["thumbnail"] == f"{config.CONTENT_URL}/thumb/{path}"


class TestThumbnail(unittest.TestCase):
    # TODO Add TestThumbnail
    # def test_correct_thumbnail_size():
    pass


class TestContentOptimization(unittest.TestCase):
    cache_folder = "/tmp/testoptimized"
    sandbox_path = config.SANDBOX_PATH

    def setUp(self):
        import shutil

        if os.path.exists(self.cache_folder):
            shutil.rmtree(self.cache_folder)

    def test_portait_image(self):
        path = "NeuronGroup.jpg"
        img = cv2.imread(os.path.join(self.sandbox_path, path), cv2.IMREAD_UNCHANGED)

        optimized = content_manager.optimize_image(
            path, self.sandbox_path, self.cache_folder, 4096, 4096
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)

        self.check_aspect(img, optimized)
        assert optimized.shape[0] == 4096
        assert (
            optimized.shape[1]
            == optimized.shape[0] * optimized.shape[1] / optimized.shape[0]
        )

        os.remove(os.path.join(self.cache_folder, path))

        optimized = content_manager.optimize_image(
            path, self.sandbox_path, self.cache_folder, 4096, 512
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        self.check_aspect(img, optimized)
        assert optimized.shape[0] == 512
        assert optimized.shape[1] == optimized.shape[0] / (
            optimized.shape[0] / optimized.shape[1]
        )  # 133

        os.remove(os.path.join(self.cache_folder, path))

        optimized = content_manager.optimize_image(
            path, self.sandbox_path, self.cache_folder, 120, 512
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        self.check_aspect(img, optimized)
        assert optimized.shape[1] == 120
        assert optimized.shape[0] == optimized.shape[1] * (
            optimized.shape[0] / optimized.shape[1]
        )  # 458

    def test_landscape_image(self):
        path = "HorizontalGroup.jpg"
        img = cv2.imread(os.path.join(self.sandbox_path, path), cv2.IMREAD_UNCHANGED)

        optimized = content_manager.optimize_image(
            path, self.sandbox_path, self.cache_folder, 4096, 4096
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        self.check_aspect(img, optimized)
        assert optimized.shape[1] == 4096
        assert optimized.shape[0] == optimized.shape[1] / (
            optimized.shape[1] / optimized.shape[0]
        )

        os.remove(os.path.join(self.cache_folder, path))

        optimized = content_manager.optimize_image(
            path, self.sandbox_path, self.cache_folder, 4096, 512
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        self.check_aspect(img, optimized)
        assert optimized.shape[0] == 512
        assert optimized.shape[1] == optimized.shape[0] / (
            optimized.shape[0] / optimized.shape[1]
        )  # 1958

        os.remove(os.path.join(self.cache_folder, path))

        optimized = content_manager.optimize_image(
            path, self.sandbox_path, self.cache_folder, 512, 120
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        print(optimized.shape)
        self.check_aspect(img, optimized, float_precision=1)
        assert optimized.shape[1] == 459
        assert optimized.shape[0] == optimized.shape[1] * (
            optimized.shape[0] / optimized.shape[1]
        )  # 120

    def test_image_with_size_smaller_than_box(self):
        path = "chess.jpg"
        img = cv2.imread(os.path.join(self.sandbox_path, path), cv2.IMREAD_UNCHANGED)

        optimized = content_manager.optimize_image(
            path, self.sandbox_path, self.cache_folder, 4096, 4096
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)

        self.check_aspect(img, optimized)
        assert optimized.shape[0] == img.shape[0]

        os.remove(os.path.join(self.cache_folder, path))

        img = cv2.imread(os.path.join(self.sandbox_path, path), cv2.IMREAD_UNCHANGED)
        optimized = content_manager.optimize_image(
            path, self.sandbox_path, self.cache_folder, 4096, 500
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)

        self.check_aspect(img, optimized)
        assert optimized.shape[0] == optimized.shape[1] == 500

    def test_square_image(self):
        path = "chess.jpg"
        img = cv2.imread(os.path.join(self.sandbox_path, path), cv2.IMREAD_UNCHANGED)

        optimized = content_manager.optimize_image(
            path, self.sandbox_path, self.cache_folder, 512, 512
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)

        self.check_aspect(img, optimized)
        assert optimized.shape[0] == optimized.shape[1] == 512

    @staticmethod
    def check_aspect(img1, img2, float_precision=2):
        assert round(img1.shape[1] / img1.shape[0], float_precision) == round(
            img2.shape[1] / img2.shape[0], float_precision
        )


if __name__ == "__main__":
    unittest.main()
