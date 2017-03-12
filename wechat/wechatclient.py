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
        self.synckey = {}
        self.joined_synckey = ''
        self.user = {}
        self.uuid_url = 'https://login.weixin.qq.com/jslogin'
        self.login_result_url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login'
        self.login_redirect_url = ''
        self.login_base_url = ''
        self.qrcode_url = 'https://login.weixin.qq.com/qrcode/'
        self.genarate_qrcode_url = 'https://login.weixin.qq.com/l/'
        #self.new_login_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage'
        self.base_request_params = {}
        '''这个特殊账号列表来自于网上，做了下去重，但是还是觉得有些可能是多余的。。。'''
        self.known_special_accounts = ['newsapp', 'filehelper', 'weibo',\
         'qqmail', 'fmessage', 'tmessage', 'qmessage', 'qqsync', 'floatbottle',\
         'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp', 'blogapp',\
         'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp', 'voip', 'blogappweixin',\
         'brandsessionholder', 'weixinreminder', 'wxitil',\
         'userexperience_alarm', 'notification_messages']
        '''通讯录里的联系人'''
        self.saved_member_count = 0
        self.saved_member_list = []
        self.contact_list = []
        '''通讯录里保存的群聊'''
        self.saved_group_list = []
        self.group_list = []
        self.public_account_list = []
        self.special_account_list = []
        self.init_data = {}
        self.batch_account_list = []
        self.backup_host_list = [\
            'wx2.qq.com',\
            'wx8.qq.com',\
            'webpush.wx8.qq.com',\
            'web2.wechat.com',\
            'webpush.web2.wechat.com',\
            'webpush.web.wechat.com',\
            'webpush.weixin.qq.com',\
            'webpush.wechat.com',\
            'webpush1.wechat.com',\
            'webpush2.wechat.com',\
            'webpush2.wx.qq.com',\
            'webpush.wx.qq.com',\
            'webpush.wx2.qq.com'\
            ]
        self.sync_url = ''
        self.web_client = WeChatWeb()

    def get_unix_timestamp(self):
        return int(round(time.time() * 1000))

    def get_complement_code(self, num):
        return (~num)&0xFFFFFFFF

    def get_uuid(self):
        '''
        获取uuid--登录需要
        url: https://login.weixin.qq.com/jslogin
        method: get
        parameters: appid, redirect_uri, fun, lang, _
        '''
        params = {
            'appid': self.appid,
            'redirect_uri': self.login_result_url,
            'fun': 'new',
            'lang': self.lang,
            '_': self.get_unix_timestamp()
        }
        response = self.web_client.do_get(self.uuid_url, params).decode("UTF-8")
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
        '''
        根据uuid获取登录的二维码
        url: https://login.weixin.qq.com/qrcode/ + uuid
        method: get
        parameters:
        二维码实际内容: https://login.weixin.qq.com/l/ + uuid
        '''
        response = self.web_client.do_get(self.qrcode_url + self.uuid)
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
            print('请安装qrcode库后重试，例如使用: pip install qrcode\n\n\
             -----------------我是分隔线-----------------\n\n')
            return False

    def do_login(self):
        '''
        扫码登录，获取登录结果
        url: https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login
        method: get
        parameters: loginicon, tip, uuid, _, r
        '''
        params = {
            'loginicon': 'true',
            'tip': 1,
            'uuid': self.uuid,
            'r': self.get_complement_code(self.get_unix_timestamp()),
            '_': self.get_unix_timestamp()
        }
        response = self.web_client.do_get(self.login_result_url, params).decode("UTF-8")
        if self.judge_login_result(response):
            return True
        params['tip'] = 0
        for i in range(0, 10):
            time.sleep(0.5)
            response = self.web_client.do_get(self.login_result_url, params).decode("UTF-8")
            if self.judge_login_result(response):
                return True
        return False

    def judge_login_result(self, response):
        '''
        登录请求返回值校验，登录成功则返回聊天页跳转链接
        '''
        reg = r'window.code=(\d+);'
        result = re.search(reg, response)
        if result:
            login_code = result.group(1)
        if login_code == '200':
            reg = r'window.redirect_uri="(\S+?)";'
            result = re.search(reg, response)
            self.login_redirect_url = result.group(1) + '&fun=new'
            self.login_base_url = self.login_redirect_url[:self.login_redirect_url.rfind('/')]
            print('******登录成功******\n')
            return True
        elif login_code == '408':
            print("登录超时,请尽快扫码登录~\n")
            return False
        elif login_code == '201':
            '''扫码成功，但还需要再请求获取链接'''
            print("扫码成功。。。\n")
            return False
        else:
            print('登录异常。。。\n')
            return False

    def login_info_init(self):
        '''
        登录成功后获取用户相关参数，用于后续所有操作
        1.
        url: 登录情况查询接口返回的window.redirect_uri
        method: get
        parameters:
        2.
        url: https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit
        method: post
        parameters:
        post_body: {
            "BaseRequest":{
                "Uin": Uin,
                "Sid": Sid,
                "Skey": Skey,
                "DeviceID": DeviceID
            }
        }
        '''
        response = self.web_client.do_get(self.login_redirect_url).decode("UTF-8")
        if not response:
            return False
        xml_response = xml.dom.minidom.parseString(response)
        root = xml_response.documentElement
        nodes = {node.nodeName : node.childNodes[0].data\
            for node in root.childNodes\
            if node.nodeName in ('skey', 'wxsid', 'wxuin', 'pass_ticket')}
        self.skey = nodes['skey']
        self.sid = nodes['wxsid']
        self.uin = nodes['wxuin']
        self.pass_ticket = nodes['pass_ticket']
        self.base_request_params = {
            'Uin': int(self.uin),
            'Sid': self.sid,
            'Skey': self.skey,
            'DeviceID': self.device_id
        }
        data = json.dumps({
            'BaseRequest': self.base_request_params
        })
        params = {
            'lang': self.lang,
            'pass_ticket': self.pass_ticket
        }
        url = self.login_base_url + '/webwxinit'
        init_data = self.web_client.do_post(url, data, True, params).decode("UTF-8")
        if not init_data:
            return False
        init_data = json.loads(init_data)
        self.synckey = init_data['SyncKey']
        self.user = init_data['User']
        self.init_data = init_data
        self.joined_synckey = ('|').join([\
            str(keyval['Key']) + '_' + str(keyval['Val'])\
            for keyval in init_data['SyncKey']['List']\
         ])
        return init_data['BaseResponse']['Ret'] == 0

    def open_login_statusnotify(self):
        '''
        登录后开启微信状态通知
        url: https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify
        method: post
        parameters: lang, pass_ticket
        post_body:{
            "BaseRequest":{
                "Uin": Uin,
                "Sid": Sid,
                "Skey": Skey,
                "DeviceID": DeviceID
                },
            "Code":3,
            "FromUserName": current_user_name,
            "ToUserName": current_user_name,
            "ClientMsgId": current_time
            }
        '''
        url = self.login_base_url + '/webwxstatusnotify'
        params = {
            'lang': self.lang,
            'pass_ticket': self.pass_ticket
        }
        data = {
            'BaseRequest': self.base_request_params,
            "Code": 3,
            "FromUserName": self.user['UserName'],
            "ToUserName": self.user['UserName'],
            "ClientMsgId": self.get_unix_timestamp()
        }
        response = self.web_client.do_post(url, json.dumps(data), True, params).decode("UTF-8")
        if not response:
            return False
        return json.loads(response)['BaseResponse']['Ret'] == 0

    def login_get_contact(self):
        '''
        登录后获取联系人
        url: https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact
        method: get
        parameters: seq, lang, skey, pass_ticket, r
        依据VerifyFlag区分：
        VerifyFlag：
            56 微信团队 -- 暂时只看到这一个
            29 京东 -- 暂时只看到这一个
            24 服务号（企业）
            8 订阅号（个人）
            0 联系人、特殊账号、群聊（只有保存到通讯录列表的群聊）
            企业号本身会被当成一个服务号，再根据里面的内容拆分成订阅号
        '''
        url = self.login_base_url + '/webwxgetcontact'
        params = {
            'seq': 0,
            'lang': self.lang,
            'skey': self.skey,
            'pass_ticket': self.pass_ticket,
            'r': self.get_unix_timestamp()
        }
        response = self.web_client.do_get(url, params).decode("UTF-8")
        if not response:
            return False
        response = json.loads(response)
        self.saved_member_count = response['MemberCount']
        self.saved_member_list = response['MemberList']
        for member in self.saved_member_list:
            if member['VerifyFlag'] == 56 or member['VerifyFlag'] == 29:
                self.special_account_list.append(member)
            elif member['VerifyFlag'] == 24 or member['VerifyFlag'] == 8:
                self.public_account_list.append(member)
            elif member['VerifyFlag'] == 0:
                if member['UserName'] in self.known_special_accounts:
                    self.special_account_list.append(member)
                elif member['UserName'][:2] == '@@':
                    self.saved_group_list.append(member)
                else:
                    self.contact_list.append(member)
            else:
                self.special_account_list.append(member)
                print("请注意这个特别的账号：")
        return True

    def login_get_extra_group(self):
        '''
        获取初始化提供的群聊列表
        根据init返回的chatset过滤，私聊init里有就不请求，否则就请求。。。
        群聊全部请求，init没有就EncryChatRoom，否则就chatroom。。。
        url: https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxbatchgetcontact
        method: post
        parameters: type, r, lang, pass_ticket
        post_body:{
            'BaseRequest': BaseRequest,
            'Count': count,
            'List' :[{
                'UserName': UserName,
                'ChatRoomId': ChatRoomId
            }]
        }
        '''
        account_to_filter = self.init_data['ChatSet'].split(',')[:-1]
        data = {
            'BaseRequest': self.base_request_params,
            'Count': 0,
            'List' :[]
        }
        owned_message_account = [contact['UserName'] for contact in self.init_data['ContactList']]
        for account in account_to_filter:
            if account[:2] == "@@":
                if account in owned_message_account:
                    data['List'].append({\
                    'UserName': account, 'ChatRoomId': ''\
                    })
                else:
                    data['List'].append({\
                    'UserName': account, 'EncryChatRoomId': ''\
                    })
            elif account not in owned_message_account:
                data['List'].append({\
                'UserName': account, 'EncryChatRoomId': ''\
                })
        data['Count'] = len(data['List'])
        if len(data['List']) == 0:
            return True
        url = self.login_base_url + '/webwxbatchgetcontact'
        params = {
            'type': 'ex',
            'r': self.get_unix_timestamp(),
            'lang': self.lang,
            'pass_ticket': self.pass_ticket,
        }
        response = self.web_client.do_post(url, json.dumps(data), True, params).decode("UTF-8")
        if not response:
            return False
        response = json.loads(response)
        if not response['ContactList']:
            return True
        returned_account = [\
            contact for contact in response['ContactList'] if contact['UserName'][:2] == '@@'\
         ]
        for account in returned_account:
            self.group_list.append(account)
        return True

    def get_group_info_by_id(self):
        print('todo')
    
    def get_sync_key(self):
        '''
        获取同步所用的key
        url: https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync
        method: post
        parameters: sid, skey
        post_body：{
            "BaseRequest":{
                "Uin": Uin,
                "Sid": Sid,
                "Skey": Skey,
                "DeviceID": DeviceID
                },
            "SyncKey":{
                "Count":Count,
                "List":[{"Key":Key,"Val":Val}},"rr": rr}
        '''
        url = self.login_base_url + '/webwxsync'
        params = {
            'sid': self.sid,
            'skey': self.skey
        }
        data = {
            'BaseRequest': self.base_request_params,
            'SyncKey': self.synckey,
            'rr': self.get_complement_code(self.get_unix_timestamp())
        }
        response = self.web_client.do_post(url, json.dumps(data), True, params).decode("UTF-8")
        if not response:
            print('获取Synckey失败，请检查。。。')
            return False
        response = json.loads(response)
        self.synckey = response['SyncKey']
        self.joined_synckey = ('|').join([\
            str(keyval['Key']) + '_' + str(keyval['Val'])\
            for keyval in response['SyncKey']['List']\
         ])

    def do_server_sync(self):
        '''
        微信服务器同步，检查连接是否正常，是否有新消息。。。
        url: https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck
        method: get
        parameters: r, skey, sid, uin, deviceid, synckey, _
        response:
            retcode:
                0 正常
                1100 失败/退出微信
            selector:
                0 正常
                2 新的消息
                7 进入/离开聊天界面
        '''
        if self.sync_url:
            url = self.sync_url
        elif self.login_redirect_url.split(r'/')[2] == 'wx2.qq.com':
            url = 'https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck'
        else:
            url = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck'
        params = {
            'r': self.get_unix_timestamp(),
            'skey': self.skey,
            'sid': self.sid,
            'uin': self.uin,
            'deviceid': self.device_id,
            'synckey': self.joined_synckey,
            '_': self.get_unix_timestamp()
        }
        response = self.web_client.do_get(url, params).decode("UTF-8")
        if not response:
            return ()
        reg = r'window.synccheck={retcode:"(\d)",selector:"(\d)"}'
        result = re.search(reg, response)
        if not result:
            return ()
        self.sync_url = url
        return (result.group(1), result.group(2))

    def check_server_sync(self):
        result = self.do_server_sync()
        if result and result[0] == '0':
            return True
        if len(self.backup_host_list) > 0:
            self.sync_url = 'https://' + self.backup_host_list.pop()
            self.do_server_sync()
        print('与微信服务器同步失败，请检查。。。')
        return False

    def get_new_msg(self):
        print('todo')
