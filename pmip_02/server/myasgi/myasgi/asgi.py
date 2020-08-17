"""
ASGI config for myasgi project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from myasgi.websocket import websocket_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myasgi.settings')

django_application = get_asgi_application()


async def application(scope, receive, send):
    """
    scope: <class 'dict'> 详细如下

        var connection2 = new WebSocket('ws://127.0.0.1:8000/abc')

        {'type': 'websocket',
        'path': '/abc',
        'raw_path': b'/abc',
        'headers': [(b'host', b'127.0.0.1:8000'), (b'upgrade', b'WebSocket'), (b'connection', b'Upgrade'),
                    (b'sec-websocket-version', b'13'), (b'sec-websocket-key', b'2viLa4ZBnF2953ARONVITw=='),
                    (b'accept', b'*/*'), (b'accept-encoding', b'gzip, deflate'), (b'user-agent', b'Python/3.8 aiohttp/3.6.2')],
        'query_string': b'',
        'client': ['127.0.0.1', 47220],
        'server': ['127.0.0.1', 8000],
        'subprotocols': [],
        'asgi': {'version': '3.0'}}

    receive: <class 'method'>
        <bound method Queue.get of <Queue at 0x7f92b14df5b0 maxsize=0 _queue=[{'type': 'websocket.connect'}] tasks=1>>
    send: <class 'function'>
        <function Server.create_application.<locals>.<lambda> at 0x7f28268f8e50>
    """
    if scope['type'] == 'http':
        # Let Django handle HTTP requests
        await django_application(scope, receive, send)

    elif scope['type'] == 'websocket':
        # We'll handle Websocket connections here
        await websocket_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")