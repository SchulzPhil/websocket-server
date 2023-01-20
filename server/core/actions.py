import json

from core.handlers import action


@action('channels:messages')
async def messages(handler, websocket, message, *_, **__):
    message['type'] = 'new_msg'

    if websocket.user == message['receiver']['uuid']:
        await websocket.send(json.dumps(message))


@action('channels:messages:read')
async def messages_read(handler, websocket, message, *_, **__):
    message['type'] = 'read_msg'

    receiver = await handler.get_dialog_opponent(message['chat'], message['user'])

    if websocket.user == receiver:
        await websocket.send(json.dumps(message))


@action('channels:uuid:chatType')
async def new_chat(handler, websocket, message, *_, **__):
    message['type'] = 'create_new_chat'

    if message['chat_type'] == 'D':
        if websocket.user == message['receiver']:
            await websocket.send(json.dumps(message))


@action('channels:chat:uuid:action')
async def user_action(handler, websocket, message, *_, **__):
    message['type'] = 'user_action'

    users = handler.redis.smembers(f'chats:{message["chat"]}:read')

    if websocket.user.encode('utf-8') in users:
        await websocket.send(json.dumps(message))


@action('channels:users:instance:update')
async def user_update(handler, websocket, message, *_, **__):
    if message['uuid'] == websocket.user:
        await websocket.send(json.dumps(message))

