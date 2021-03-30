from ..utils import jsonrpc
from ..utils.asynchro import run_async
from . import content_manager, fs_manager


@jsonrpc.validate_jsonrpc(required_param="path")
async def request_image(data):
    """Handler for RequestImage JSON-RPC method. Provides URLs of an image."""
    path = data["params"]["path"]
    client_size = None

    try:
        client_size = data["params"]["clientSize"]
    except KeyError:
        pass

    obj = content_manager.get_image_urls(path, client_size)
    return jsonrpc.prepare_response(data, obj)


@jsonrpc.validate_jsonrpc(required_param="path")
async def request_file(data):
    """Provides URL of a file or agreed error code"""

    path = data["params"]["path"]

    obj = content_manager.get_file_urls(path)
    return jsonrpc.prepare_response(data, obj)


@jsonrpc.validate_jsonrpc(required_param="path")
async def list_directory(data):
    """Handler for RequestFile JSON-RPC method. Lists content of specified directory"""

    path = data["params"]["path"]
    obj = await run_async(fs_manager.list_directory, path)
    return jsonrpc.prepare_response(data, obj)


@jsonrpc.validate_jsonrpc(required_param="name")
async def search(data):
    """Handler for RequestFile JSON-RPC method. Lists content of specified directory"""

    name = data["params"]["name"]
    obj = await run_async(fs_manager.sarch_file_system, name)
    return jsonrpc.prepare_response(data, obj)
