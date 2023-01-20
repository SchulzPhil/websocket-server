import jwt
import http
from redis import Redis

from server.datastructures import Headers
from server.server import WebSocketServerProtocol

from core import settings


class QueryParamsProtocol(WebSocketServerProtocol):
    query_params: dict
    user: str
    redis: Redis = Redis(
        settings.redis_host,
        settings.redis_port,
        settings.redis_db,
        settings.redis_password
    )

    @staticmethod
    def get_query_params(path: str) -> dict:
        try:
            query = path.split('?')[-1].split('&')
            return dict(map(lambda x: x.split('='), query))
        except ValueError:
            return {}

    def get_user(self, token: str) -> str:
        try:
            payload = jwt.decode(token, settings.secret, algorithms='HS256')
        except jwt.exceptions.DecodeError:
            return ''
        except jwt.exceptions.ExpiredSignatureError:
            return ''
        except jwt.exceptions.ImmatureSignatureError:
            return ''

        if 'user_id' not in payload:
            return ''

        uuid = self.redis.get(f'users:{payload["user_id"]}')

        if not uuid:
            return ''

        return uuid.decode('utf-8')

    async def process_request(self, path: str, request_headers: Headers):
        self.query_params = self.get_query_params(path)

        if 'token' not in self.query_params:
            return http.HTTPStatus.UNAUTHORIZED, [], b"Missing token\n"

        self.user = self.get_user(self.query_params['token'])

        if not self.user:
            return http.HTTPStatus.UNAUTHORIZED, [], b"Invalid token\n"

        return await super().process_request(path, request_headers)

