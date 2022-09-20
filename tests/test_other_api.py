import json

import aiohttp
import pytest

from veedrive import config

@pytest.mark.asyncio
async def test_configuration(testing_backend):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{config.DEFAULT_HOST}:{config.DEFAULT_PORT}/config") as resp:
            reponse = json.loads(await resp.text())
            assert reponse["SANDBOX_PATH"] == config.SANDBOX_PATH


@pytest.mark.asyncio
async def test_healthcheck(testing_backend, setup_db):
    async def create_presentation_folder():
        request_payload = {
            "method": "CreateFolder",
            "id": "1",
            "params": {"folder_name": "folder"},
        }
        await testing_backend.send_ws(request_payload)

    await create_presentation_folder()
    payload = {
        "method": "HealthCheck",
        "id": "2",
    }
    response = await testing_backend.send_ws(payload, endpoint="healthcheck")
    result = response["result"]
    assert result["fs_ok"] and result["db_ok"]
