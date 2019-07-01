# -*- encoding:utf-8 -*-
"""
@ Created by Seven on  2019/01/19 <https://7yue.in>
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, FetchedValue, SmallInteger, TIMESTAMP
from werkzeug.security import generate_password_hash, check_password_hash

from .enums import UserSuper, UserActive
from .db import MixinJSONSerializer, db
from .util import camel2line


# 基础的crud model
class BaseCrud(db.Model, MixinJSONSerializer):
    __abstract__ = True

    def __init__(self):
        name: str = self.__class__.__name__
        if not hasattr(self, '__tablename__'):
            self.__tablename__ = camel2line(name)

    def _set_fields(self):
        self._exclude = []

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    # 硬删除
    def delete(self, commit=False):
        db.session.delete(self)
        if commit:
            db.session.commit()

    # 查
    @classmethod
    def get(cls, start=None, count=None, one=True, **kwargs):
        if one:
            return cls.query.filter().filter_by(**kwargs).first()
        return cls.query.filter().filter_by(**kwargs).offset(start).limit(count).all()

    # 增
    @classmethod
    def create(cls, **kwargs):
        one = cls()
        for key in kwargs.keys():
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        db.session.add(one)
        if kwargs.get('commit') is True:
            db.session.commit()
        return one

    def update(self, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        db.session.add(self)
        if kwargs.get('commit') is True:
            db.session.commit()
        return self


# 提供软删除，及创建时间，更新时间信息的crud model
class InfoCrud(db.Model, MixinJSONSerializer):
    __abstract__ = True
    _create_time = Column('create_time', TIMESTAMP(True), default=datetime.now)
    update_time = Column(TIMESTAMP(True), default=datetime.now, onupdate=datetime.now)
    delete_time = Column(TIMESTAMP(True))

    def __init__(self):
        name: str = self.__class__.__name__
        if not hasattr(self, '__tablename__'):
            self.__tablename__ = camel2line(name)

    def _set_fields(self):
        self._exclude = ['update_time', 'delete_time']

    @property
    def create_time(self):
        if self._create_time is None:
            return None
        return int(round(self._create_time.timestamp() * 1000))

    # @property
    # def update_time(self):
    #     if self._update_time is None:
    #         return None
    #     return int(round(self._update_time.timestamp() * 1000))

    # @property
    # def delete_time(self):
    #     if self._delete_time is None:
    #         return None
    #     return int(round(self._delete_time.timestamp() * 1000))

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    # 软删除
    def delete(self, commit=False):
        self.delete_time = datetime.now()
        db.session.add(self)
        # 记得提交会话
        if commit:
            db.session.commit()

    # 硬删除
    def hard_delete(self, commit=False):
        db.session.delete(self)
        if commit:
            db.session.commit()

    # 查
    @classmethod
    def get(cls, start=None, count=None, one=True, **kwargs):
        # 应用软删除，必须带有delete_time
        if kwargs.get('delete_time') is None:
            kwargs['delete_time'] = None
        if one:
            return cls.query.filter().filter_by(**kwargs).first()
        return cls.query.filter().filter_by(**kwargs).offset(start).limit(count).all()

    # 增
    @classmethod
    def create(cls, **kwargs):
        one = cls()
        for key in kwargs.keys():
            # if key == 'from':
            #     setattr(one, '_from', kwargs[key])
            # if key == 'parts':
            #     setattr(one, '_parts', kwargs[key])
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        db.session.add(one)
        if kwargs.get('commit') is True:
            db.session.commit()
        return one

    def update(self, **kwargs):
        for key in kwargs.keys():
            # if key == 'from':
            #     setattr(self, '_from', kwargs[key])
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        db.session.add(self)
        if kwargs.get('commit') is True:
            db.session.commit()
        return self


class UserInterface(InfoCrud):
    __tablename__ = 'jian_user'

    id = Column(Integer, primary_key=True)
    nickname = Column(String(24), nullable=False, unique=True)
    # : super express the user is super(super admin) ;  1 -> common |  2 -> super
    # : super 代表是否为超级管理员 ;  1 -> 普通用户 |  2 -> 超级管理员
    super = Column(SmallInteger, nullable=False, default=1, server_default=FetchedValue())
    # : active express the user can manage the authorities or not ; 1 -> active | 2 -> not
    # : active 代表当前用户是否为激活状态，非激活状态默认失去用户权限 ; 1 -> 激活 | 2 -> 非激活
    active = Column(SmallInteger, nullable=False, default=1, server_default=FetchedValue())
    # : used to send email in the future
    # : 预留字段，方便以后扩展
    email = Column(String(100), unique=True)
    # : which group the user belongs,nullable is true
    # : 用户所属的权限组id
    group_id = Column(Integer)
    _password = Column('password', String(100))

    def _set_fields(self):
        self._exclude = ['password']

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    @property
    def is_super(self):
        return self.super == UserSuper.SUPER.value

    @property
    def is_active(self):
        return self.active == UserActive.ACTIVE.value

    @classmethod
    def verify(cls, nickname, password):
        raise Exception('must implement this method')

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    def reset_password(self, new_password):
        raise Exception('must implement this method')

    def change_password(self, old_password, new_password):
        raise Exception('must implement this method')


class AuthInterface(BaseCrud):
    __tablename__ = 'jian_auth'

    id = Column(Integer, primary_key=True)
    # : belongs to which group
    # : 所属权限组id
    group_id = Column(Integer, nullable=False)
    # : authority field
    # : 权限字段
    auth = Column(String(60))
    # : authority module, default common , which can sort authorities
    # : 权限的模块
    module = Column(String(50))


class GroupInterface(BaseCrud):
    __tablename__ = 'jian_group'

    id = Column(Integer, primary_key=True)
    # : name of group
    # : 权限组名称
    name = Column(String(60))
    # a description of a group
    # 权限组描述
    info = Column(String(255))


class LogInterface(BaseCrud):
    __tablename__ = 'jian_log'

    id = Column(Integer, primary_key=True)
    # : log message
    # : 日志信息
    message = Column(String(450))
    # : create time
    # : 日志创建时间
    _time = Column('time', TIMESTAMP(True), default=datetime.now)
    # : user id
    # : 用户id
    user_id = Column(Integer, nullable=False)
    # user_name at that moment
    # 用户当时的昵称
    user_name = Column(String(20))
    # : status_code check request is success or not
    # : 请求的http返回码
    status_code = Column(Integer)
    # request method
    # 请求方法
    method = Column(String(20))
    # request path
    # 请求路径
    path = Column(String(50))
    # which authority is accessed
    # 访问那个权限
    authority = Column(String(100))

    @property
    def time(self):
        if self._time is None:
            return None
        return int(round(self._time.timestamp() * 1000))


class EventInterface(BaseCrud):
    __tablename__ = 'jian_event'
    id = Column(Integer, primary_key=True)
    # : belongs to which group
    group_id = Column(Integer, nullable=False)
    # message type ['订单','修改密码']
    message_events = Column(String(250))


# service暂时不用
class ServiceInterface(object):
    pass
