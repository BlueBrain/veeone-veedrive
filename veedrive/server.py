import asyncio
import json
import logging
import os.path
from concurrent.futures import ProcessPoolExecutor

import aiohttp
import cv2
from aiohttp import web
from aiohttp.web import (HTTPBadRequest, HTTPForbidden,
                         HTTPInternalServerError, HTTPNotFound, HTTPOk)

from . import config
from .content import content_manager
from .content import ws_handlers as content_handler
from .content.utils import get_dir_file_hash_pair
from .presentation import ws_handlers as presentation_handler
from .utils import jsonrpc
from .utils.exceptions import CodeException, WrongObjectType

loop = asyncio.get_event_loop()


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
            logging.error(f"ws connection closed with exception {ws.exception()}")
    return ws

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
    elif method == "ListPresentations":
        return await presentation_handler.list_presentations(data)
    elif method == "GetPresentation":
        return await presentation_handler.get_presentation(data)
    elif method == "SavePresentation":
        return await presentation_handler.save_presentation(data)
    elif method == "PresentationVersions":
        return await presentation_handler.list_scene_versions(data)
    elif method == "DeletePresentation":
        return await presentation_handler.delete_presentation(data)
    elif method == "PurgePresentations":
        return await presentation_handler.purge_presentations(data)
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
        extra_query_parms = "width", "height", "mode"
        if not all(e in request.query.keys() for e in extra_query_parms):
            thumnail_cache_path = os.path.join(*get_dir_file_hash_pair(path))
            if os.path.exists(
                os.path.join(config.THUMBNAIL_CACHE_PATH, thumnail_cache_path)
            ):
                return web.HTTPFound(
                    f"{config.STATIC_CONTENT_URL}/cache/{thumnail_cache_path}"
                )

            with ProcessPoolExecutor(1) as process_executor:
                await loop.run_in_executor(
                    process_executor,
                    content_manager.cache_thumbnail,
                    path,
                    config.THUMBNAIL_CACHE_PATH,
                )
            return web.HTTPFound(
                f"{config.STATIC_CONTENT_URL}/cache/{thumnail_cache_path}"
            )
        else:
            optional_params = [
                int(request.query["width"]),
                int(request.query["height"]),
                request.query["mode"],
            ]
            with ProcessPoolExecutor(1) as process_executor:
                data = await loop.run_in_executor(
                    process_executor,
                    content_manager.get_thumbnail,
                    path,
                    *optional_params,
                )
        return web.Response(body=data[0], content_type=data[1])
    except FileNotFoundError as e:
        raise HTTPNotFound()
    except PermissionError as e:
        raise HTTPForbidden()
    except (ValueError, TypeError) as e:

        raise HTTPBadRequest(reason=e)
    except cv2.error as e:
        logging.error(e)
        raise HTTPInternalServerError(reason="Opencv cannot handle this request")
    except Exception:
        raise
        raise HTTPInternalServerError


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
        logging.error(e)
        raise HTTPInternalServerError()


async def authorized(request):
    """Authentication status endpoint handler.
    If a request hasn't been rejected by a middleware it means
    a request is authorized

    :param request: request
    :type request: class: `aiohttp.web.BaseRequest`
    :return: 200 status code
    :rtype: class: `aiohttp.web.Response`
    """
    return HTTPOk()
