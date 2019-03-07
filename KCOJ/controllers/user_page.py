from flask import render_template
from ..models.user import User
from ..utils.gravatar import Gravatar


def main(useruid: str, targe_id: str):
    """
    個資畫面
    """
    user = User(useruid)

    if not targe_id:
        targe_id = user.userid

    target = User(targe_id + user.course)

    return render_template(
        'user.j2',
        title=("KCOJ - " + target.userid),
        userid=user.userid,
        profile_image=Gravatar(user.email).set_size(30).image,
        view_userid=target.userid,
        view_email=target.email,
        view_gravatar=Gravatar(target.email).set_size(200).image,
        no_me=(user.userid != target.userid))
