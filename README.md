<h4 align="center">Jian (简单)</h4>

<p align="center">
  <a href="http://flask.pocoo.org/docs/1.0/" rel="nofollow">
  <img src="https://img.shields.io/badge/Flask-1.0.2-green.svg" alt="flask version" data-canonical-src="https://img.shields.io/badge/Flask-1.0.2-green.svg" style="max-width:100%;"></a>
  <a href="https://www.python.org" rel="nofollow"><img src="https://img.shields.io/badge/Python-%3E3.5-yellowgreen.svg" alt="Python version" data-canonical-src="https://img.shields.io/badge/Python-%3E3.5-yellowgreen.svg" style="max-width:100%;"></a>
</p>

# Jian
对Flask项目中一些常用第三方进行封装.
例如:
 - SQLalchemy
 - WTF-forms
 - JWT
 - Blueprint
 - Route_meta
 - Exception
 - Log
对这些优秀的第三方库进行二次开发,使更贴合我们项目中的使用.


# 安装 install

> pipenv or pip

```bash
pipenv install jian
```

`or`

```bash
pip install jian
```

## 使用

> 初始化项目,并且注册Jian

```python
from jian import Jian


def create_apps():
    app = Flask(__name__)
    app.config.from_object('app.config.setting')
    Jian(app)
```

> 数据层操作

```python
from sqlalchemy import Column, String, Integer

from jian.interface import InfoCrud as Base


class Friend(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(32), unique=True)
    doc = Column(String(50))
    image = Column(String(50))
```

> 表单验证
```python
from wtforms import PasswordFiled
from wtforms.validators import DataRequired
from jian.forms import Form

# 注册校验
class RegisterForm(Form):
    password = PasswordField('新密码', validators=[
        DataRequired(message='新密码不可为空'),
        Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}$', message='密码长度必须在6~22位之间，包含字符、数字和 _ '),
        EqualTo('confirm_password', message='两次输入的密码不一致，请输入相同的密码')])
    confirm_password = PasswordField('确认新密码', validators=[DataRequired(message='请确认密码')])
    nickname = StringField(validators=[DataRequired(message='昵称不可为空'),
                                       length(min=2, max=10, message='昵称长度必须在2~10之间')])
```

> 获取JWT登录令牌

```python
from jian.jwt import get_tokens

# Forms , Exception, Model 等要自己引入,这里只介绍jwt的用法
# 登录逻辑只是展示,并不是这样直接用,登录逻辑已经封装到jian.core中

@login.route('/login', methods=['POST'])
def login():
    form = LoginForm().validate_for_api()
    user = User.query.filter_by(nickname=nickname).first()
    if user is None or user.delete_time is not None:
        raise NotFound(msg='用户不存在')
    if not user.check_password(password):
        raise ParameterException(msg='密码错误，请输入正确密码')
    if not user.is_active:
        raise AuthFailed(msg='您目前处于未激活状态，请联系超级管理员')
    access_token, refresh_token = get_tokens(user)
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })
```

> 记录日志模块

```python
from jian.log import Logger

# 第一种方法
@Logger(template='新注册了一个用户')
def register_user():
    pass

# 第二种方法主要是复杂的结构
def register_user():
    Log.create_log(
        message=f'{user.nickname}登陆成功获取了令牌',
        user_id=user.id, user_name=user.nickname,
        status_code=200, method='post',path='/cms/user/login',
        authority='无', commit=True
    )
    ...

```

## 下个版本开发计划

- [ ] 加入Swagger文档.
- [ ] 文件上传模块.