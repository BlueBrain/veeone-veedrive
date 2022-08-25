from ..utils import jsonrpc
from . import db_manager


async def get_presentation(data):
    """Handler for ListScenes JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """

    presentation = await (await db_manager.get_db()).get_presentation(
        presentation_id=data["params"]["id"]
    )
    return jsonrpc.prepare_response(data, presentation)


async def list_scene_versions(data):
    """Handler for SceneVersions JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """

    presentation_versions = await (await db_manager.get_db()).get_presentation_versions(
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

    try:
        folder = data["params"]["folder"]
    except KeyError:
        folder = None
    presentation_list = await (await db_manager.get_db()).list_presentations(folder)
    response = {
        "results": presentation_list,
        "count": len(presentation_list),
    }
    return jsonrpc.prepare_response(data, response)


async def save_presentation(data):
    """Handler for SaveScene JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """
    presentation_data = data["params"]
    inserted_id: str = await (await db_manager.get_db()).save_presentation_to_storage(
        presentation_data
    )
    return jsonrpc.prepare_response(data, "ok")


async def delete_presentation(data):
    """Handler for DeleteScene JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """
    await (await db_manager.get_db()).delete_presentation(data["params"]["id"])
    return jsonrpc.prepare_response(data, 0)


async def purge_presentations(data):
    await (await db_manager.get_db()).purge_presentations()
    return jsonrpc.prepare_response(data, "OK")


async def create_folder(data):
    """Handler for CreateFolder JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """
    folder = data["params"]["folder"]
    try:
        await (await db_manager.get_db()).create_folder(folder)
        return jsonrpc.prepare_response(data, 'OK')
    except Exception as e:
        return jsonrpc.prepare_error(data, 701, str(e))


async def remove_folder(data):
    """Handler for RemoveFolder JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """
    folder = data["params"]["folder"]

    presentation_list = await (await db_manager.get_db()).list_presentations(folder)
    if presentation_list:
        return jsonrpc.prepare_error(data, 403, "Cannot remove, folder contains presentations")
    try:
        await (await db_manager.get_db()).remove_folder(folder)
        return jsonrpc.prepare_response(data, 'OK')
    except Exception as e:
        return jsonrpc.prepare_error(data, 400, str(e))


async def list_folders(data):
    """Handler for ListFolders JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """
    folder_list = await (await db_manager.get_db()).list_folders()
    return jsonrpc.prepare_response(data, folder_list)
