import asyncio
from concurrent.futures import ProcessPoolExecutor


async def run_async(func, *args):
    executor = ProcessPoolExecutor()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)
