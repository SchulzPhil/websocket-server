import asyncio
import server

from core import settings
from core.handlers import DefaultHandler
from core.protocols import QueryParamsProtocol

handler = DefaultHandler(
    settings.logger,
    settings.redis_host,
    settings.redis_port,
    settings.redis_password,
    0
)


async def main():
    await handler.startup()
    async with server.serve(
            handler,
            settings.host,
            settings.port,
            create_protocol=QueryParamsProtocol
    ):
        return await asyncio.Future()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()

