import copy
import logging
import uuid

import motor.motor_asyncio
import pymongo
from pymongo.collection import Collection
from pymongo.results import InsertOneResult

from .. import config
from ..utils.exceptions import CodeException
from .db import DBInterface, prepare_presentation_data

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(config.DB_HOST, config.DB_PORT)
mongo_database = mongo_client[config.DB_NAME]
archive_collection = mongo_database.presentation_archive_collection
presentation_collection = mongo_database.presentation_collection


class MongoConnector(DBInterface):
    async def get_presentation(self, presentation_id: str):
        presentation_id = uuid.UUID(presentation_id)
        existing_presentation: Collection = await presentation_collection.find_one(
            {"id": presentation_id}
        )
        if existing_presentation:
            del existing_presentation["_id"]
            return existing_presentation
        else:
            raise CodeException(config.PRESENTATION_NOT_FOUND, "Presentation not found")

    async def get_presentation_versions(self, presentation_id: str):
        try:
            presentation_id = uuid.UUID(presentation_id)
            presentation_list = []
            cursor = archive_collection.find({"id": presentation_id})
            for presentation in await cursor.to_list(length=100):
                del presentation["_id"]
                presentation_list.append(presentation)
            return presentation_list
        except Exception as e:
            raise CodeException(config.PRESENTATION_DB_ISSUE, f"execution error: {e}")

    async def list_presentations(self):
        try:
            cursor = presentation_collection.find().sort(
                [("savedAt", pymongo.DESCENDING)]
            )
            presentation_list = map(
                prepare_presentation_data, await cursor.to_list(length=100)
            )
            logging.debug(f"Found presentations: {presentation_list}")
        except Exception as e:
            raise CodeException(config.PRESENTATION_DB_ISSUE, f"execution error: {e}")

        return list(presentation_list)

    async def save_presentation_to_storage(self, presentation_data: dict):
        try:
            existing_presentation: Collection = await self.get_presentation(
                presentation_data["id"]
            )
            await self._archive_presentation(existing_presentation)
            await presentation_collection.delete_one(existing_presentation)
        except CodeException as e:
            if e.code == config.PRESENTATION_NOT_FOUND:
                pass
        finally:
            data_to_save = copy.deepcopy(presentation_data)
            data_to_save["id"] = uuid.UUID(presentation_data["id"])
            result: InsertOneResult = await presentation_collection.insert_one(
                data_to_save
            )
            return result.inserted_id

    async def delete_presentation(self, presentation_id: str):
        try:
            found = await self.get_presentation(presentation_id)
            await presentation_collection.delete_one(found)
        except CodeException:
            raise
        except Exception as e:
            raise CodeException(config.PRESENTATION_DB_ISSUE, f"execution error: {e}")

    async def purge_presentations(self):
        return await presentation_collection.delete_many({})

    async def _archive_presentation(self, presentation):
        presentation_to_archive = copy.copy(presentation)
        await archive_collection.insert_one(presentation_to_archive)
