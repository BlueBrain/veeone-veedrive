import asyncio
import json

from aiohttp import ClientSession


async def main():
    try:
        session = ClientSession()
        async with session.ws_connect("http://0.0.0.0:4444/ws") as ws:
            await ws.send_str(
                '{"method": "ListDirectory", "id": "1", "params": {"path": "."} }'
            )
            async for msg in ws:
                data = json.loads(msg.data)
                if "result" in data:
                    print("data from ws handler:", data)
                    raise SystemExit(0)
                else:
                    raise Exception
    except Exception as e:
        print(str(e))
        raise SystemExit(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
