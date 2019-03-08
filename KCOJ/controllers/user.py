from flask import redirect, render_template
from flask_login import login_user
from ..models.user import User
from ..utils.sessions import get_session, get_empty_session


def main(useruid: str, old_passwd: str, new_passwd: str, email: str):
    """
    修改個資
    """
    user = User(useruid)
    session = get_empty_session()

    session.login(
        user.userid, old_passwd, session.courses.index(user.course) + 1)

    if session.active:
        session = get_session(useruid)

        if new_passwd:
            session.update_password(new_passwd)
            user.passwd = new_passwd

        if email:
            user.email = email

    return redirect('/user')
