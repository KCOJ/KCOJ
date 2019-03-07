from flask import redirect, render_template
from flask_login import login_user
from ..models.user import User
from ..utils.sessions import get_empty_session


def main(userid: str, passwd: str, course: str):
    """
    登入畫面
    """
    session = get_empty_session()

    session.login(userid, passwd, session.courses.index(course) + 1)

    if session.active:
        useruid = userid + course

        login_user(User(useruid))

        user = User(useruid)
        user.userid = userid
        user.passwd = passwd
        user.course = course
        user.email = ''

        return redirect('/')

    else:
        return render_template(
            'login.j2',
            title="KCOJ - 登入",
            courses=session.courses,
            error_message="登入失敗，請檢查輸入的資訊是否有誤！")
