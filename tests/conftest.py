import asyncio
import json
import os
import signal
import subprocess
import time

import pytest
import websockets
from asyncpg import connect

from veedrive import config

FNULL = open(os.devnull, "w")
server = None


# Redefine event loop in order to run setup_db fixture in module scope
@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def setup_db():
    conn = await connect(
        database=config.DB_NAME,
        user=config.DB_USERNAME,
        host=config.DB_HOST,
        password=config.DB_PASSWORD,
    )
    await conn.execute(
        "CREATE TABLE IF NOT EXISTS public.presentations (id SERIAL NOT NULL, data jsonb NOT NULL,  CONSTRAINT presentation_pkey PRIMARY KEY (id))"
    )
    await conn.execute(
        "CREATE TABLE IF NOT EXISTS public.archived_presentations (id SERIAL NOT NULL, data jsonb NOT NULL, CONSTRAINT archived_presentation_pkey PRIMARY KEY (id))"
    )
    await conn.execute(
        "CREATE TABLE IF NOT EXISTS public.folders (name VARCHAR NOT NULL, PRIMARY KEY (name))"
    )

    await conn.execute(f"DELETE from presentations;")
    await conn.execute(f"DELETE from archived_presentations;")
    await conn.execute(f"DELETE from folders;")


@pytest.fixture(scope="session")
def testing_backend(request):
    start_server(verbose=True)

    def teardown():
        kill_server()

    request.addfinalizer(teardown)
    return TestHelper


def start_server(verbose=False):
    global server
    sandbox_test_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "sandbox_folder"
    )
    os.environ["VEEDRIVE_MEDIA_PATH"] = sandbox_test_folder

    print("VEEDRIVE_MEDIA_PATH configured as:", os.getenv("VEEDRIVE_MEDIA_PATH"))
    if verbose:
        server = subprocess.Popen(["python3", "-m", "veedrive.main"])
    else:
        server = subprocess.Popen(
            ["python3", "-m", "veedrive.main"], stdout=FNULL, stderr=FNULL
        )
    config.THUMBNAIL_CACHE_PATH = os.path.join(config.SANDBOX_PATH, "cache")
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
