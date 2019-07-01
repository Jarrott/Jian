# -*- encoding:utf-8 -*-
"""
@ Created by Seven on  2019/01/19 <https://7yue.in>
"""

from functools import wraps

from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_current_user, create_access_token, \
    create_refresh_token

from .exception import AuthFailed, InvalidTokenException, ExpiredTokenException, NotFound

jwt = JWTManager()


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_current_user()
        if not current_user.is_super:
            raise AuthFailed(msg='只有超级管理员可操作')
        return fn(*args, **kwargs)

    return wrapper


def group_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_current_user()
        # check current user is active or not
        # 判断当前用户是否为激活状态
        if not current_user.is_active:
            raise AuthFailed(msg='您目前处于未激活状态，请联系超级管理员')
        # not super
        if not current_user.is_super:
            group_id = current_user.group_id
            if group_id is None:
                raise AuthFailed(msg='您还不属于任何权限组，请联系超级管理员获得权限')
            from .core import is_user_allowed
            it = is_user_allowed(group_id)
            if not it:
                raise AuthFailed(msg='权限不够，请联系超级管理员获得权限')
            else:
                return fn(*args, **kwargs)
        else:
            return fn(*args, **kwargs)

    return wrapper


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)

    return wrapper


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    from .core import find_user
    # token is granted , user must be exit
    # 如果token已经被颁发，则该用户一定存在
    user = find_user(id=identity)
    if user is None:
        raise NotFound(msg='用户不存在')
    return user


@jwt.expired_token_loader
def expired_loader_callback():
    return ExpiredTokenException()


@jwt.invalid_token_loader
def invalid_loader_callback(e):
    return InvalidTokenException()


@jwt.unauthorized_loader
def unauthorized_loader_callback(e):
    return AuthFailed(msg='认证失败，请检查请求头或者重新登陆')


def get_tokens(user):
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return access_token, refresh_token