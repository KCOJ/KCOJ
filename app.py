#!/usr/bin/env python3

from base64 import b64encode
from os.path import isdir, isfile
import os
import sys
import hashlib

from flask import Flask, request, redirect, render_template
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from KCOJ_api import KCOJ

from config import CONFIG
from user import User

# 自動產生 instance 的 key
if not isdir(sys.path[0] + '/instance'):
    os.mkdir(sys.path[0] + '/instance')
if not isfile(sys.path[0] + '/instance/config.py'):
    with open(sys.path[0] + '/instance/config.py', 'w') as f:
        f.write('SECRET_KEY = \'' +
                b64encode(os.urandom(8)).decode('utf-8') + '\'')

# 初始化 Flask
app = Flask(__name__,
            template_folder='views',
            instance_relative_config=True)
app.config.from_pyfile('config.py')

# 初始化 Flask 登入管理員
login_manager = LoginManager(app)


# 儲存使用者資訊
users = {}


@login_manager.user_loader
def user_loader(userid):
    if User.is_exist(userid):
        return User(userid)
    else:
        return None


# 由外部提供題目標題、敘述、標籤
from question import QUESTIONS
ext_questions = QUESTIONS


def keep_login():
    """
    試著保持著登入狀態
    """
    # 取得使用者 UID
    useruid = current_user.get_id()
    # 建立使用者物件
    users[useruid] = User(useruid)
    users[useruid].api = users[useruid].api or KCOJ(CONFIG['TARGET']['URL'])
    # 確認是否是登入狀態
    if users[useruid].api.active:
        return True
    # 嘗試登入
    try:
        users[useruid].api.login(users[useruid].userid,
                                 users[useruid].passwd,
                                 users[useruid].api.courses.index(users[useruid].course) + 1)
    except IndexError:
        return False
    # 回傳狀態
    return users[useruid].api.active


def get_gravatar(email, size):
    """
    取得 Gravatar 上的大頭貼
    """
    # 直接回傳網址
    return 'https://s.gravatar.com/avatar/{PROFILE}?size={SIZE}'.format(
        PROFILE=hashlib.md5(bytes(email, 'utf-8')).hexdigest(), SIZE=str(size))


@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
def index_page():
    """
    主畫面
    """
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()
    # 取得使用者 UID
    useruid = current_user.get_id()
    # 顯示主畫面
    return render_template(
        'index.j2',
        title="KCOJ - 首頁",
        userid=users[useruid].userid,
        profile_image=get_gravatar(users[useruid].email, 30),
        notices=users[useruid].api.get_notices())


@login_manager.unauthorized_handler
def login_failed_page():
    """
    登入失敗轉址回登入畫面
    """
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login_page():
    """
    登入畫面
    """
    # 使用 API
    api = KCOJ(CONFIG['TARGET']['URL'])

    if request.method == 'GET':
        # 顯示登入畫面
        return render_template(
            'login.j2',
            title="KCOJ - 登入",
            courses=api.courses)

    if request.method == 'POST':
        # 取得登入資訊
        userid = request.form['userid']
        passwd = request.form['passwd']
        course = request.form['course']
        useruid = userid + course
        # 登入交作業網站
        api.login(userid, passwd, api.courses.index(course) + 1)
        # 確認是否登入成功
        if api.active:
            # 登入成功
            login_user(User(useruid))
            # 將登入資訊儲存起來
            if useruid in users:
                users[useruid].api = api
            else:
                users[useruid] = User(useruid)
                users[useruid].userid = userid
                users[useruid].passwd = passwd
                users[useruid].course = course
                users[useruid].email = ''
                users[useruid].api = api
            return redirect('/')
        else:
            # 顯示登入畫面含錯誤訊息
            return render_template(
                'login.j2',
                title="KCOJ - 登入",
                courses=api.courses,
                error_message="登入失敗，請檢查輸入的資訊是否有誤！")


@app.route('/user', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def user_page():
    """
    個人資料畫面
    """
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()
    # 取得使用者 UID
    useruid = current_user.get_id()
    # 取得使用者 ID
    userid = users[useruid].userid

    if request.method == 'GET':
        # 取得要查看的使用者 ID
        try:
            view_userid = request.args['userid']
        except KeyError:
            view_userid = userid
        # 取得要查看的使用者 Email
        try:
            view_email = users[view_userid + users[useruid].course].email
        except KeyError:
            if view_userid == userid:
                # 如果查看是自己的話就顯示自己的 Email
                view_email = users[useruid].email
            else:
                view_email = ''

        return render_template(
            'user.j2',
            title=("KCOJ - " + view_userid),
            userid=userid,
            profile_image=get_gravatar(users[useruid].email, 30),
            view_userid=view_userid,
            view_email=view_email,
            view_gravatar=get_gravatar(view_email, 200),
            no_me=(userid != view_userid))

    if request.method == 'POST':
        # 取得要更新的資訊
        old_passwd = request.form['old_passwd']
        new_passwd = request.form['new_passwd']
        email = request.form['email']
        # 登入交作業網站
        api = KCOJ(CONFIG['TARGET']['URL'])
        api.login(userid, old_passwd,
                  api.courses.index(users[useruid].course) + 1)
        # 確認是否登入成功
        if api.active:
            # 如果要變更密碼
            if new_passwd != '':
                api.update_password(new_passwd)
                users[useruid].passwd = new_passwd
            # 如果要變更 Email
            if email != '':
                users[useruid].email = email

        return redirect('/user')


@app.route('/question', methods=['GET'], strict_slashes=False)
@login_required
def question_page():
    """
    作業題庫畫面
    """
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()
    # 取得使用者 UID
    useruid = current_user.get_id()
    # 取得使用者 ID
    userid = users[useruid].userid

    # 所有題目列表
    questions = {}

    # 取得 API 裡的題目資訊
    api_question = users[useruid].api.get_question()
    for num in api_question:
        questions[num] = {
            'title': '未命名',
            'description': '沒有敘述',
            'tag': '',
            'deadline': api_question[num]['deadline'],
            'submit': '期限已到' if api_question[num]['expired'] else '期限未到',
            'status': '已繳' if api_question[num]['status'] else '未繳',
            'language': api_question[num]['language'],
            'results': users[useruid].api.list_results(num, userid),
        }

    # 取得外部提供的題目資訊
    for num in ext_questions:
        # 如果 API 沒有這題就跳過
        if not num in api_question:
            continue
        # 新增外部資訊
        questions[num]['title'] = ext_questions[num]['title']
        questions[num]['description'] = ext_questions[num]['description']
        questions[num]['tag'] = ext_questions[num]['tag']

    closed = {}
    opened = {}

    for num in questions:
        # 判斷題目是否關閉
        if questions[num]['submit'] == '期限已到':
            # 收錄至已關閉的題目
            closed[num] = questions[num]
            if len(closed[num]['results']) == 0:
                # 題目燈號為未繳交
                closed[num]['light'] = 2
            else:
                results = []
                for result in closed[num]['results']:
                    results += [result[1] == '通過測試']
                # 題目燈號為已／未繳交
                closed[num]['light'] = 0 if False in results else 1
        else:
            # 收錄至仍開啟的題目
            opened[num] = questions[num]
            if len(opened[num]['results']) == 0:
                # 題目燈號為未繳交
                opened[num]['light'] = 2
            else:
                results = []
                for result in opened[num]['results']:
                    results += [result[1] == '通過測試']
                # 題目燈號為已／未繳交
                opened[num]['light'] = 0 if False in results else 1

    return render_template(
        'question.j2',
        title="KCOJ - " + users[useruid].course + " 題庫",
        userid=userid,
        profile_image=get_gravatar(users[useruid].email, 30),
        course=users[useruid].course,
        opened_questions=opened,
        closed_questions=closed)


@app.route('/question/<number>/content', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/question/<number>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def question_number_page(number):
    """
    作業題目畫面
    """
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()
    # 取得使用者 UID
    useruid = current_user.get_id()
    # 取得使用者 ID
    userid = users[useruid].userid

    if request.method == 'GET':
        # 顯示題目列表
        questions = {}

        # 取得 API 裡的題目資訊
        api_question = users[useruid].api.get_question()
        for num in api_question:
            questions[num] = {
                'title': '未命名',
                'description': '沒有敘述',
                'tag': '',
                'deadline': api_question[num]['deadline'],
                'submit': '期限已到' if api_question[num]['expired'] else '期限未到',
                'status': '已繳' if api_question[num]['status'] else '未繳',
                'language': api_question[num]['language'],
                'results': users[useruid].api.list_results(num, userid),
            }

        # 取得外部提供的題目資訊
        for num in ext_questions:
            # 如果 API 沒有這題就跳過
            if not num in api_question:
                continue
            questions[num]['title'] = ext_questions[num]['title']
            questions[num]['description'] = ext_questions[num]['description']
            questions[num]['tag'] = ext_questions[num]['tag']

        # 選擇特定的題目
        question = questions[number]

        if len(question['results']) == 0:
            # 題目燈號為未繳交
            question['light'] = 2
        else:
            results = []
            for result in question['results']:
                results += [result[1] == '通過測試']
            # 題目燈號為已／未繳交
            question['light'] = 0 if False in results else 1

        test_cases = []
        for result in question['results']:
            test_cases.append([int(result[1] == '通過測試'), result[0], result[1]])

        content = users[useruid].api.get_question_content(number)

        return render_template(
            'question_number.j2',
            title=("KCOJ - " + users[useruid].course + " " + number),
            userid=userid,
            profile_image=get_gravatar(users[useruid].email, 30),
            question_number=number,
            question_title=question['title'],
            question_content=content,
            question_cases=test_cases,
            question_light=question['light'])

    if request.method == 'POST':
        # 取得使用者程式碼
        code = request.form['code']
        # 定義檔名
        filename = userid + number
        language = users[useruid].api.get_question()[number]['language']
        if language == 'Python':
            filename += '.py'
        if language == 'Java':
            filename += '.java'
        if language == 'C#':
            filename += '.cs'
        if language == 'C':
            filename += '.c'
        # 把程式碼儲存成文字檔
        with open(sys.path[0] + '/' + filename, 'w') as f:
            f.write(code)
        # 刪除原本的程式碼
        users[useruid].api.delete_question_answer(number)
        # 上傳並判斷是否成功
        if users[useruid].api.post_question_answer(number, "Send from KCOJ", filename):
            # TODO: 提示上傳成功
            pass
        else:
            # TODO: 提示上傳失敗
            pass

        # 移除上傳的檔案
        os.remove(filename)
        # 回到題目頁
        return redirect('/question/' + number)


@app.route('/question/<number>/forum', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def question_number_forum_page(number):
    """
    作業討論畫面
    """
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()
    # 取得使用者 UID
    useruid = current_user.get_id()
    # 取得使用者 ID
    userid = users[useruid].userid

    if request.method == 'GET':
        # 顯示題目列表
        questions = {}

        # 取得 API 裡的題目資訊
        api_question = users[useruid].api.get_question()
        for num in api_question:
            questions[num] = {
                'title': '未命名',
                'description': '沒有敘述',
                'tag': '',
                'deadline': api_question[num]['deadline'],
                'submit': '期限已到' if api_question[num]['expired'] else '期限未到',
                'status': '已繳' if api_question[num]['status'] else '未繳',
                'language': api_question[num]['language'],
                'results': users[useruid].api.list_results(num, userid),
            }

        # 取得外部提供的題目資訊
        for num in ext_questions:
            # 如果 API 沒有這題就跳過
            if not num in api_question:
                continue
            questions[num]['title'] = ext_questions[num]['title']
            questions[num]['description'] = ext_questions[num]['description']
            questions[num]['tag'] = ext_questions[num]['tag']

        # 選擇特定的題目
        question = questions[number]

        if len(question['results']) == 0:
            # 題目燈號為未繳交
            question['light'] = 2
        else:
            results = []
            for result in question['results']:
                results += [result[1] == '通過測試']
            # 題目燈號為已／未繳交
            question['light'] = 0 if False in results else 1

        test_cases = []
        for result in question['results']:
            test_cases.append([int(result[1] == '通過測試'), result[0], result[1]])

        content = users[useruid].api.get_question_content(number)

        return render_template(
            'question_number_forum.j2',
            title=("KCOJ - " + users[useruid].course + " " + number),
            userid=userid,
            profile_image=get_gravatar(users[useruid].email, 30),
            question_number=number,
            question_title=question['title'],
            question_content=content,
            question_cases=test_cases,
            question_light=question['light'])

    if request.method == 'POST':
        # TODO: 新增討論文章。
        return "POST /question/" + number + "chat"


@app.route('/question/<number>/passed', methods=['GET'], strict_slashes=False)
@login_required
def question_number_passed_page(number):
    """
    作業通過畫面
    """
    # 嘗試保持登入狀態
    if not keep_login():
        logout_user()
    # 取得使用者 UID
    useruid = current_user.get_id()
    # 取得使用者 ID
    userid = users[useruid].userid

    # 顯示題目列表
    questions = {}

    # 取得 API 裡的題目資訊
    api_question = users[useruid].api.get_question()
    for num in api_question:
        questions[num] = {
            'title': '未命名',
            'description': '沒有敘述',
            'tag': '',
            'deadline': api_question[num]['deadline'],
            'submit': '期限已到' if api_question[num]['expired'] else '期限未到',
            'status': '已繳' if api_question[num]['status'] else '未繳',
            'language': api_question[num]['language'],
            'results': users[useruid].api.list_results(num, userid),
        }

    # 取得外部提供的題目資訊
    for num in ext_questions:
        # 如果 API 沒有這題就跳過
        if not num in api_question:
            continue
        questions[num]['title'] = ext_questions[num]['title']
        questions[num]['description'] = ext_questions[num]['description']
        questions[num]['tag'] = ext_questions[num]['tag']

    # 選擇特定的題目
    question = questions[number]

    if len(question['results']) == 0:
        # 題目燈號為未繳交
        question['light'] = 2
    else:
        results = []
        for result in question['results']:
            results += [result[1] == '通過測試']
        # 題目燈號為已／未繳交
        question['light'] = 0 if False in results else 1

    test_cases = []
    for result in question['results']:
        test_cases.append([int(result[1] == '通過測試'), result[0], result[1]])

    content = users[useruid].api.get_question_content(number)

    passers_info = {}
    passers = users[useruid].api.get_question_passers(number)
    for passer in passers:
        try:
            passer_email = users[passer + users[useruid].course]['email']
        except KeyError:
            passer_email = ''

        passers_info[passer] = get_gravatar(passer_email, 25)

    return render_template(
        'question_number_passed.j2',
        title=("KCOJ - " + users[useruid].course + " " + number),
        userid=userid,
        profile_image=get_gravatar(users[useruid].email, 30),
        question_number=number,
        question_title=question['title'],
        question_content=content,
        question_cases=test_cases,
        question_light=question['light'],
        passers=passers_info)


@app.route('/logout', methods=['GET'], strict_slashes=False)
@login_required
def logout_nopage():
    """
    登出系統
    """
    logout_user()
    return redirect('/login')


def main():
    # 開啟伺服器
    app.run(port=11711, threaded=True)


if __name__ == '__main__':
    main()
