#!/usr/bin/env python3

from flask import Flask, request, Response
from flask_login import LoginManager

# 初始化 Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'KuoKuoKuo'
# 初始化 Flask 登入管理員
login_manager = LoginManager(app)

# 主畫面
@app.route('/', methods=['GET'], strict_slashes=False)
def root_page():
    # TODO: 如果沒登入就跳轉到 /login。

    # TODO: 顯示主畫面
    return "GET /"

# 登入畫面
@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login_page():
    if request.method == 'GET':
        # TODO: 顯示登入畫面。
        return "GET /login"
    if request.method == 'POST':
        # TODO: 登入成功則跳轉到 /，否則顯示登入畫面並加上失敗提示字串。
        return "POST /login"

# 個人資料畫面
@app.route('/user', methods=['GET', 'POST'], strict_slashes=False)
def user_page():
    # TODO: 如果沒登入就跳轉到 /login。

    if request.method == 'GET':
        # TODO: 顯示 Gravatar 大頭貼和變更密碼的欄位，
        # 不過在顯示別人的資料（?id=）時不會出現變更密碼的欄位。
        return "GET /user"
    if request.method == 'POST':
        # TODO: 判斷舊密碼是否正確，正確的話更新資料。
        return "POST /user"

# 技巧文庫畫面
@app.route('/docs', methods=['GET'], strict_slashes=False)
def docs_page():
    # TODO: 如果沒登入就跳轉到 /login。

    # TODO: 顯示文件列表。
    return "GET /docs"

# 技巧文件畫面
@app.route('/docs/<name>', methods=['GET'], strict_slashes=False)
def docs_name_page(name):
    # TODO: 如果沒登入就跳轉到 /login。

    # TODO: 顯示該篇文件。
    return "GET /docs/" + name

# 作業題庫畫面
@app.route('/question', methods=['GET'], strict_slashes=False)
def question_page():
    # TODO: 如果沒登入就跳轉到 /login。

    # TODO: 顯示題目列表。
    return "GET /question"

# 作業題目畫面
@app.route('/question/<number>', methods=['GET', 'POST'], strict_slashes=False)
def question_number_page(number):
    # TODO: 如果沒登入就跳轉到 /login。

    if request.method == 'GET':
        # TODO: 顯示題目內容。
        return "GET /question/" + number
    if request.method == 'POST':
        # TODO: 提交程式碼內容到作業網站。
        return "POST /question/" + number

# 作業討論畫面
@app.route('/question/<number>/chat', methods=['GET', 'POST'], strict_slashes=False)
def question_number_chat_page(number):
    # TODO: 如果沒登入就跳轉到 /login。

    if request.method == 'GET':
        # TODO: 顯示討論內容。
        return "GET /question/" + number + "chat"
    if request.method == 'POST':
        # TODO: 新增討論文章。
        return "POST /question/" + number + "chat"

# 作業通過畫面
@app.route('/question/<number>/passed', methods=['GET'], strict_slashes=False)
def question_number_passed_page(number):
    # TODO: 如果沒登入就跳轉到 /login。

    # TODO: 顯示通過名單。
    return "GET /question/" + number + "passed"

def main():
    app.run(port=11711, threaded=True, debug=True)

if __name__ == '__main__':
    main()