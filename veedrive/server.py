import json
import logging

import aiohttp
from aiohttp import web
from aiohttp.web import (HTTPBadRequest, HTTPForbidden,
                         HTTPInternalServerError, HTTPNotFound)

from . import config
from .content import content_manager
from .content import ws_handlers as content_handler
from .presentation import ws_handlers as presentation_handler
from .utils import jsonrpc
from .utils.exceptions import CodeException, WrongObjectType

logging.basicConfig(level=config.logger_level)
logger = logging.getLogger(__name__)


async def handle_ws(request):
    """Websocket handler dispatching JSON-RPC to corresponding handlers

    :param request: WS HTTP request
    :type request: class: `aiohttp.web.BaseRequest`
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == "close":
                await ws.close()
            else:
                response = None
                data = json.loads(msg.data)
                try:
                    response = await process_request(data)
                except KeyError as e:
                    await ws.send_str(
                        str(
                            jsonrpc.prepare_error(
                                data, config.MALFORMED_REQUEST, "Malformed"
                            )
                        )
                    )
                except CodeException as e:
                    await ws.send_str(str(jsonrpc.prepare_error_code(data, e)))
                except PermissionError as e:
                    await ws.send_str(
                        str(
                            jsonrpc.prepare_error(
                                data, config.PERMISSION_DENIED, str(e)
                            )
                        )
                    )
                except FileNotFoundError as e:
                    await ws.send_str(
                        str(jsonrpc.prepare_error(data, config.PATH_NOT_FOUND, str(e)))
                    )
                except WrongObjectType as e:
                    await ws.send_str(
                        str(
                            jsonrpc.prepare_error(
                                data, config.WRONG_FILE_TYPE_REQUESTED, str(e)
                            )
                        )
                    )

                await ws.send_str(str(response))

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error(f"ws connection closed with exception {ws.exception()}")


async def process_request(data):
    method = data["method"]
    # Content
    if method == "RequestFile":
        return await content_handler.request_file(data)
    elif method == "RequestImage":
        return await content_handler.request_image(data)
    elif method == "ListDirectory":
        return await content_handler.list_directory(data)
    elif method == "Search":
        return await content_handler.search(data)
    elif method == "SearchResult":
        return await content_handler.get_search_result(data)

    # Scene
    elif method == "ListScenes":
        return await presentation_handler.list_scenes(data)
    elif method == "SceneVersions":
        return await presentation_handler.list_scene_versions(data)
    elif method == "SaveScene":
        return await presentation_handler.save_scene(data)
    elif method == "DeleteScene":
        return await presentation_handler.delete_scene(data)
    elif method == "GetScene":
        return await presentation_handler.get_scene(data)
    # Method not defined
    else:
        return jsonrpc.prepare_error(data, 404, "Method not defined")


async def handle_thumbnail_request(request):
    """Thumbnail endpoint handler. Provides a generated thumbnail

    :param request: thumbnail request
    :type request: class: `aiohttp.web.BaseRequest`
    :return: requested thumnail
    :rtype: class: `aiohttp.web.Response`
    """
    path = request.match_info["path"]
    try:
        try:
            width = int(request.query["width"])
            height = int(request.query["height"])
            mode = request.query["mode"]
            data = await content_manager.get_thumbnail(path, width, height, mode)
        except KeyError:
            data = await content_manager.get_thumbnail(path)
        return web.Response(body=data[0], content_type=data[1])
    except FileNotFoundError as e:
        raise HTTPNotFound()
    except PermissionError as e:
        raise HTTPForbidden()
    except (ValueError, TypeError):
        raise HTTPBadRequest()
    except Exception as e:
        logger.error(e)
        raise e


async def handle_scaled_image_request(request):
    path = request.match_info["path"]
    try:
        width = int(request.query["width"])
        height = int(request.query["height"])
        try:
            mode = str(request.query["mode"])
            data = await content_manager.get_scaled_image(path, width, height, mode)
        except KeyError:
            data = await content_manager.get_scaled_image(path, width, height)
        return web.Response(body=data[0], content_type=data[1])
    except (KeyError, ValueError):
        raise HTTPBadRequest()
    except FileNotFoundError:
        raise HTTPNotFound()
    except PermissionError:
        raise HTTPForbidden()
    except Exception as e:
        logger.error(e)
        raise HTTPInternalServerError()
