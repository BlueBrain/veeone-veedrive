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

    async def get_presentation(self, presentation_id: str):
        presentation_id = uuid.UUID(presentation_id)
        sql_string = f"SELECT data ::jsonb FROM presentations WHERE data ::jsonb ->> 'id' = '{presentation_id}';"

        result = await self.conn.fetchrow(sql_string)
        if not result:
            raise CodeException(config.PRESENTATION_NOT_FOUND, "Presentation not found")
        else:
            return json.loads(result[0])

    async def get_presentation_versions(self, presentation_id: str):
        sql_string = (
            f"SELECT data ::jsonb FROM archived_presentations WHERE data ::jsonb ->> 'id' = "
            f"'{presentation_id}';"
        )
        results = await self.conn.fetch(sql_string)
        return [json.loads(result[0]) for result in results]

    async def get_presentations(self):
        sql_string = f"SELECT data ::jsonb FROM presentations ORDER BY data ::jsonb ->> 'savedAt' DESC LIMIT 1000;"

        full_list = [
            json.loads(result[0]) for result in await self.conn.fetch(sql_string)
        ]
        return list(map(prepare_presentation_data, full_list))

    async def save_presentation_to_storage(self, presentation_data: dict):
        try:
            existing_presentation = await self.get_presentation(presentation_data["id"])
            await self._archive_presentation(existing_presentation)
            await self.delete_presentation(presentation_data["id"])
        except CodeException as e:
            if e.code == config.PRESENTATION_NOT_FOUND:
                pass
        finally:
            sql_string = f"INSERT INTO presentations (data) VALUES ('{json.dumps(presentation_data)}') RETURNING id;"
            return await self.conn.execute(sql_string)

    async def delete_presentation(self, presentation_id: str):
        sql_string = f"DELETE from presentations WHERE data ::jsonb ->> 'id'  =  '{presentation_id}' ;"
        return await self.conn.execute(sql_string)

    async def purge_presentations(self):
        sql_string = f"DELETE from presentations;"
        return await self.conn.execute(sql_string)

    async def _archive_presentation(self, presentation_data: dict):
        sql_string = f"INSERT INTO archived_presentations (data) VALUES ('{json.dumps(presentation_data)}') RETURNING id;"
        return await self.conn.execute(sql_string)
