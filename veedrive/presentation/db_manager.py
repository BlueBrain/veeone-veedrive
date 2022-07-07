from veedrive.config import DB_TYPE

from .mongo_connector import MongoConnector
from .pg_connector import create_pg_connector

db = None


async def get_db():
    global db
    if db:
        return db
    db = (
        MongoConnector()
        if DB_TYPE == "mongo"
        else await create_pg_connector()
        if DB_TYPE == "postgres"
        else None
    )
    return db
