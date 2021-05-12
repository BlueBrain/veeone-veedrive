import json
import os
import signal
import subprocess
import time

import pytest
import websockets

from veedrive import config

FNULL = open(os.devnull, "w")
server = None


@pytest.fixture(scope="session")
def testing_backend(request):
    start_server(verbose=True)

    def teardown():
        kill_server()

    request.addfinalizer(teardown)
    return TestHelper


def start_server(verbose=False):
    global server
    print("VEEDRIVE_MEDIA_PATH configured as:", os.getenv("VEEDRIVE_MEDIA_PATH"))
    if verbose:
        server = subprocess.Popen(["python3", "-m", "veedrive.main"])
    else:
        server = subprocess.Popen(
            ["python3", "-m", "veedrive.main"], stdout=FNULL, stderr=FNULL
        )
    time.sleep(2)


def kill_server():
    server.send_signal(signal.SIGINT)
    server.wait()
    FNULL.close()


class TestHelper:
    @staticmethod
    async def send_ws(payload):
        async with websockets.connect(
            f"ws://{config.DEFAULT_HOST}:{config.DEFAULT_PORT}/ws"
        ) as websocket:
            await websocket.send(json.dumps(payload))
            response = await websocket.recv()
            return json.loads(response)

    @staticmethod
    async def get_thumbnail_url(file_name):
        payload_data = {
            "method": "RequestFile",
            "id": "1",
            "params": {"path": file_name},
        }
        response = await TestHelper.send_ws(payload_data)
        return response["result"]["thumbnail"]
