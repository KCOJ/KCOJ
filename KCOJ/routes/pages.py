import os
import sys
from flask import Blueprint, request, redirect, render_template
from flask_login import login_required, login_user, logout_user, current_user
from KCOJ_api import KCOJ

from ..utils.sessions import get_session
from ..utils.gravatar import Gravatar
from ..models.user import User
from ..controllers.keep_active import keep_active
from ..controllers.index_page import main as index_page
from ..controllers.login_page import main as login_page
from ..controllers.login import main as login
from ..controllers.user_page import main as user_page
from ..question import QUESTIONS
from ..config import CONFIG

app = Blueprint('pages', __name__)

# 由外部提供題目標題、敘述、標籤
ext_questions = QUESTIONS


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
    user = User(useruid)
    session = get_session(useruid)

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    # 取得使用者 ID
    userid = user.userid

    if request.method == 'GET':
        # 取得要查看的使用者 ID
        target_id = request.args.get('userid')

        # 顯示個資畫面
        return user_page(useruid, target_id)

    if request.method == 'POST':
        # 取得要更新的資訊
        old_passwd = request.form['old_passwd']
        new_passwd = request.form['new_passwd']
        email = request.form['email']
        # 登入交作業網站
        api = KCOJ(CONFIG['TARGET']['URL'])
        api.login(userid, old_passwd,
                  api.courses.index(user.course) + 1)
        # 確認是否登入成功
        if api.active:
            # 如果要變更密碼
            if new_passwd != '':
                api.update_password(new_passwd)
                user.passwd = new_passwd
            # 如果要變更 Email
            if email != '':
                user.email = email

        return redirect('/user')


@app.route('/question', methods=['GET'], strict_slashes=False)
@login_required
def question_page():
    """
    作業題庫畫面
    """
    # 取得使用者物件
    useruid = current_user.get_id()
    user = User(useruid)
    session = get_session(useruid)

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    # 取得使用者 ID
    userid = user.userid

    # 所有題目列表
    questions = {}

    # 取得 API 裡的題目資訊
    api_question = session.get_question()
    for num in api_question:
        questions[num] = {
            'title': '未命名',
            'description': '沒有敘述',
            'tag': '',
            'deadline': api_question[num]['deadline'],
            'submit': '期限已到' if api_question[num]['expired'] else '期限未到',
            'status': '已繳' if api_question[num]['status'] else '未繳',
            'language': api_question[num]['language'],
            'results': session.list_results(num, userid),
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
        title="KCOJ - " + user.course + " 題庫",
        userid=userid,
        profile_image=Gravatar(user.email).set_size(30).image,
        course=user.course,
        opened_questions=opened,
        closed_questions=closed)


@app.route('/question/<number>/content', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/question/<number>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def question_number_page(number):
    """
    作業題目畫面
    """
    # 取得使用者物件
    useruid = current_user.get_id()
    user = User(useruid)
    session = get_session(useruid)

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    # 取得使用者 ID
    userid = user.userid

    if request.method == 'GET':
        # 顯示題目列表
        questions = {}

        # 取得 API 裡的題目資訊
        api_question = session.get_question()
        for num in api_question:
            questions[num] = {
                'title': '未命名',
                'description': '沒有敘述',
                'tag': '',
                'deadline': api_question[num]['deadline'],
                'submit': '期限已到' if api_question[num]['expired'] else '期限未到',
                'status': '已繳' if api_question[num]['status'] else '未繳',
                'language': api_question[num]['language'],
                'results': session.list_results(num, userid),
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

        content = session.get_question_content(number)

        return render_template(
            'question_number.j2',
            title=("KCOJ - " + user.course + " " + number),
            userid=userid,
            profile_image=Gravatar(user.email).set_size(30).image,
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
        language = session.get_question()[number]['language']
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
        session.delete_question_answer(number)
        # 上傳並判斷是否成功
        if session.post_question_answer(number, "Send from KCOJ", filename):
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
    # 取得使用者物件
    useruid = current_user.get_id()
    user = User(useruid)
    session = get_session(useruid)

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    # 取得使用者 ID
    userid = user.userid

    if request.method == 'GET':
        # 顯示題目列表
        questions = {}

        # 取得 API 裡的題目資訊
        api_question = session.get_question()
        for num in api_question:
            questions[num] = {
                'title': '未命名',
                'description': '沒有敘述',
                'tag': '',
                'deadline': api_question[num]['deadline'],
                'submit': '期限已到' if api_question[num]['expired'] else '期限未到',
                'status': '已繳' if api_question[num]['status'] else '未繳',
                'language': api_question[num]['language'],
                'results': session.list_results(num, userid),
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

        content = session.get_question_content(number)

        return render_template(
            'question_number_forum.j2',
            title=("KCOJ - " + user.course + " " + number),
            userid=userid,
            profile_image=Gravatar(user.email).set_size(30).image,
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
    # 取得使用者物件
    useruid = current_user.get_id()
    user = User(useruid)
    session = get_session(useruid)

    # 嘗試保持登入狀態
    if not keep_active(useruid):
        logout_user()

    # 取得使用者 ID
    userid = user.userid

    # 顯示題目列表
    questions = {}

    # 取得 API 裡的題目資訊
    api_question = session.get_question()
    for num in api_question:
        questions[num] = {
            'title': '未命名',
            'description': '沒有敘述',
            'tag': '',
            'deadline': api_question[num]['deadline'],
            'submit': '期限已到' if api_question[num]['expired'] else '期限未到',
            'status': '已繳' if api_question[num]['status'] else '未繳',
            'language': api_question[num]['language'],
            'results': session.list_results(num, userid),
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

    content = session.get_question_content(number)

    passers_info = {}
    passers = session.get_question_passers(number)
    for passer in passers:
        try:
            passer_email = User(passer + user.course).email
        except Exception:   # TODO: I don't know!
            passer_email = ''

        passers_info[passer] = Gravatar(passer_email).set_size(25).image

    return render_template(
        'question_number_passed.j2',
        title=("KCOJ - " + user.course + " " + number),
        userid=userid,
        profile_image=Gravatar(user.email).set_size(30).image,
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
