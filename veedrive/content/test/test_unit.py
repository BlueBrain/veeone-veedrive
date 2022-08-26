import os.path
import shutil
import unittest

import cv2

from ... import config
from ...utils.exceptions import WrongObjectType
from .. import content_manager, fs_manager

sandboxpath = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tests", "sandbox_folder"))
config.SANDBOX_PATH = sandboxpath


class TestPath(unittest.TestCase):
    def test_exceptions(self):
        with self.assertRaises(PermissionError):
            fs_manager.validate_path("/tmp", "dir")
        with self.assertRaises(PermissionError):
            fs_manager.validate_path(os.path.join(sandboxpath, "../../"), "dir")
        with self.assertRaises(PermissionError):
            fs_manager.validate_path(os.path.join(sandboxpath, "/../"), "file")
        with self.assertRaises(PermissionError):
            fs_manager.validate_path(os.path.join(sandboxpath, "../"), "file")
        with self.assertRaises(PermissionError):
            fs_manager.validate_path(os.path.join(sandboxpath, "/"), "file")

        with self.assertRaises(FileNotFoundError):
            fs_manager.validate_path(
                os.path.join(sandboxpath, "folder1", "file_not_exisiting"),
                "file",
            )
        with self.assertRaises(WrongObjectType):
            fs_manager.validate_path(
                os.path.join(sandboxpath, "folder1"), "file"
            )
        with self.assertRaises(WrongObjectType):
            fs_manager.validate_path(
                os.path.join(sandboxpath, "folder1", "file1"), "dir"
            )


class TestWsHandlers(unittest.TestCase):
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

    def setUp(self):
        if os.path.exists(self.cache_folder):
            shutil.rmtree(self.cache_folder)

    def test_portait_image(self):
        file_name = "NeuronGroup.jpg"
        img = cv2.imread(
            os.path.join(sandboxpath, file_name), cv2.IMREAD_UNCHANGED
        )

        optimized = content_manager.optimize_image(
            file_name, sandboxpath, self.cache_folder, 4096, 4096
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)

        self.check_aspect(img, optimized)
        assert optimized.shape[0] == 4096
        assert (
            optimized.shape[1]
            == optimized.shape[0] * optimized.shape[1] / optimized.shape[0]
        )

        os.remove(os.path.join(self.cache_folder, file_name))

        optimized = content_manager.optimize_image(
            file_name, sandboxpath, self.cache_folder, 4096, 512
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        self.check_aspect(img, optimized)
        assert optimized.shape[0] == 512
        assert optimized.shape[1] == optimized.shape[0] / (
            optimized.shape[0] / optimized.shape[1]
        )  # equals 133

        os.remove(os.path.join(self.cache_folder, file_name))

        optimized = content_manager.optimize_image(
            file_name, sandboxpath, self.cache_folder, 120, 512
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        self.check_aspect(img, optimized)
        assert optimized.shape[1] == 120
        assert optimized.shape[0] == optimized.shape[1] * (
            optimized.shape[0] / optimized.shape[1]
        )  # equals 458

    def test_landscape_image(self):
        file_name = "HorizontalGroup.jpg"
        img = cv2.imread(
            os.path.join(sandboxpath, file_name), cv2.IMREAD_UNCHANGED
        )

        optimized = content_manager.optimize_image(
            file_name, sandboxpath, self.cache_folder, 4096, 4096
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        self.check_aspect(img, optimized)
        assert optimized.shape[1] == 4096
        assert optimized.shape[0] == optimized.shape[1] / (
            optimized.shape[1] / optimized.shape[0]
        )

        os.remove(os.path.join(self.cache_folder, file_name))

        optimized = content_manager.optimize_image(
            file_name, sandboxpath, self.cache_folder, 4096, 512
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        self.check_aspect(img, optimized)
        assert optimized.shape[0] == 512
        assert optimized.shape[1] == optimized.shape[0] / (
            optimized.shape[0] / optimized.shape[1]
        )  # equals 1958

        os.remove(os.path.join(self.cache_folder, file_name))

        optimized = content_manager.optimize_image(
            file_name, sandboxpath, self.cache_folder, 512, 120
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)
        self.check_aspect(img, optimized, float_precision=1)
        assert optimized.shape[1] == 459
        assert optimized.shape[0] == optimized.shape[1] * (
            optimized.shape[0] / optimized.shape[1]
        )  # equals 120

    def test_image_with_size_smaller_than_box(self):
        path = "chess.jpg"
        img = cv2.imread(os.path.join(sandboxpath, path), cv2.IMREAD_UNCHANGED)

        optimized = content_manager.optimize_image(
            path, sandboxpath, self.cache_folder, 4096, 4096
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)

        self.check_aspect(img, optimized)
        assert optimized.shape[0] == img.shape[0]

        os.remove(os.path.join(self.cache_folder, path))

        img = cv2.imread(os.path.join(sandboxpath, path), cv2.IMREAD_UNCHANGED)
        optimized = content_manager.optimize_image(
            path, sandboxpath, self.cache_folder, 4096, 500
        )
        optimized = cv2.imread(str(optimized), cv2.IMREAD_UNCHANGED)

        self.check_aspect(img, optimized)
        assert optimized.shape[0] == optimized.shape[1] == 500

    def test_square_image(self):
        path = "chess.jpg"
        img = cv2.imread(os.path.join(sandboxpath, path), cv2.IMREAD_UNCHANGED)

        optimized = content_manager.optimize_image(
            path, sandboxpath, self.cache_folder, 512, 512
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
