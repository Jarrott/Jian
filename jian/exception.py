# -*- encoding:utf-8 -*-
"""
@ Created by Seven on  2019/01/19 <https://7yue.in>
"""
from flask import json, request
from werkzeug.exceptions import HTTPException
from werkzeug._compat import text_type


class APIException(HTTPException):
    code = 500
    msg = '抱歉，服务器未知错误'
    error_code = 999

    def __init__(self, msg=None, code=None, error_code=None,
                 headers=None):
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if msg:
            self.msg = msg
        if headers is not None:
            headers_merged = headers.copy()
            headers_merged.update(self.headers)
            self.headers = headers_merged

        super(APIException, self).__init__(msg, None)

    def get_body(self, environ=None):
        body = dict(
            msg=self.msg,
            error_code=self.error_code,
            request=request.method + '  ' + self.get_url_no_param()
        )
        text = json.dumps(body)
        return text_type(text)

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]


class Success(APIException):
    code = 201
    msg = '成功'
    error_code = 0


class Failed(APIException):
    code = 400
    msg = '失败'
    error_code = 9999


class AuthFailed(APIException):
    code = 401
    msg = '认证失败'
    error_code = 10000


class NotFound(APIException):
    code = 404
    msg = '资源不存在'
    error_code = 10020


class ParameterException(APIException):
    code = 400
    msg = '参数错误'
    error_code = 10030


class InvalidTokenException(APIException):
    code = 401
    msg = '令牌失效'
    error_code = 10040


class ExpiredTokenException(APIException):
    code = 422
    msg = '令牌过期'
    error_code = 10050


class UnknownException(APIException):
    code = 400
    msg = '服务器未知错误'
    error_code = 999


class RepeatException(APIException):
    code = 400
    msg = '字段重复'
    error_code = 10060


class Forbidden(APIException):
    code = 401
    msg = '不可操作'
    error_code = 10070
