import environ
from core.loggers import get_logger

env = environ.Env()

host = env.str('WS_HOST', '0.0.0.0')
port = env.int('WS_PORT', 8001)
redis_host = env.str('REDIS_HOST', '127.0.0.1')
redis_port = env.int('REDIS_PORT', 6380)
redis_db = env.int('REDIS_DB', 0)
redis_password = env.str('REDIS_PASSWORD')
secret = env.str('SECRET_KEY')

logger = get_logger('websockets')
