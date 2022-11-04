import json
import logging

import aiohttp
from aiohttp import web
from sentry_sdk import configure_scope

from .content import fs_manager
from .presentation import db_manager
from .utils import jsonrpc
from .utils.asynchro import run_async


async def handle_healthcheck(request):
    """Websocket healthcheck handler

    :param request: WS HTTP request
    :type request: class: `aiohttp.web.BaseRequest`
    """
    with configure_scope() as scope:
        if scope.transaction:
            scope.transaction.sampled = False

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == "close":
                await ws.close()
            else:
                data = json.loads(msg.data)
                try:
                    if data["method"] == "HealthCheck":
                        data["params"] = {"path": "."}
                        fs_result = await run_async(fs_manager.list_directory, ".")
                        fs_operational = (
                            True
                            if fs_result["directories"] or fs_result["files"]
                            else False
                        )

                        presentation_list = await (
                            await db_manager.get_db()
                        ).list_presentations()
                        folder_list = await (await db_manager.get_db()).list_folders()
                        db_operational = bool(presentation_list or folder_list)
                        response = {
                            "fs_ok": fs_operational,
                            "db_ok": db_operational,
                        }
                        await ws.send_str(jsonrpc.prepare_response(data, response))
                except Exception as e:
                    await ws.send_str(
                        jsonrpc.prepare_error(
                            data, 13, "Issue while performing health check: " + str(e)
                        )
                    )
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logging.error(f"ws connection closed with exception {ws.exception()}")
    return ws
