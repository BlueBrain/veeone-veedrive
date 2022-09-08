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


