import aiohttp
import asyncio
import json

from aiohttp import WSMsgType


with open('my_server_addr.txt', 'r+') as f:
    server_ip = f.read()
    print('IP:',server_ip)
    if not server_ip:
        ip = input('请输入服务器IP地址:端口 >>>')
        server_ip = f"ws://{ip}"
        f.write(server_ip)


async def myclien():
    headers = {'status': 'pmip'}
    session = aiohttp.ClientSession(headers=headers)
    while True:
        try:
            async with session.ws_connect(server_ip) as ws:
                active = True
                print('连接成功')
                while active:
                    data = await ws.receive()
                    print(data)

                    if data.type is WSMsgType.TEXT:
                        pass
                    elif data.type is WSMsgType.CLOSED:
                        print('准备关闭连接')
                        active = False
                        continue
                    else:
                        continue
                    # WSMessage(type= < WSMsgType.TEXT: 1 >,
                    # data = '{"user": "127.0.0.1:37760", "text": "{\\"headers\\": {}, \\"url\\": \\"http://www.baidu.com\\", \\"method\\": \\"get\\"}"}', extra = '')
                    data = json.loads(data.data)
                    # {'user': '127.0.0.1:37764', 'text': '{"headers": {}, "url": "http://www.baidu.com", "method": "get"}'}
                    message = json.loads(data['text'])
                    rerult = await request_method[message['method']](message)
                    await ws.send_bytes(f"user={data['user']},text=".encode() + rerult)
                else:
                    await ws.close()
                    await asyncio.sleep(5)

        except Exception as e:
            # 若连接断开，或是服务器拒绝建立连接，那么每隔60秒再次请求连接
            print(e, '等待重新连接')
            await asyncio.sleep(60)
            continue


async def myget(message):
    if (headers := message.get('headers', None)) and (url := message.get('url', None)):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url=url) as request:
                result = await request.read()
            return result
    return None


async def mypost(message):
    # session.put('http://httpbin.org/put', data=b'data')
    if (headers := message.get('headers', None)) and (url := message.get('url', None)) and (
            data := message.get('data', None)):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url=url, data=data) as request:
                result = request.read()
            return result
    return None


async def myput(message):
    # session.put('http://httpbin.org/put', data=b'data')
    pass


async def mydelete(message):
    # session.delete('http://httpbin.org/delete')
    pass


async def myoptions(message):
    # session.options('http://httpbin.org/get')
    pass


async def mypatch(message):
    # session.patch('http://httpbin.org/patch', data=b'data')
    pass


request_method = {
    'get': myget,
    'post': mypost,
    'put': myput,
    'delete': mydelete,
    'options': myoptions,
    'patch': mypatch,
}


asyncio.run(myclien())
