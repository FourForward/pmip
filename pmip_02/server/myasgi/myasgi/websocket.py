# websocket.py

import json
import re

from django.conf import settings


async def websocket_application(scope, receive, send):
    # 主函数
    result = await authentication(scope)
    await method_dict[result](scope, receive, send)


async def bypmip(scope, receive, send):
    """
    代理IP服务器逻辑：将宿主机IP做键，websocket对象作值，存入pmip_dict字典，如果该键已经存在，则拒绝连接，断开连接时删除该键值对
    循环等待接收代理IP服务器的消息（这个消息包含爬虫返回的信息在内），再将该消息转发给提出此需求的客户
    """
    while True:
        event = await receive()
        if event['type'] == 'websocket.connect': # 请求连接分支
            ip = scope['client'][0]
            if not pmip_dict.get(ip, ''):
                pmip_dict[ip] = [scope, receive, send]
                for item in my_url_dict.values():
                    item.append(ip)  # 这里会不会出问题？需不需要加锁
                await send({'type': 'websocket.accept'})
            else:
                await send({'type': 'websocket.no'})

        elif event['type'] == 'websocket.receive': # 收发数据分支
            # 判断这条消息是给哪个客户的，进行选择发送
            # print(event)
            # >>> {'type': 'websocket.receive', 'bytes': b'user=127.0.0.1:40766,text=\n<!doctype html>\n\n<html>\n…………}
            message = event['bytes']
            # >>> b'user=127.0.0.1:40766,text=\n<!doctype html>\n\n<html>\n…………
            user = re.search(rb'user=(?P<IP>.*?),text', message, re.S).group('IP').decode()
            text = re.search(rb',text=(?P<text>.*)',message,re.S).group('text')
            if target_send := clien_dict.get(user,None)[-1]:
                await target_send({'type': 'websocket.send', 'bytes': text})

        elif event['type'] == 'websocket.disconnect': # 断开连接分支
            try:
                del pmip_dict[ip]
            except Exception as e:
                pass
            print('断开连接')
            break


async def byclien(scope, receive, send):
    """
    负责接收客户发送过来的爬虫语句，将其按顺序转发给代理IP
        转发逻辑：客户发送的消息包含域名地址，我们提取主域名，为其建立一个列表，其中包含所有代理IP服务器的 键 ，
        每次弹出对应域名列表头部的一个代理IP，将其压入尾部，向该代理IP 发送消息，视为一次代理访问
    """
    while True:
        event = await receive()
        if event['type'] == 'websocket.connect':
            # 将客户的IP+端口存入字典中，同一个IP 可能会有多个客户同时存在,所以加上端口号
            ip = scope['client'][0] + ':' + str(scope['client'][1])
            clien_dict[ip] = [scope, receive, send]
            await send({'type': 'websocket.accept'})
        elif event['type'] == 'websocket.receive':
            # 提取主域名,判断该域名列表是否存在，不存在则，建立该域名的列表
            # 该正则可以提取域名或IP地址+端口号
            url = re.findall(r'.*\.\w+\.\w+:?\w*', json.loads(event['text'])['url'])[0]
            if not my_url_dict.get(url, None):
                my_url_dict[url] = list(pmip_dict.keys())

            # 弹出该列表首位，并压入尾部
            url_list = my_url_dict[url]
            while True:
                pmip = url_list.pop(0)
                # 提取代理IP的发送接口，发送代理请求
                try:
                    pmip_send = pmip_dict[pmip][-1]
                except Exception as e:
                    # 代理失效如何处理:再弹出列表第一个代理IP ，直至该代理IP 存在
                    print('pmip已失去连接')
                else:
                    url_list.append(pmip)
                    await pmip_send({'type': 'websocket.send', 'text': json.dumps({'user': ip, 'text': event['text']})})
                    break


        elif event['type'] == 'websocket.disconnect':
            try:
                del clien_dict[ip]
            except Exception as e:
                pass
            break


async def byover(scope, receive, send):
    return None


async def mysend(send, message):
    """
        发送消息
    """
    await send({'type': 'websocket.send', 'text': message})


async def authentication(scope):
    """
    识别来者是代理服务器还是客户端
    """
    headers = dict(scope['headers'])
    if headers.get(b'status', None) == b'pmip':
        return 'pmip'
    if headers.get(b'status', None) == b'clien' and headers.get(b'key', None) == settings.KEY.encode():
        return 'clien'
    return 'over'


pmip_dict = {}  # 存储代理服务器的连接对象
clien_dict = {}  # 存储客户的连接对象
my_url_dict = {}  # 存储每一个主域名下的代理IP顺序列表
method_dict = {'pmip': bypmip, 'clien': byclien, 'over': byover}
