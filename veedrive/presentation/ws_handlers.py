import logging

from pymongo.results import InsertOneResult

from ..utils import jsonrpc
from . import presentation_manager


async def get_presentation(data):
    """Handler for ListScenes JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """

    presentation = await presentation_manager.get_presentation(
        presentation_id=data["params"]["id"]
    )
    del presentation["_id"]
    return jsonrpc.prepare_response(data, presentation)


async def list_scene_versions(data):
    """Handler for SceneVersions JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """

    presentation_versions = await presentation_manager.get_presentation_versions(
        presentation_id=data["params"]["id"]
    )
    return jsonrpc.prepare_response(data, presentation_versions)


async def list_presentations(data):
    """Handler for ListScenes JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """

    response = await presentation_manager.get_presentations()
    return jsonrpc.prepare_response(data, response)


async def save_presentation(data):
    """Handler for SaveScene JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """
    presentation_data = data["params"]
    logging.info(f"presentation_data={type(presentation_data)} => {presentation_data}")
    result: InsertOneResult = await presentation_manager.save_presentation_to_storage(
        presentation_data
    )
    logging.info(
        f"Response from Mongo: {result.inserted_id} ({type(result.inserted_id)})"
    )
    return jsonrpc.prepare_response(data, str(result.inserted_id))


async def delete_presentation(data):
    """Handler for DeleteScene JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """
    await presentation_manager.delete_presentation(data["params"]["id"])
    return jsonrpc.prepare_response(data, 0)


async def purge_presentations(data):
    await presentation_manager.purge_presentations()
    return jsonrpc.prepare_response(data, "OK")
