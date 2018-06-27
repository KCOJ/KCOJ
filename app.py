#!/usr/bin/env python3

from KCOJ_api.kcoj import KCOJ

from flask import Flask, request, url_for, redirect, Response
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import sys
import json
import time
import hashlib
import threading

URL = "https://140.124.184.228/Exam/"

# 初始化 Flask
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

# 初始化 Flask 登入管理員
login_manager = LoginManager(app)

# 儲存使用者資訊
users = {}  

class User(UserMixin):      
    def __init__(self, userid):
        super()
        self.id = userid

@login_manager.user_loader
def user_loader(userid):
    if userid in users:    
        return User(userid)
    else:
        return None

# 試著保持著登入狀態
def keep_login():
    user = users[current_user.get_id()]
    # 確認是否是登入狀態
    if user['api'].check_online():
        return True
    # 如果不是登入狀態就嘗試登入
    user['api'].login(user['userid'], user['passwd'], user['course'])
    # 回傳登入狀態
    return user['api'].check_online()

# 主畫面
@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
def root_page():
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    # TODO: 顯示主畫面
    return str(users[current_user.get_id()]['api'].get_notices())

# 登入失敗回到登入畫面
@login_manager.unauthorized_handler
def login_failed_page():
    return redirect('/login')

# 登入畫面
@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login_page():
    if request.method == 'GET':
        # TODO: 放上真正的登入畫面。
        temp = """
            <form action='/login' method='POST'>
                userid: <input name='userid' type='text' required/>
                <br>
                passwd: <input name='passwd' type='password' required/>
                <br>
                course: <input name='course' type='text' required/>
                <br>
                <input value='Login' type='submit'/>
            </form>
        """
        return Response(temp, content_type='text/html; charset=utf-8')

    if request.method == 'POST':
        # 取得登入資訊
        userid = request.form['userid']
        passwd = request.form['passwd']
        course = request.form['course']
        # 登入交作業網站
        api = KCOJ(URL)
        api.login(userid, passwd, course)
        # 確認是否登入成功
        if api.check_online():
            # 登入成功
            login_user(User(userid))
            # 將登入資訊儲存起來
            if userid in users:
                users[userid]['api'] = api
            else:
                users[userid] = {
                    'userid': userid,
                    'passwd': passwd,
                    'course': course,
                    'email': '',
                    'api': api,
                }
            return redirect('/')
        else:
            # TODO: 登入失敗顯示登入畫面並加上失敗提示字串。
            return redirect('/login')

# 個人資料畫面
@app.route('/user', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def user_page():
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    if request.method == 'GET':
        # TODO: 顯示 Gravatar 大頭貼和變更密碼的欄位，
        # 不過在顯示別人的資料（?id=）時不會出現變更密碼的欄位。
        email = users[current_user.get_id()]['email']
        gravatar_url = 'https://s.gravatar.com/avatar/' + hashlib.md5(bytes(email, 'utf-8')).hexdigest()
        temp = """
            <img src="{0}" alt="gravatar">
            <pre>{1}</pre>
            <form action='/user' method='POST'>
                old_passwd: <input name='old_passwd' type='password' required/>
                <br>
                new_passwd: <input name='new_passwd' type='password'/>
                <br>
                email: <input name='email' type='email'/>
                <br>
                <input value='Submit' type='submit'/>
            </form>
        """.format(gravatar_url, email)
        return Response(temp, content_type='text/html; charset=utf-8')
    if request.method == 'POST':
        # TODO: 判斷舊密碼是否正確，正確的話更新資料。
        return "POST /user"

# 技巧文庫畫面
@app.route('/docs', methods=['GET'], strict_slashes=False)
@login_required
def docs_page():
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    # TODO: 顯示文件列表。
    return "GET /docs"

# 技巧文件畫面
@app.route('/docs/<name>', methods=['GET'], strict_slashes=False)
@login_required
def docs_name_page(name):
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    # TODO: 顯示該篇文件。
    return "GET /docs/" + name

# 作業題庫畫面
@app.route('/question', methods=['GET'], strict_slashes=False)
@login_required
def question_page():
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    # TODO: 顯示題目列表。
    return str(users[current_user.get_id()]['api'].list_questions())

# 作業題目畫面
@app.route('/question/<number>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def question_number_page(number):
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    if request.method == 'GET':
        # TODO: 顯示題目內容。
        return users[current_user.get_id()]['api'].show_question(number)
    if request.method == 'POST':
        # TODO: 提交程式碼內容到作業網站。
        return "POST /question/" + number

# 作業討論畫面
@app.route('/question/<number>/chat', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def question_number_chat_page(number):
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    if request.method == 'GET':
        # TODO: 顯示討論內容。
        return "GET /question/" + number + "chat"
    if request.method == 'POST':
        # TODO: 新增討論文章。
        return "POST /question/" + number + "chat"

# 作業通過畫面
@app.route('/question/<number>/passed', methods=['GET'], strict_slashes=False)
@login_required
def question_number_passed_page(number):
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()
    
    # TODO: 顯示通過名單。
    return str(users[current_user.get_id()]['api'].list_passers(number))

# 登出沒有畫面
@app.route('/logout', methods=['GET'], strict_slashes=False)
@login_required
def logout_nopage():
    logout_user()
    return redirect('/login')

# 將 JSON 檔還原使用者資料
def restore_db():
    try:
        with open(sys.path[0] + '/users.json', 'r') as f:
            users_restore = json.load(f)
            for key in users_restore.keys():
                user = users_restore[key]
                users[key] = {
                    'userid': user['userid'],
                    'passwd': user['passwd'],
                    'course': user['course'],
                    'email': user['email'],
                    'api': KCOJ(URL),
                }
    except FileNotFoundError:
        with open(sys.path[0] + '/users.json', 'w') as f:
            f.write("{}")

# 備份使用者資料到 JSON 檔
def backup_db():
    users_backup = {}
    for key in users.keys():
        user = users[key]
        users_backup[key] = {
            'userid': user['userid'],
            'passwd': user['passwd'],
            'course': user['course'],
            'email': user['email'],
        }
    with open(sys.path[0] + '/users.json', 'w') as f:
        json.dump(users_backup, f, indent='  ')
	
class BackupThread(threading.Thread):
    def run(self):
        while True:
            # 備份資料
            backup_db()
            # 延遲 10 秒
            time.sleep(10)

def main():
    # 還原資料
    restore_db()
    # 背景自動備份資料
    BackupThread().start()
    # 開啟伺服器
    app.run(port=11711, threaded=True)

if __name__ == '__main__':
    main()