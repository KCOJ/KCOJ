from flask import Blueprint, request, redirect
from flask_login import login_required, logout_user, current_user

from ..controllers.keep_active import keep_active
from ..controllers.index_page import main as index_page
from ..controllers.login_page import main as login_page
from ..controllers.login import main as login
from ..controllers.user_page import main as user_page
from ..controllers.user import main as user
from ..controllers.question_page import main as question_page
from ..controllers.question_content_page import main as question_content_page
from ..controllers.question_content import main as question_content
from ..controllers.question_passed_page import main as question_passed_page

app = Blueprint('pages', __name__)


@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
def index_route():
    """
    首頁畫面
    """
    # 取得使用者物件
    useruid = current_user.get_id()

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    # 顯示主畫面
    return index_page(useruid)


@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login_route():
    """
    登入畫面
    """
    if request.method == 'GET':
        # 顯示登入畫面
        return login_page()

    if request.method == 'POST':
        # 取得登入資訊
        userid = request.form['userid']
        passwd = request.form['passwd']
        course = request.form['course']

        return login(userid, passwd, course)


@app.route('/user', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def user_route():
    """
    個資畫面
    """
    # 取得使用者物件
    useruid = current_user.get_id()

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    if request.method == 'GET':
        # 取得要查看的使用者 ID
        target_id = request.args.get('userid')

        # 顯示個資畫面
        return user_page(useruid, target_id)

    if request.method == 'POST':
        # 取得要更新的資訊
        old_passwd = request.form.get('old_passwd')
        new_passwd = request.form.get('new_passwd')
        email = request.form.get('email')

        return user(useruid, old_passwd, new_passwd, email)


@app.route('/question', methods=['GET'], strict_slashes=False)
@login_required
def question_route():
    """
    題庫畫面
    """
    # 取得使用者物件
    useruid = current_user.get_id()

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    return question_page(useruid)


@app.route('/question/<number>/content', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/question/<number>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def question_content_route(number):
    """
    題目內容畫面
    """
    # 取得使用者物件
    useruid = current_user.get_id()

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    if request.method == 'GET':
        return question_content_page(useruid, number)

    if request.method == 'POST':
        # 取得使用者程式碼
        code = request.form['code']

        return question_content(useruid, number, code)


@app.route('/question/<number>/passed', methods=['GET'], strict_slashes=False)
@login_required
def question_passed_route(number):
    """
    題目通過者畫面
    """
    # 取得使用者物件
    useruid = current_user.get_id()

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    return question_passed_page(useruid, number)


@app.route('/logout', methods=['GET'], strict_slashes=False)
@login_required
def logout_nopage():
    """
    登出系統
    """
    logout_user()
    return redirect('/login')
