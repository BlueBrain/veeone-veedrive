import copy
import json
import logging
import uuid

import motor.motor_asyncio
import pymongo

from .. import config
from ..utils.exceptions import CodeException

logger = logging.getLogger(__name__)

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(config.DB_HOST, config.DB_PORT)
db = mongo_client[config.DB_NAME]
archive_collection = db.scene_collection_archive
scene_collection = db.scene_collection


async def get_scene(name):
    try:
        return await _find_scene(name)
    except CodeException:
        raise
    # TODO REMOVE?
    except Exception as e:
        raise CodeException(config.SCENE_DB_ISSUE, f"execution error: {e}")


async def get_scene_versions(name):
    try:
        scenes = []
        cursor = archive_collection.find({"name": name})

        for scene in await cursor.to_list(length=100):
            scenes.append(scene)
        return scenes
    # TODO REMOVE?
    except Exception as e:
        raise CodeException(config.SCENE_DB_ISSUE, f"execution error: {e}")


async def get_scenes():
    try:
        scenes = []
        cursor = scene_collection.find()
        for scene in await cursor.to_list(length=100):
            scenes.append(scene)
        return scenes
    # TODO REMOVE?
    except Exception as e:
        raise CodeException(config.SCENE_DB_ISSUE, f"execution error: {e}")


async def save_scene(scene):
    try:
        found = await _find_scene(scene.name)
        await _archive_scene(found)
        # TODO rather update ?
        await scene_collection.delete_one(found)
    except CodeException as e:
        if e.code == config.SCENE_NOT_FOUND:
            pass
    finally:
        await scene_collection.insert_one(json.loads(scene.serialize()))


async def delete_scene(name):
    try:
        found = await _find_scene(name)
        await scene_collection.delete_one(found)
    except CodeException:
        raise
    # TODO REMOVE?
    except Exception as e:
        raise CodeException(config.SCENE_DB_ISSUE, f"execution error: {e}")


async def _find_scene(name):
    found = await scene_collection.find_one({"name": name})
    if found:
        return found
    else:
        raise CodeException(config.SCENE_NOT_FOUND, "presentation not found")


async def _archive_scene(scene):
    to_be_archived = copy.copy(scene)
    to_be_archived["_id"] = str(uuid.uuid4())
    to_be_archived["version"] = await _get_next_version(scene["name"])
    await archive_collection.insert_one(to_be_archived)


async def _get_next_version(scene_name):
    try:
        cursor = archive_collection.find({"name": scene_name})
        cursor.sort("version", pymongo.DESCENDING).limit(1)
        latest = 0
        async for document in cursor:
            latest = document["version"]

    except Exception as e:
        raise e

    return latest + 1
