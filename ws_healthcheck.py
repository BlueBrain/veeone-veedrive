import asyncio
import json
import os

import aiohttp

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 4444))

URL = f"http://{HOST}:{PORT}/ws"


async def main():
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:

        await send_message(ws)
        async for msg in ws:
            if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                print(f"Got wrong message type: {msg.type}")
                break
            response = json.loads(msg.data)
            try:
                number_files = len(response["result"]["files"])
                print(f"number of files listed: {number_files }", flush=True)
                if number_files > 0:
                    raise SystemExit(0)
                else:
                    raise SystemExit(1)
            except KeyError:
                print(f"Error {response['error']}")
                raise SystemExit(1)


async def send_message(ws):
    await ws.send_str(
        '{"method": "ListDirectory", "id": "1", "params": {"path": "."} }'
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
