from ..utils import jsonrpc
from ..utils.asynchro import run_async
from . import content_manager, fs_manager
from .fs_manager import fs_search_results


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
    """Handler for Search JSON-RPC method. Search media path for a file"""
    search_query = data["params"]["name"]

    try:
        starting_path = data["params"]["starting_path"]
        search_id = fs_manager.search_file(search_query, starting_path)
    except KeyError:
        search_id = fs_manager.search_file(search_query)
    except Exception as e:
        return jsonrpc.prepare_error(data, 70, str(e))

    return jsonrpc.prepare_response(data, {"searchId": search_id})


@jsonrpc.validate_jsonrpc(required_param="searchId")
async def get_search_result(data):
    """Handler for SearchResult JSON-RPC method """
    search_id = data["params"]["searchId"]

    try:
        result = fs_search_results[search_id].copy()
        try:
            result.pop("started_at")
            result.pop("finished_at")
        except KeyError:
            pass
        if result["done"]:
            fs_search_results.pop(search_id)
        return jsonrpc.prepare_response(data, result)

    except KeyError as e:
        return jsonrpc.prepare_error(
            data, 69, f"search id {search_id} has not been yet created"
        )
