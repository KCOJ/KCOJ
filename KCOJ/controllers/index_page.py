from flask import render_template
from ..models.user import User
from ..utils.sessions import get_session
from ..utils.gravatar import Gravatar


def main(useruid):
    """
    首頁畫面
    """
    user = User(useruid)
    session = get_session(useruid)

    return render_template(
        'index.j2',
        title="KCOJ - 首頁",
        userid=user.userid,
        profile_image=Gravatar(user.email).set_size(30).image,
        notices=session.get_notices())
