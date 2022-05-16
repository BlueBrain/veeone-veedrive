import argparse
import asyncio
import logging

from aiohttp import web

from . import config, server
from .content import fs_manager, utils
from .utils import logger, sentry

parser = argparse.ArgumentParser(description="websocket proxy application")
parser.add_argument(
    "--port", dest="port", type=int, default=config.DEFAULT_PORT, help="port to bind to"
)

parser.add_argument(
    "--address",
    dest="address",
    type=str,
    help="address to bind to",
    default=config.DEFAULT_HOST,
)
parser.add_argument(
    "--origin-auth",
    dest="origin_auth",
    action="store_true",
    help="use host based auth",
    default=config.USE_ORIGIN_AUTH,
)


args = parser.parse_args()
config.USE_ORIGIN_AUTH = args.origin_auth


def get_middlewares():
    middlewares = []
    if config.USE_ORIGIN_AUTH:
        from .auth.middlewares import origin_based_auth
        middlewares.append(origin_based_auth)
        logging.info(
            f"Adding origin based authentication with following whitelist: {config.ORIGIN_WHITELIST}"
        )
    return middlewares


async def start_app():

    if config.ENVIRONMENT:
        sentry.set_up()

    app = web.Application(middlewares=get_middlewares())
    app.router.add_routes(
        [
            web.get("/ws", server.handle_ws),
            web.get("/content/thumb/{path:[^{}]+}", server.handle_thumbnail_request),
            web.get(
                "/content/scaled/{path:[^{}]+}", server.handle_scaled_image_request
            ),
            web.static("/static", config.SANDBOX_PATH),
            web.get("/authorized", server.authorized),
        ]
    )
    app_runner = web.AppRunner(app, access_log=None)
    await app_runner.setup()

    loop.create_task(fs_manager.purge_search_results())
    utils.create_cache_subfolders(config.THUMBNAIL_CACHE_PATH)

    tcp_site = web.TCPSite(app_runner, args.address, args.port)
    logging.error(f"application server running at: {args.address}:{args.port}")
    await tcp_site.start()
    return app_runner, tcp_site


loop = asyncio.get_event_loop()
runner, site = loop.run_until_complete(start_app())

try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(runner.cleanup())
