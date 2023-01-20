import asyncio
import json
from datetime import datetime

import server.exceptions
import logging
import server.exceptions
from redis import Redis


class DefaultHandler:
    redis: Redis
    users: dict = {}

    actions: dict = {}

    def __init__(self, logger: logging.Logger, redis_host: str, redis_port: int, redis_password: str, redis_db: int):
        self.logger = logger
        self.redis = Redis(redis_host, redis_port, redis_db, redis_password)

        self.logger.info(self.actions.__str__())

    async def notify_online_status(self, websocket, status: bool):
        for chat in self.redis.smembers(f'users:{websocket.user}:chats'):
            opponent = await self.get_dialog_opponent(chat.decode('utf-8'), websocket.user)

            for client in self.users:
                if self.users[client] == opponent:
                    try:
                        await client.send(json.dumps({
                            'user': websocket.user, 'is_online': status,
                            'type': 'online_status', 'chat_id': chat.decode('utf-8'),
                            'last_online': self.redis.hget(f'users:{websocket.user}', 'last_online').decode('utf-8')
                        }))
                    except server.exceptions.ConnectionClosedOK:
                        logging.info(f"User status changed: {status} - {websocket.user}")
                        continue

    async def on_connected(self, websocket):
        self.logger.info(f'Connected: {websocket.remote_address}')

        nickname = self.redis.hget(f'users:{websocket.user}', 'email')
        self.logger.info(f'Authorized: {nickname}')

        await self.notify_online_status(websocket, True)

        self.users[websocket] = websocket.user
        self.redis.sadd('users:online', websocket.user)

        self.redis.hset(
            f'users:{websocket.user}',
            'is_online',
            1
        )

    async def on_disconnected(self, websocket):
        self.logger.info(f'Disconnected: {websocket.remote_address}')

        self.redis.srem('users:online', websocket.user)

        await self.notify_online_status(websocket, False)

        self.redis.hset(
            f'users:{websocket.user}',
            'is_online',
            0
        )

        self.redis.hset(
            f'users:{websocket.user}',
            'last_online',
            datetime.now().timestamp()
        )

        self.users.pop(websocket)

    async def is_closed(self, websocket):
        try:
            await asyncio.wait_for(websocket.recv(), timeout=0.0001)
        except server.exceptions.ConnectionClosed:
            return True
        except asyncio.exceptions.TimeoutError:
            return False
        return False

    async def get_dialog_opponent(self, uuid: str, user: str) -> str:
        members = self.redis.smembers("chats:{uuid}:users".format(uuid=uuid))
        members = set(map(lambda x: x.decode('utf8'), members))

        difference = members.difference({user})

        if len(difference) == 1:
            return difference.pop()

        return ''

    async def handle(self, websocket):
        pubsub = self.redis.pubsub()
        pubsub.subscribe(*list(self.actions.keys()))

        while not await self.is_closed(websocket):
            msg = pubsub.get_message()

            if isinstance(msg, dict):
                channel = msg['channel'].decode('utf-8')

                self.logger.info(f'Got message: {msg}')

                if channel in self.actions:
                    if msg['type'] in self.actions[channel]:
                        try:
                            payload = json.loads(msg['data'].decode('utf-8'))
                            await self.actions[channel][msg['type']](self, websocket, payload)
                        except server.exceptions.ConnectionClosed:
                            break

    async def __call__(self, websocket):
        await self.on_connected(websocket)
        await self.handle(websocket)
        await self.on_disconnected(websocket)

    async def startup(self):
        self.redis.delete('users:online')

        for user in self.redis.smembers('users:all'):
            self.redis.hset(
                f'users:{user.decode("utf-8")}',
                'is_online',
                0
            )


def action(channel, type_='message'):
    def wrapper(function):

        if channel not in DefaultHandler.actions:
            DefaultHandler.actions[channel] = {}

        DefaultHandler.actions[channel][type_] = function

        return function

    return wrapper
