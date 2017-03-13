#!/usr/bin/env python
# coding: utf-8
'''
    我们不生产请求，我们只是请求的搬运工。。。
'''
import urllib.request
from urllib.parse import urlencode
import urllib.error
import http.cookiejar

class WeChatWeb:
    '''http请求集合'''
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
        self.refer = 'https://wx2.qq.com/?&lang=zh_CN'
        cookiejar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent), ('Referer', self.refer)]
        urllib.request.install_opener(opener)

    def do_get(self, url, params: dict={}):
        '''构造get请求'''
        if params:
            params = urlencode(params)
            url = url + "?%s" %params
        request = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(request)
            return response.read()
        except urllib.error.HTTPError as err:
            print(err.reason)
        except urllib.error.URLError as err:
            print(err.reason)
        except Exception:
            import traceback
            print(traceback.format_exc())
        return ''

    def do_post(self, url, data: str, isJson=False, params: dict={}):
        '''构造post请求'''
        if params:
            params = urlencode(params)
            url = url + "?%s" %params
        request = urllib.request.Request(url=url, data=data.encode(encoding="UTF-8"))
        if isJson:
            request.add_header('ContentType', 'application/json; charset=UTF-8')
        try:
            response = urllib.request.urlopen(request)
            return response.read()
        except urllib.error.HTTPError as err:
            print(err.reason)
        except urllib.error.URLError as err:
            print(err.reason)
        except Exception:
            import traceback
            print(traceback.format_exc())
        return ''
