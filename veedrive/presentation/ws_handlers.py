from ..utils import jsonrpc
from . import presentation_manager
from .presentation import Scene, Topic, Window


async def get_scene(data):
    """Handler for ListScenes JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """

    presentation = await presentation_manager.get_scene(name=data["params"]["name"])
    return jsonrpc.prepare_response(data, presentation)


async def list_scene_versions(data):
    """Handler for SceneVersions JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """

    presentation_versions = await presentation_manager.get_scene_versions(
        name=data["params"]["name"]
    )
    return jsonrpc.prepare_response(data, presentation_versions)


async def list_scenes(data):
    """Handler for ListScenes JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """

    presentation_list = await presentation_manager.get_scenes()
    return jsonrpc.prepare_response(data, presentation_list)


async def save_scene(data):
    """Handler for SaveScene JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """
    topics = []
    scene_param = data["params"]["presentation"]
    for t in scene_param["topics"]:
        windows = []
        for w in t["windows"]:
            window = Window.create_from_json(w)
            windows.append(window)
        topic = Topic(t["name"], windows)
        topics.append(topic)

    new_scene = Scene(scene_param["name"], topics)
    await presentation_manager.save_scene(new_scene)
    return jsonrpc.prepare_response(data, 0)


async def delete_scene(data):
    """Handler for DeleteScene JSON-RPC method.

    :param data: JSON-RPC object
    :type data: dict
    :return: JSON-RPC object
    :rtype: dict
    """
    await presentation_manager.delete_scene(data["params"]["name"])
    return jsonrpc.prepare_response(data, 0)
