import urllib3
from flask import Flask, redirect
from flask_login import LoginManager

from .models.user import User
from .routes.pages import app as pages_api

urllib3.disable_warnings()

# 初始化 Flask
app = Flask(__name__,
            instance_relative_config=True)
app.config.from_pyfile('config.py')

# 初始化 Flask 登入管理員
login_manager = LoginManager(app)


@login_manager.user_loader
def user_loader(useruid):
    if User.is_exist(useruid):
        return User(useruid)
    else:
        return None


@login_manager.unauthorized_handler
def login_failed_page():
    """
    登入失敗轉址回登入畫面
    """
    return redirect('/login')


app.register_blueprint(pages_api)
