from flask import render_template
from ..models.user import User
from ..utils.sessions import get_empty_session
from ..utils.gravatar import Gravatar


def main():
    """
    登入畫面
    """
    session = get_empty_session()

    return render_template(
            'login.j2',
            title="KCOJ - 登入",
            courses=session.courses)
