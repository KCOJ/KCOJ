#!/usr/bin/env python3

from KCOJ_api.kcoj import KCOJ

from flask import Flask, request, url_for, redirect, Response, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import sys
import json
import time
import hashlib
import threading

URL = "https://140.124.184.228/Exam/"

# 初始化 Flask
app = Flask(__name__, instance_relative_config=True, template_folder='template')
app.config.from_object('config')
app.config.from_pyfile('config.py')

# 初始化 Flask 登入管理員
login_manager = LoginManager(app)

# 寫死的題目標題、敘述、標籤
with open('questions.json', 'r') as f:
    ext_questions = json.load(f)

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

# 取得 Gravatar 上的大頭貼
def get_gravatar(email, size):
    return 'https://s.gravatar.com/avatar/' + hashlib.md5(bytes(email, 'utf-8')).hexdigest() + '?size=' + str(size)

# 主畫面
@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
def index_page():
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    userid = current_user.get_id()
    # 顯示主畫面
    return render_template('index.html', title="KCOJ - 首頁", userid=userid, gravatar=get_gravatar(users[userid]['email'], 30), notices=users[userid]['api'].get_notices())

# 登入失敗回到登入畫面
@login_manager.unauthorized_handler
def login_failed_page():
    return redirect('/login')

# 登入畫面
@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login_page():
    # 使用 API
    api = KCOJ(URL)

    if request.method == 'GET':
        # 顯示登入畫面
        return render_template('login.html', title="KCOJ - 登入", courses=api.get_courses())

    if request.method == 'POST':
        # 取得登入資訊
        userid = request.form['userid']
        passwd = request.form['passwd']
        try:
            course = api.get_courses().index(request.form['course']) + 1
        except ValueError:
            course = 0
        # 登入交作業網站
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
            # 顯示登入畫面含錯誤訊息
            return render_template('login.html', title="KCOJ - 登入", courses=api.get_courses(), error_message="登入失敗，請檢查輸入的資訊是否有誤！")

# 個人資料畫面
@app.route('/user', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def user_page():
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    if request.method == 'GET':
        # TODO: 在顯示別人的資料（?id=）時不會出現變更密碼的欄位。

        userid = current_user.get_id()

        try:
            view_userid = request.args['userid']
        except KeyError:
            view_userid = userid

        try:
            view_email = users[view_userid]['email']
        except KeyError:
            if view_userid == userid:
                view_email = users[userid]['email']
            else:
                view_email = ''

        return render_template('user.html', title=("KCOJ - " + view_userid), userid=userid, gravatar=get_gravatar(users[userid]['email'], 30), view_userid=view_userid, view_email=view_email, view_gravatar=get_gravatar(view_email, 200), no_me=(userid != view_userid))

    if request.method == 'POST':
        # 取得更新資訊
        userid = current_user.get_id()
        old_passwd = request.form['old_passwd']
        new_passwd = request.form['new_passwd']
        email = request.form['email']
        # 登入交作業網站
        api = KCOJ(URL)
        api.login(userid, old_passwd, users[userid]['course'])
        # 確認是否登入成功
        if api.check_online():
            # 如果要變更密碼
            if new_passwd != '':
                api.change_password(new_passwd)
                users[userid]['passwd'] = new_passwd
            # 如果要變更 Email
            if email != '':
                users[userid]['email'] = email
                
        return redirect('/user')

# 技巧文庫畫面
@app.route('/docs', methods=['GET'], strict_slashes=False)
@login_required
def docs_page():
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    userid = current_user.get_id()

    return render_template('docs.html', title="KCOJ - 程式技巧", userid=userid, gravatar=get_gravatar(users[userid]['email'], 30))

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

    # 顯示題目列表。
    userid = current_user.get_id()

    questions = {}
    int_questions = users[userid]['api'].list_questions()

    for number in int_questions:
        if number in ext_questions:
            questions[number] = {
                'title': ext_questions[number]['title'],
                'description': ext_questions[number]['description'],
                'tag': ext_questions[number]['tag'],
                'deadline': int_questions[number][0],
                'submit': int_questions[number][1],
                'status': int_questions[number][2],
                'language': int_questions[number][3],
                'results': users[userid]['api'].list_results(number, userid),
            }
        else:
            questions[number] = {
                'title': '未命名',
                'description': '沒有敘述',
                'tag': '',
                'deadline': int_questions[number][0],
                'submit': int_questions[number][1],
                'status': int_questions[number][2],
                'language': int_questions[number][3],
                'results': users[userid]['api'].list_results(number, userid),
            }

    close_questions = {}
    open_questions = {}

    for number in questions:
        if questions[number]['submit'] == '期限已到':
            close_questions[number] = questions[number]
            if len(close_questions[number]['results']) == 0:
                close_questions[number]['result'] = 2
            else:
                results = []
                raw = close_questions[number]['results']
                for result in raw:
                    results += [result[1]]

                results = list(map(lambda x: x == '通過測試', results))

                if False in results:
                    close_questions[number]['result'] = 0
                else:
                    close_questions[number]['result'] = 1
        else:
            open_questions[number] = questions[number]
            if len(open_questions[number]['results']) == 0:
                open_questions[number]['result'] = 2
            else:
                results = []
                raw = open_questions[number]['results']
                for result in raw:
                    results += [result[1]]

                results = list(map(lambda x: x == '通過測試', results))

                if False in results:
                    open_questions[number]['result'] = 0
                else:
                    open_questions[number]['result'] = 1

    return render_template('question.html', title="KCOJ - 題庫", userid=userid, gravatar=get_gravatar(users[userid]['email'], 30), course=KCOJ(URL).get_courses()[int(users[userid]['course']) - 1], open_questions=open_questions, close_questions=close_questions)

# 作業題目畫面
@app.route('/question/<number>/content', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/question/<number>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def question_number_page(number):
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    if request.method == 'GET':
        userid = current_user.get_id()

        content = users[userid]['api'].show_question(number)

        question_number = number

        questions = {}
        int_questions = users[userid]['api'].list_questions()

        for number in int_questions:
            if number in ext_questions:
                questions[number] = {
                    'title': ext_questions[number]['title'],
                    'description': ext_questions[number]['description'],
                    'tag': ext_questions[number]['tag'],
                    'deadline': int_questions[number][0],
                    'submit': int_questions[number][1],
                    'status': int_questions[number][2],
                    'language': int_questions[number][3],
                    'results': users[userid]['api'].list_results(number, userid),
                }
            else:
                questions[number] = {
                    'title': '未命名',
                    'description': '沒有敘述',
                    'tag': '',
                    'deadline': int_questions[number][0],
                    'submit': int_questions[number][1],
                    'status': int_questions[number][2],
                    'language': int_questions[number][3],
                    'results': users[userid]['api'].list_results(number, userid),
                }

        for number in questions:
            if len(questions[number]['results']) == 0:
                questions[number]['result'] = 2
            else:
                results = []
                raw = questions[number]['results']
                for result in raw:
                   results += [result[1]]

                results = list(map(lambda x: x == '通過測試', results))

                if False in results:
                    questions[number]['result'] = 0
                else:
                    questions[number]['result'] = 1

        question = questions[question_number]

        results = []
        raw = question['results']
        for result in raw:
           results += [result]

        display_results = list(map(lambda x: [int(x[1] == '通過測試'), x[0], x[1]], results))

        return render_template('question_number.html', title=("KCOJ - " + question_number), userid=userid, gravatar=get_gravatar(users[userid]['email'], 30), question_number=question_number, question_title=question['title'], content=content, results=display_results)
    if request.method == 'POST':
        # TODO: 提交程式碼內容到作業網站。
        return "POST /question/" + number

# 作業討論畫面
@app.route('/question/<number>/forum', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def question_number_forum_page(number):
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()

    if request.method == 'GET':
        userid = current_user.get_id()

        content = users[userid]['api'].show_question(number)

        question_number = number

        questions = {}
        int_questions = users[userid]['api'].list_questions()

        for number in int_questions:
            if number in ext_questions:
                questions[number] = {
                    'title': ext_questions[number]['title'],
                    'description': ext_questions[number]['description'],
                    'tag': ext_questions[number]['tag'],
                    'deadline': int_questions[number][0],
                    'submit': int_questions[number][1],
                    'status': int_questions[number][2],
                    'language': int_questions[number][3],
                    'results': users[userid]['api'].list_results(number, userid),
                }
            else:
                questions[number] = {
                    'title': '未命名',
                    'description': '沒有敘述',
                    'tag': '',
                    'deadline': int_questions[number][0],
                    'submit': int_questions[number][1],
                    'status': int_questions[number][2],
                    'language': int_questions[number][3],
                    'results': users[userid]['api'].list_results(number, userid),
                }

        for number in questions:
            if len(questions[number]['results']) == 0:
                questions[number]['result'] = 2
            else:
                results = []
                raw = questions[number]['results']
                for result in raw:
                   results += [result[1]]

                results = list(map(lambda x: x == '通過測試', results))

                if False in results:
                    questions[number]['result'] = 0
                else:
                    questions[number]['result'] = 1

        question = questions[question_number]

        results = []
        raw = question['results']
        for result in raw:
           results += [result]

        display_results = list(map(lambda x: [int(x[1] == '通過測試'), x[0], x[1]], results))

        return render_template('question_number_forum.html', title=("KCOJ - " + question_number), userid=userid, gravatar=get_gravatar(users[userid]['email'], 30), question_number=question_number, question_title=question['title'], content=content, results=display_results)
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
    userid = current_user.get_id()

    content = users[userid]['api'].show_question(number)

    question_number = number

    questions = {}
    int_questions = users[userid]['api'].list_questions()

    for number in int_questions:
        if number in ext_questions:
            questions[number] = {
                'title': ext_questions[number]['title'],
                'description': ext_questions[number]['description'],
                'tag': ext_questions[number]['tag'],
                'deadline': int_questions[number][0],
                'submit': int_questions[number][1],
                'status': int_questions[number][2],
                'language': int_questions[number][3],
                'results': users[userid]['api'].list_results(number, userid),
            }
        else:
            questions[number] = {
                'title': '未命名',
                'description': '沒有敘述',
                'tag': '',
                'deadline': int_questions[number][0],
                'submit': int_questions[number][1],
                'status': int_questions[number][2],
                'language': int_questions[number][3],
                'results': users[userid]['api'].list_results(number, userid),
            }

    for number in questions:
        if len(questions[number]['results']) == 0:
            questions[number]['result'] = 2
        else:
            results = []
            raw = questions[number]['results']
            for result in raw:
               results += [result[1]]

            results = list(map(lambda x: x == '通過測試', results))

            if False in results:
                questions[number]['result'] = 0
            else:
                questions[number]['result'] = 1

    question = questions[question_number]

    results = []
    raw = question['results']
    for result in raw:
       results += [result]

    display_results = list(map(lambda x: [int(x[1] == '通過測試'), x[0], x[1]], results))

    return render_template('question_number_passed.html', title=("KCOJ - " + question_number), userid=userid, gravatar=get_gravatar(users[userid]['email'], 30), question_number=question_number, question_title=question['title'], content=content, results=display_results, passers=users[current_user.get_id()]['api'].list_passers(number))

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