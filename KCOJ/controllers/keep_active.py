from ..models.user import User
from ..utils.sessions import get_session


def keep_active(useruid: str):
    """
    試著保持著登入狀態
    """
    # 取得使用者物件
    user = User(useruid)
    session = get_session(useruid)

    # 確認登入狀態
    if session.active:
        return True

    # 嘗試重新登入
    try:
        session.login(user.userid,
                      user.passwd,
                      session.courses.index(user.course) + 1)
    except IndexError:
        return False

    # 直接回傳登入狀態
    return session.active