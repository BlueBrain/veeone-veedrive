from aiohttp.web import middleware, Response
from .. import config


@middleware
async def origin_based_auth(request, handler):
    source = request.headers.get('X-FORWARDED-FOR', None)
    if not source:
        source = request.remote
    if source in config.ORIGIN_WHITELIST:
        return await handler(request)
    return Response(status=403)
