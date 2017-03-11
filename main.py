#!/usr/bin/env python
# coding: utf-8
'''
    开始干活了。。。
'''
from wechat.wechatclient import WeChatClient

if __name__ == '__main__':
    we = WeChatClient()
    we.get_uuid()
    we.get_qrcode()
    we.do_login()
