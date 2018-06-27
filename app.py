#!/usr/bin/env python3

from KCOJ_api.kcoj import KCOJ

from flask import Flask, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

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
    user['api'].login(current_user.get_id(), user['passwd'], user['course'])
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
    return "GET /"

# 登入失敗回到登入畫面
@login_manager.unauthorized_handler
def login_failed_page():
    return redirect('/login')

# 登入畫面
@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login_page():
    if request.method == 'GET':
        # TODO: 放上真正的登入畫面。
        return """
            <form action='login' method='POST'>
                <input name='userid' type='text'/>
                <input name='passwd' type='password'/>
                <input name='course' type='text'/>
                <input value='Login' type='submit'/>
            </form>
        """

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
        
        return "GET /user"
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
    return "GET /question"

# 作業題目畫面
@app.route('/question/<number>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def question_number_page(number):
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    if request.method == 'GET':
        # TODO: 顯示題目內容。
        return "GET /question/" + number
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
    return "GET /question/" + number + "passed"

# 登出沒有畫面
@app.route('/logout', methods=['GET'], strict_slashes=False)
@login_required
def logout_nopage():
    logout_user()
    return redirect('/login')


def main():
    app.run(port=11711, threaded=True)

if __name__ == '__main__':
    main()