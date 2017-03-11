#!/usr/bin/env python
# coding: utf-8
'''
    我们不生产消息，我们只是消息的搬运工。。。
'''
import time
import re
import sys
import os
import subprocess
import random
import json
import xml.dom.minidom
from wechat.wechatweb import WeChatWeb



class WeChatClient:
    '''山寨版微信客户端'''
    def __str__(self):
        description = ''
        return description

    def __init__(self):
        self.uuid = ''
        self.lang = 'zh_CN'
        self.appid = 'wx782c26e4c19acffb'
        self.skey = ''
        self.sid = ''
        self.uin = ''
        self.pass_ticket = ''
        self.device_id = 'e' + str(random.randint(1e14, 1e15-1))
        self.synckey = ''
        self.joined_synckey = ''
        self.user = ''
        self.uuid_url = 'https://login.weixin.qq.com/jslogin'
        self.login_result_url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login'
        self.login_redirect_url = ''
        self.login_base_url = ''
        self.qrcode_url = 'https://login.weixin.qq.com/qrcode/'
        self.genarate_qrcode_url = 'https://login.weixin.qq.com/l/'
        self.new_login_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage'


    def get_uuid(self):
        '''获取uuid--登录需要'''
        params = {
            'appid': self.appid,
            'redirect_uri': self.login_result_url,
            'fun': 'new',
            'lang': self.lang,
            '_': int(time.time())
        }
        response = WeChatWeb().do_get(self.uuid_url, params).decode("UTF-8")
        if not response:
            return False
        reg = r'window.QRLogin.code = (\d{3}); window.QRLogin.uuid = "(\S+?)";'
        result = re.search(reg, response)
        if result:
            response_code = result.group(1)
            self.uuid = result.group(2)
            return response_code == '200'
        return False

    def get_qrcode(self):
        '''根据uuid获取登录的二维码'''
        response = WeChatWeb().do_get(self.qrcode_url + self.uuid)
        if not response:
            return False
        print("请用手机微信扫描二维码进行登录。。。")
        file_path = r'.\loginQrcode.jpg'
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "wb") as qrcode_jpg:
            qrcode_jpg.write(response)
        try:
            if 'win' in sys.platform:
                os.startfile(file_path)
            if 'darwin' in sys.platform:
                subprocess.call(["open", file_path])
            return True
        except Exception:
            pass
        try:
            import qrcode
            console_qrcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
            console_qrcode.add_data(self.genarate_qrcode_url + self.uuid)
            console_qrcode.make(fit=True)
            console_qrcode.print_ascii(invert=True)
            print("如果打印成乱码，请用浏览器打开链接：" + self.qrcode_url + self.uuid + " 扫码登录。。。")
            return True
        except ImportError:
            print("请安装qrcode库后重试，例如使用: pip install qrcode\n\n\
             -----------------我是分隔线-----------------\n\n")
            return False

    def do_login(self):
        '''扫码登录，获取登录结果'''
        params = {
            'loginicon': 'true',
            'tip': 1,
            'uuid': self.uuid,
            '_': str(time.time())
        }
        response = WeChatWeb().do_get(self.login_result_url, params).decode("UTF-8")
        if self.judge_login_result(response):
            return True
        params['tip'] = 0
        for i in range(0, 10):
            response = WeChatWeb().do_get(self.login_result_url, params).decode("UTF-8")
            if self.judge_login_result(response):
                return True
        return False

    def judge_login_result(self, response):
        '''登录请求返回值校验，登录成功则返回聊天页跳转链接'''
        reg = r'window.code=(\d+);'
        result = re.search(reg, response)
        if result:
            login_code = result.group(1)
        if login_code == '200':
            reg = r'window.redirect_uri="(\S+?)";'
            result = re.search(reg, response)
            self.login_redirect_url = result.group(1) + '&fun=new'
            print(self.login_redirect_url)
            self.login_base_url = self.login_redirect_url[:self.login_redirect_url.rfind('/')]
            print(self.login_base_url)
            print(response)
            print('******登录成功******\n')
            return True
        elif login_code == '408':
            print("登录超时,请尽快扫码登录~\n")
            return False
        else:
            print('登录异常。。。\n')
            return False

    def login_info_init(self):
        '''登录成功获取用户相关参数，用于消息收发'''
        response = WeChatWeb().do_get(self.login_redirect_url).decode("UTF-8")
        if not response:
            return False
        xml_response = xml.dom.minidom.parseString(response)
        root = xml_response.documentElement
        nodes = {node.nodeName : node.childNodes[0].data for node in root.childNodes}
        self.skey = nodes['skey']
        self.sid = nodes['wxsid']
        self.uin = nodes['wxuin']
        self.pass_ticket = nodes['pass_ticket']
        data = {
            'Uin': int(self.uin),
            'Sid': self.sid,
            'Skey': self.skey,
            'DeviceID': self.device_id
        }
        data = json.dumps(data)
        params = {
            'lang': self.lang,
            'pass_ticket': self.pass_ticket
        }
        init_data = WeChatWeb().do_post(
            self.login_base_url + '/webwxinit', data, True, params).decode("UTF-8")
        if not init_data:
            return False
        init_data = json.loads(init_data)
        self.synckey = init_data['SyncKey']
        self.user = init_data['User']
        self.joined_synckey = "|".join(
            [str(keyval['Key']) + "_" + str(keyval['Val']) for keyval in self.synckey['List']])
        return init_data['BaseResponse']['Ret'] == 0
