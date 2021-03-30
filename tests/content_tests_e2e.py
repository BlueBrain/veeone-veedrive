import json
import os
import unittest

import aiounittest
import cv2
import imageio
import numpy as np
import requests
import testing_server
import websockets
from aiohttp.web import HTTPBadRequest, HTTPNotFound, HTTPOk

from veedrive import config

tmp_filename = "/tmp/content_test_gif.tmp"


class Test(aiounittest.AsyncTestCase):
    async def test_request_image(self):
        payload = {"method": "RequestImage", "id": "1", "params": {"path": "chess.jpg"}}
        response = await self._send_ws(payload)
        assert response["id"] == "1"
        assert "thumbnail" in response["result"]
        assert "url" in response["result"]

        payload = {
            "method": "RequestImage",
            "id": "2",
            "params": {
                "path": "chess.jpg",
                "clientSize": {"width": 500, "height": 100},
            },
        }
        response = await self._send_ws(payload)
        result = response["result"]
        # Check for extended keys
        assert response["id"] == "2"
        assert result["thumbnail"] == f"{config.CONTENT_URL}/thumb/chess.jpg"
        assert (
            result["scaled"]
            == f"{config.CONTENT_URL}/scaled/chess.jpg?width=500&height=100"
        )
        assert result["url"] == f"{config.STATIC_CONTENT_URL}/chess.jpg"
        assert isinstance(result["size"], int)

        # Check if content is served
        for image_type in ["thumbnail", "scaled", "url"]:
            req = requests.get(result[image_type])
            assert req.status_code == HTTPOk.status_code

    async def test_get_image(self):
        payload = {
            "method": "RequestImage",
            "id": "2",
            "params": {
                "path": "chess.jpg",
                "clientSize": {"width": 500, "height": 100},
            },
        }
        response = await self._send_ws(payload)
        result = response["result"]
        # Request thumbnail and check its size
        req = requests.get(result["thumbnail"])
        img = cv2.imdecode(np.frombuffer(req.content, np.uint8), cv2.IMREAD_UNCHANGED)
        assert img.shape == (256, 256, 3)

        # Request url size (1000, 1000)
        req = requests.get(result["url"])
        img = cv2.imdecode(np.frombuffer(req.content, np.uint8), cv2.IMREAD_UNCHANGED)
        assert img.shape == (1000, 1000, 3)

        # Request scaled down size image and check its size
        req = requests.get(result["scaled"])
        img = cv2.imdecode(np.frombuffer(req.content, np.uint8), cv2.IMREAD_UNCHANGED)
        assert img.shape == (100, 100, 3)

        payload = {
            "method": "RequestImage",
            "id": "2",
            "params": {"path": "chess.jpg", "clientSize": {"width": 50, "height": 100}},
        }
        response = await self._send_ws(payload)
        result = response["result"]
        req = requests.get(result["scaled"])
        img = cv2.imdecode(np.frombuffer(req.content, np.uint8), cv2.IMREAD_UNCHANGED)
        assert img.shape == (50, 50, 3)

        # Get a thumbnail fitting or filling a specified box
        thumbnail_specific_size_url = (
            result["thumbnail"] + "?width=100&height=50&mode=fill"
        )
        req = requests.get(thumbnail_specific_size_url)
        img = cv2.imdecode(np.frombuffer(req.content, np.uint8), cv2.IMREAD_UNCHANGED)
        assert img.shape == (50, 100, 3)

        thumbnail_specific_size_url = (
            result["thumbnail"] + "?width=100&height=50&mode=fit"
        )
        req = requests.get(thumbnail_specific_size_url)
        img = cv2.imdecode(np.frombuffer(req.content, np.uint8), cv2.IMREAD_UNCHANGED)
        assert img.shape == (50, 50, 3)

        # Query param validatation
        thumbnail_specific_size_url = (
            result["thumbnail"] + "?width=100&height=a&mode=fit"
        )
        req = requests.get(thumbnail_specific_size_url)
        assert req.status_code == HTTPBadRequest.status_code

        thumbnail_specific_size_url = (
            result["scaled"] + "?width=100&height=100&mode=center"
        )
        req = requests.get(thumbnail_specific_size_url)
        assert req.status_code == HTTPBadRequest.status_code

        # Path validation
        req = requests.get(f"{config.STATIC_CONTENT_URL}/chess.jpg")
        assert req.status_code == HTTPOk.status_code

        req = requests.get(f"{config.STATIC_CONTENT_URL}/MISSING_chess.jpg")
        assert req.status_code == HTTPNotFound.status_code

        req = requests.get(f"{config.STATIC_CONTENT_URL}/thumb/../chess.jpg")
        assert (
            req.status_code == HTTPOk.status_code
        )  # not 403 as '../' is handled by aiohttp.web.static

    async def test_request_image_error(self):
        payload = {
            "method": "RequestImage",
            "id": "1",
            "params": {"path": "chess_dont_exist.jpg"},
        }
        response = await self._send_ws(payload)
        assert response["error"]["code"] == 0

        payload = {"method": "RequestImage", "id": "1", "params": {"path": "folder1"}}
        response = await self._send_ws(payload)
        assert response["error"]["code"] == 1

        payload = {
            "method": "RequestImage",
            "id": "1",
            "params": {"path": "../content_tests_e2e.py"},
        }
        response = await self._send_ws(payload)
        # TODO: Rework error codes
        # assert response["error"]["code"] == 3

    async def test_request_file(self):
        payload = {"method": "RequestFile", "id": "1", "params": {"path": "file.pdf"}}
        response = await self._send_ws(payload)
        result = response["result"]
        assert response["id"] == "1"

        # Check for standard keys of result
        assert response["id"] == "1"
        assert result["thumbnail"] == f"{config.CONTENT_URL}/thumb/file.pdf"
        assert result["url"] == f"{config.STATIC_CONTENT_URL}/file.pdf"
        assert isinstance(result["size"], int)

        # Check if content is served

        for image_type in ["thumbnail", "url"]:
            req = requests.get(result[image_type])
            assert req.status_code == HTTPOk.status_code

    async def test_get_pdf_thumbnail(self):
        thumbnail_url = await self._get_thumbnail_url("file.pdf")
        req = requests.get(thumbnail_url)
        img = cv2.imdecode(np.frombuffer(req.content, np.uint8), cv2.IMREAD_UNCHANGED)
        assert img.shape == (256, 181, 3)  # Aspect ratio of A4

    async def test_get_pdf_thumbnail_with_size_constraint(self):
        thumbnail_url = await self._get_thumbnail_url("file.pdf")
        thumbnail_specific_size_url = thumbnail_url + "?width=70&height=50&mode=fit"

        req = requests.get(thumbnail_specific_size_url)
        img = cv2.imdecode(np.frombuffer(req.content, np.uint8), cv2.IMREAD_UNCHANGED)
        assert img.shape == (50, 35, 3)

        thumbnail_specific_size_url = thumbnail_url + "?width=70&height=50&mode=fill"

        req = requests.get(thumbnail_specific_size_url)
        img = cv2.imdecode(np.frombuffer(req.content, np.uint8), cv2.IMREAD_UNCHANGED)
        assert img.shape == (50, 70, 3)

    async def test_get_movie_thumbnail(self):
        thumbnail_url = await self._get_thumbnail_url("bbb_short.mp4")
        req = requests.get(thumbnail_url)
        with open(tmp_filename, "wb+") as f:
            f.write(req.content)
        gif = imageio.mimread(tmp_filename)
        assert gif[1].shape == (144, 256, 4)

    async def test_get_movie_thumbnail_with_size_constraint(self):
        thumbnail_url = await self._get_thumbnail_url("bbb_short.mp4")
        req = requests.get(thumbnail_url + "?width=70&height=50&mode=fit")
        with open(tmp_filename, "wb+") as f:
            f.write(req.content)
        gif = imageio.mimread(tmp_filename)

        assert gif[1].shape == (39, 70, 4)

        req = requests.get(thumbnail_url + "?width=35&height=50&mode=fit")
        with open(tmp_filename, "wb+") as f:
            f.write(req.content)
        gif = imageio.mimread(tmp_filename)
        assert gif[1].shape == (20, 35, 4)

        req = requests.get(thumbnail_url + "?width=70&height=50&mode=fill")
        with open(tmp_filename, "wb+") as f:
            f.write(req.content)
        gif = imageio.mimread(tmp_filename)
        assert gif[1].shape == (50, 70, 4)

        # Video clip in portait orientation
        thumbnail_url = await self._get_thumbnail_url("bbb_vertical.mp4")
        req = requests.get(thumbnail_url + "?width=70&height=50&mode=fit")
        with open(tmp_filename, "wb+") as f:
            f.write(req.content)
        gif = imageio.mimread(tmp_filename)

        assert gif[1].shape == (50, 28, 4)

        req = requests.get(thumbnail_url + "?width=70&height=50&mode=fill")
        with open(tmp_filename, "wb+") as f:
            f.write(req.content)
        gif = imageio.mimread(tmp_filename)
        assert gif[1].shape == (50, 70, 4)

        os.remove(tmp_filename)

    async def test_list_directory(self):
        payload = {
            "method": "ListDirectory",
            "id": "1",
            "params": {"path": "bbb_vertical.mp4"},
        }
        response = await self._send_ws(payload)
        # TODO: Rework error codes
        # assert response["error"]["code"] == 2  # not a directory

        payload = {
            "method": "ListDirectory",
            "id": "1",
            "params": {"path": "./NOT_EXISTING"},
        }
        response = await self._send_ws(payload)
        assert response["error"]["code"] == 0  # not found

        payload = {"method": "ListDirectory", "id": "1", "params": {"path": "./"}}
        response = await self._send_ws(payload)
        files = response["result"]["files"]
        dirs = response["result"]["directories"]
        assert isinstance(files, list)
        assert isinstance(dirs, list)

    async def test_search(self):
        payload = {"method": "Search", "id": "1", "params": {"name": "bbb"}}
        response = await self._send_ws(payload)
        files = response["result"]["files"]
        assert isinstance(files, list)
        assert len(files) == 2

        payload = {"method": "Search", "id": "1", "params": {"name": "folder"}}
        response = await self._send_ws(payload)
        dirs = response["result"]["directories"]
        assert isinstance(dirs, list)
        assert len(dirs) == 2

    @staticmethod
    async def _send_ws(payload):
        async with websockets.connect("ws://localhost:4444/ws") as websocket:
            await websocket.send(json.dumps(payload))
            response = await websocket.recv()
            return json.loads(response)

    async def _get_thumbnail_url(self, file_name):
        payload_data = {
            "method": "RequestFile",
            "id": "1",
            "params": {"path": file_name},
        }
        response = await self._send_ws(payload_data)
        return response["result"]["thumbnail"]


if __name__ == "__main__":
    testing_server.start_server(verbose=True)
    try:
        unittest.main()
    finally:
        testing_server.kill_server()
