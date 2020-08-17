from django.http import HttpResponse
from django.conf import settings
import requests


def agency(request):
    """
    代理IP服务器主程序
    转发请求并返回响应
    :param request:
    :return:
    """
    data = eval(request.POST.get('data', '')) if request.POST.get('username','') == settings.USERNAME and request.POST.get('password', '') == settings.PASSWORD else ''

    return HttpResponse(data)
