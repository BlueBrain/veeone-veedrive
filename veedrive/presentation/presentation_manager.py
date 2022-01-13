import copy
import logging
import uuid

import motor.motor_asyncio
import pymongo
from pymongo.collection import Collection

from .. import config
from ..utils.exceptions import CodeException

logger = logging.getLogger(__name__)

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(config.DB_HOST, config.DB_PORT)
db = mongo_client[config.DB_NAME]
archive_collection = db.presentation_archive_collection
presentation_collection = db.presentation_collection


async def get_presentation(presentation_id: str):
    try:
        return await _get_presentation_by_id(presentation_id)
    except CodeException:
        raise
    # TODO REMOVE?
    except Exception as e:
        raise CodeException(config.PRESENTATION_DB_ISSUE, f"execution error: {e}")


async def get_presentation_versions(presentation_id: str):
    try:
        presentation_list = []
        cursor = archive_collection.find({"id": presentation_id})
        for presentation in await cursor.to_list(length=100):
            presentation_list.append(presentation)
        return presentation_list
    except Exception as e:
        raise CodeException(config.PRESENTATION_DB_ISSUE, f"execution error: {e}")


LIST_PRESENTATIONS_EXPOSE_ATTRIBUTES = [
    "id",
    "name",
    "createdAt",
    "updatedAt",
    "savedAt",
]


def _prepare_presentation_data(item):
    return {key: item.get(key) for key in LIST_PRESENTATIONS_EXPOSE_ATTRIBUTES}


async def get_presentations():
    try:
        presentation_count = await presentation_collection.count_documents({})
        cursor = presentation_collection.find().sort([("savedAt", pymongo.DESCENDING)])
        presentation_list = map(
            _prepare_presentation_data, await cursor.to_list(length=100)
        )
        logger.debug(f"Found presentations: {presentation_list}")
    # TODO REMOVE?
    except Exception as e:
        raise CodeException(config.PRESENTATION_DB_ISSUE, f"execution error: {e}")

    return {
        "results": list(presentation_list),
        "count": presentation_count,
    }


async def _archive_presentation(presentation: Collection):
    presentation_to_archive = copy.copy(presentation)
    await archive_collection.insert_one(presentation_to_archive)


async def save_presentation_to_storage(presentation_data: dict):
    try:
        existing_presentation: Collection = await _get_presentation_by_id(
            presentation_data["id"]
        )
        await _archive_presentation(existing_presentation)
        await presentation_collection.delete_one(existing_presentation)
    except CodeException as e:
        if e.code == config.PRESENTATION_NOT_FOUND:
            pass
    finally:
        data_to_save = copy.deepcopy(presentation_data)
        data_to_save["id"] = uuid.UUID(presentation_data["id"])
        return await presentation_collection.insert_one(data_to_save)


async def _get_presentation_by_id(presentation_id_hex: str):
    presentation_id = uuid.UUID(presentation_id_hex)
    existing_presentation: Collection = await presentation_collection.find_one(
        {"id": presentation_id}
    )
    if existing_presentation:
        return existing_presentation
    else:
        raise CodeException(config.PRESENTATION_NOT_FOUND, "Presentation not found")


async def delete_presentation(presentation_id: str):
    try:
        found = await _get_presentation_by_id(presentation_id)
        await presentation_collection.delete_one(found)
    except CodeException:
        raise
    except Exception as e:
        raise CodeException(config.PRESENTATION_DB_ISSUE, f"execution error: {e}")


async def purge_presentations():
    return await presentation_collection.delete_many({})
