import argparse
import asyncio
import logging

from aiohttp import web

from . import config, server

logging.basicConfig(level=config.logger_level)
logger = logging.getLogger(__name__)

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

args = parser.parse_args()


async def start_app():
    app = web.Application()
    app.router.add_routes(
        [
            web.get("/ws", server.handle_ws),
            web.get("/content/thumb/{path}", server.handle_thumbnail_request),
            web.get("/content/scaled/{path}", server.handle_scaled_image_request),
            web.static("/static", config.SANDBOX_PATH),
        ]
    )
    app_runner = web.AppRunner(app)
    await app_runner.setup()
    tcp_site = web.TCPSite(app_runner, args.address, args.port)
    logger.info(f"application server running at: {args.address}:{args.port}")
    await tcp_site.start()
    return app_runner, tcp_site


loop = asyncio.get_event_loop()
runner, site = loop.run_until_complete(start_app())

try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(runner.cleanup())
