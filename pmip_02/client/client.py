import json
import aiohttp
import asyncio
import re

from aiohttp import WSMessage


async def myspider():
    headers = {'status': 'clien', 'key': '123456'}
    target_headers = {'useragent':'la'}
    session = aiohttp.ClientSession(headers=headers)
    async with session.ws_connect('ws://127.0.0.1:8000') as ws:
        await ws.send_json({'headers': target_headers, 'url': 'http://www.baidu.com', 'method': 'get'})
        data = await ws.receive() # type: WSMessage
        print(type(data))
        print(data.data)

asyncio.run(myspider())