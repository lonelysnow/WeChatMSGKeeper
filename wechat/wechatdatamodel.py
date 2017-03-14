#!/usr/bin/env python
# coding: utf-8
'''
    保存数据。。。
'''
import os
from sqlalchemy import Column, Integer, String, DECIMAL, \
    create_engine, exc, orm, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Users(Base):
    '''
    用户表
    '''
    __tablename__ = 'users'
    uin = Column(Integer)
    username = Column(String(128), primary_key=True)
    nickname = Column(String(128))
    headimgurl = Column(String(1024))
    contactflag = Column(Integer)
    membercount = Column(Integer)
    memberlist = Column(String(1024))
    remarkname = Column(String(128))
    hideinputbarflag = Column(Integer)
    sex = Column(Integer)
    signature = Column(String(1024))
    verifyflag = Column(Integer)
    owneruin = Column(Integer)
    pyinitial = Column(String(128))
    pyquanpin = Column(String(128))
    remarkpyinitial = Column(String(128))
    remarkpyquanpin = Column(String(128))
    starfriend = Column(Integer)
    appaccountflag = Column(Integer)
    statues = Column(Integer)
    attrstatus = Column(Integer)
    province = Column(String(128))
    city = Column(String(128))
    alias = Column(String(128))
    snsflag = Column(Integer)
    unifriend = Column(Integer)
    displayname = Column(String(128))
    chatroomid = Column(Integer)
    keyword = Column(String(128))
    encrychatroomId = Column(String(128))
    isowner = Column(Integer)

class UserGroupMap(Base):
    '''
    群组表
    '''
    __tablename__ = 'user_group_map'
    uin = Column(Integer)
    groupusername = Column(String(128), primary_key=True)
    groupnickname = Column(String(128))
    username = Column(String(128), ForeignKey('users.username'))
    usernickname = Column(String(128))

class Message(Base):
    '''
    消息表
    '''
    __tablename__ = 'message'
    msgid = Column(String(128))
    fromusername = Column(String(128))
    tousername = Column(String(128))
    msgtype = Column(Integer)
    content = Column(String(4096))
    status = Column(Integer)
    imgstatus = Column(Integer)
    createtime = Column(Integer)
    voicelength = Column(Integer)
    playlength = Column(Integer)
    filename = Column(String(128))
    filesize = Column(String(128))
    mediaid = Column(String(128))
    url = Column(String(1024))
    appmsgtype = Column(Integer)
    statusnotifycode = Column(Integer)
    statusnotifyusername = Column(String(4096))
    recommendinfo = Column(Integer, ForeignKey('message_recommendinfo.id'))
    forwardflag = Column(Integer)
    appInfo = Column(Integer, ForeignKey('message_appinfo.id'))
    hasProductid = Column(Integer)
    ticket = Column(String(128))
    imgheight = Column(Integer)
    imgwidth = Column(Integer)
    submsgtype = Column(Integer)
    newmsgid = Column(DECIMAL)
    oricontent = Column(String(128))

class RecommendInfo(Base):
    '''
    消息推荐信息表
    '''
    __tablename__ = 'message_recommendinfo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128))
    nickname = Column(String(128))
    qqnum = Column(DECIMAL)
    province = Column(String(128))
    city = Column(String(128))
    content = Column(String(128))
    signature = Column(String(128))
    alias = Column(String(128))
    scene = Column(Integer)
    verifyflag = Column(Integer)
    attrstatus = Column(Integer)
    sex = Column(Integer)
    ticket = Column(String(128))
    opcode = Column(Integer)

class AppInfo(Base):
    '''
    消息应用信息表
    '''
    __tablename__ = 'message_appinfo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    appid = Column(DECIMAL)
    apptype = Column(Integer)

class WeChatDB():
    '''
    数据库操作
    '''
    def __init__(self, dsn):
        try:
            engine = create_engine(dsn)
        except ImportError:
            print('请安装sqlalchemy库后重试，例如使用: pip install sqlalchemy\n\n\
             -----------------我是分隔线-----------------\n\n')
        try:
            engine.connect()
        except exc.OperationalError:
            engine = create_engine(os.path.dirname(dsn))
            engine.execute('CREATE DATABASE %s' % os.path.basename(dsn)).close()
            engine = create_engine(dsn)
            Base.metadata.create_all(engine)
        Session = orm.sessionmaker(bind=engine)
        self.session = Session()
