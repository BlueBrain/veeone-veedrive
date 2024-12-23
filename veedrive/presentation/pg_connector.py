import json
import uuid

import asyncpg

from .. import config
from ..utils.exceptions import CodeException
from .db import DBInterface, prepare_presentation_data


async def create_pg_connector():
    self = PgConnector()
    await self.set_up_connection()
    return self


class PgConnector(DBInterface):
    def __init__(self):
        self.conn = None

    async def set_up_connection(self):
        self.conn = await asyncpg.connect(
            database=config.DB_NAME,
            user=config.DB_USERNAME,
            host=config.DB_HOST,
            password=config.DB_PASSWORD,
        )

    async def get_presentation(self, presentation_id: str = None, presentation_name: str = None, presentation_folder: str = None,
    ):
        sql_base = "SELECT data ::jsonb FROM presentations"
        if presentation_id:
            presentation_id = uuid.UUID(presentation_id)
            sql_string = f"{sql_base} WHERE data ::jsonb ->> 'id' = '{presentation_id}';"
        if presentation_name:
            if presentation_folder:
                sql_string = f"{sql_base} WHERE data ::jsonb ->> 'name' = '{presentation_name}' AND data ::jsonb ->> 'folder' = '{presentation_folder}';"
            else:
                sql_string = f"{sql_base} WHERE data ::jsonb ->> 'name' = '{presentation_name}' AND data ::jsonb ->> 'folder' IS NULL;"
        result = await self.conn.fetchrow(sql_string)
        if not result:
            return None
        else:
            return json.loads(result[0])

    async def get_presentation_versions(self, presentation_id: str):
        sql_string = (
            f"SELECT data ::jsonb FROM archived_presentations WHERE data ::jsonb ->> 'id' = "
            f"'{presentation_id}';"
        )
        results = await self.conn.fetch(sql_string)
        return [json.loads(result[0]) for result in results]

    async def list_presentations(self, folder=None):
        folder_filter_string = (
            f"WHERE data::jsonb ->> 'folder' = '{folder}'"
            if folder
            else "WHERE NOT data ::jsonb ? 'folder' OR data::jsonb ->> 'folder' IS NULL "
        )
        sql_string = f"SELECT data ::jsonb FROM presentations {folder_filter_string} \
                       ORDER BY data ::jsonb ->> 'savedAt' DESC LIMIT 1000;"

        full_list = [
            json.loads(result[0]) for result in await self.conn.fetch(sql_string)
        ]
        return list(map(prepare_presentation_data, full_list))

    async def save_presentation_to_storage(self, presentation_data: dict):
        existing_presentation = await self.get_presentation(presentation_data["id"])
        try:
            presentation_folder = presentation_data["folder"]
        except KeyError:
            presentation_folder = None

        if existing_presentation:
            print("existing with same ID", flush=True)
            await self._archive_presentation(existing_presentation)
            await self.delete_presentation(presentation_data["id"])

        if not existing_presentation:
            existing_presentation_with_same_name = await self.get_presentation(
                presentation_name=presentation_data["name"],
                presentation_folder=presentation_folder,
            )
            if existing_presentation_with_same_name:
                print("existing with different ID and same name", flush=True)
                raise CodeException(
                    10,
                    f'{presentation_data["name"]} already exists in folder: {presentation_folder}',
                )

        sql_string = f"INSERT INTO presentations (data) VALUES ('{json.dumps(presentation_data)}') RETURNING id;"
        return await self.conn.execute(sql_string)

    async def delete_presentation(self, presentation_id: str):
        sql_string = f"DELETE from presentations WHERE data ::jsonb ->> 'id'  =  '{presentation_id}' ;"
        return await self.conn.execute(sql_string)

    async def create_folder(self, folder_name: str):
        sql_string = f"INSERT INTO folders(name) VALUES ('{folder_name}') ;"
        try:
            await self.conn.execute(sql_string)
        except asyncpg.exceptions.UniqueViolationError:
            raise Exception("Folder already exists")

    async def remove_folder(self, folder_name: str):
        sql_string = f"DELETE FROM folders where name = '{folder_name}' RETURNING * ;"
        res = await self.conn.fetchval(sql_string)
        if not res:
            raise Exception("Specified folder does not exist")

    async def list_folders(self):
        sql_string = f"SELECT name from folders;"
        results = await self.conn.fetch(sql_string)
        return [(result[0]) for result in results]

    async def _archive_presentation(self, presentation_data: dict):
        sql_string = f"INSERT INTO archived_presentations (data) VALUES ('{json.dumps(presentation_data)}') RETURNING id;"
        return await self.conn.execute(sql_string)
