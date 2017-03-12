#!/usr/bin/env python
# coding: utf-8
'''
    开始干活了。。。
'''
from wechat.wechatclient import WeChatClient
import json

if __name__ == '__main__':
    we = WeChatClient()
    we.get_uuid()
    we.get_qrcode()
    we.do_login()
    we.login_info_init()
    we.open_login_statusnotify()
    we.login_get_contact()
    we.login_get_extra_group()
    we.do_server_sync()
    we.get_sync_key()
    we.check_server_sync()
