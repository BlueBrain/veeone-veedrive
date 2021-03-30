import json
import unittest

import aiounittest
import pymongo
import testing_server
import websockets

import veedrive.config as config


class Test(aiounittest.AsyncTestCase):
    async def test_1_save_scene(self):
        mongo_client = pymongo.MongoClient()
        mongo_client.drop_database(config.DB_NAME)
        f = open("tests/presentations.json")
        scenes = json.load(f)
        f.close()
        scene1, scene1_update, scene2 = scenes

        scene1_save_1_payload = {
            "method": "SaveScene",
            "id": "1",
            "params": {"presentation": scene1},
        }
        response = await self._send_ws(scene1_save_1_payload)
        assert response["result"] == 0

        scene1_save_2_payload = {
            "method": "SaveScene",
            "id": "1",
            "params": {"presentation": scene1_update},
        }
        response = await self._send_ws(scene1_save_2_payload)
        assert response["result"] == 0

        scene2_save_1_payload = {
            "method": "SaveScene",
            "id": "1",
            "params": {"presentation": scene2, "clientId": "client123"},
        }
        response = await self._send_ws(scene2_save_1_payload)
        assert response["result"] == 0

        scene2_save_2_payload = {
            "method": "SaveScene",
            "id": "1",
            "params": {"presentation": scene2, "clientId": "client123"},
        }
        response = await self._send_ws(scene2_save_2_payload)
        assert response["result"] == 0

        scene1_save_3_payload = {
            "method": "SaveScene",
            "id": "1",
            "params": {"presentation": scene1},
        }
        response = await self._send_ws(scene1_save_3_payload)
        assert response["result"] == 0

    async def test_2_list_scenes(self):
        obj = {"method": "ListScenes", "id": "1", "params": {}}
        response = await self._send_ws(obj)
        assert response["id"] == "1"
        assert isinstance(response["result"], list)
        assert len(response["result"]) == 2
        self._validate_scenes_fields((response["result"]))

    async def test_2_list_archived_scenes(self):
        obj = {"method": "SceneVersions", "id": "1", "params": {"name": "scene1"}}
        response = await self._send_ws(obj)
        assert len(response["result"]) == 2
        self._validate_scenes_fields((response["result"]))

        f = open("tests/presentations.json")
        # the first object from presentations.json was saved first and next over-written by second object
        # in test_1_save_scene
        scene1 = json.load(f)[0]
        f.close()

        version_1 = response["result"][0]
        # remove keys added when versioning
        version_1.pop("_id", None)
        version_1.pop("version", None)
        assert scene1 == version_1

        obj = {"method": "SceneVersions", "id": "1", "params": {"name": "scene2"}}
        response = await self._send_ws(obj)
        assert len(response["result"]) == 1

        # Test for MALFORMED error
        obj = {"method": "SceneVersions", "id": "1", "params": {"ame": "scene1"}}
        response = await self._send_ws(obj)
        assert response["error"]["code"] == 4

    async def test_5_delete_scene(self):
        obj = {
            "method": "DeleteScene",
            "id": "1",
            "params": {"name": "scene1"},
        }
        response = await self._send_ws(obj)
        assert response["id"] == "1"
        assert response["result"] == 0

        obj = {"method": "GetScene", "id": "1", "params": {"name": "scene1"}}
        response = await self._send_ws(obj)
        assert "error" in response

        obj = {"method": "ListScenes", "id": "1", "params": {}}
        response = await self._send_ws(obj)
        assert len(response["result"]) == 1

        # Test for SCENE_NOT_FOUND error on a subsequent
        obj = {
            "method": "DeleteScene",
            "id": "1",
            "params": {"name": "scene1", "clientId": "client_id_123"},
        }
        response = await self._send_ws(obj)
        assert response["error"]["code"] == 0

        # Test for MALFORMED error
        obj = {"method": "DeleteScene", "id": "1", "params": {"ame": "scene1"}}
        response = await self._send_ws(obj)
        assert response["error"]["code"] == 4

        # Test archive
        obj = {
            "method": "GetScene",
            "id": "1",
            "params": {"name": "scene2", "clientId": "client_id_123"},
        }
        response = await self._send_ws(obj)
        scene_1 = response["result"]

        obj = {"method": "SceneVersions", "id": "1", "params": {"name": "scene2"}}
        response = await self._send_ws(obj)
        assert len(response["result"]) == 1

        obj = {
            "method": "DeleteScene",
            "id": "1",
            "params": {"name": "scene2", "clientId": "client_id_456"},
        }
        await self._send_ws(obj)

        obj = {"method": "SceneVersions", "id": "1", "params": {"name": "scene2"}}
        response = await self._send_ws(obj)
        assert len(response["result"]) == 1

        version_1 = response["result"][0]

        # remove _id and keys added when versioning
        version_1.pop("_id", None)
        version_1.pop("version", None)
        scene_1.pop("_id", None)
        assert scene_1 == version_1

    @staticmethod
    async def _send_ws(obj):
        async with websockets.connect("ws://localhost:4444/ws") as websocket:
            await websocket.send(json.dumps(obj))
            response = await websocket.recv()
            return json.loads(response)

    @staticmethod
    def _validate_scenes_fields(scenes):
        # for presentation in [json.loads(presentation) for presentation in scenes]:
        for scene in scenes:
            assert scene["name"]
            assert scene["_id"]
            assert scene["theme"]

            # Topic validation
            topics = scene["topics"]
            assert isinstance(topics, list)
            for topic in topics:
                assert topic["layout"]
                assert topic["name"]
                assert topic["windows"]
                # Window validation
                windows = topic["windows"]
                assert isinstance(windows, list)
                for window in windows:
                    assert isinstance(window["aspect"], float)
                    assert isinstance(window["selected"], bool)
                    assert isinstance(window["dimensions"], list)
                    assert isinstance(window["size"], list)
                    assert isinstance(window["source"], str)
                    assert isinstance(window["mode"], int)


if __name__ == "__main__":

    testing_server.start_server(verbose=True)
    try:
        unittest.main()
    finally:
        testing_server.kill_server()
