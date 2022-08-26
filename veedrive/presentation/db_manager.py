from .pg_connector import create_pg_connector

db = None


async def get_db():
    global db
    if db:
        return db
    return await create_pg_connector()
