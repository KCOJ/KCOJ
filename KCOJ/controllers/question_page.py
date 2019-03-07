from flask import render_template
from ..models.user import User
from ..utils.sessions import get_session
from ..utils.gravatar import Gravatar


def main(useruid: str):
    """
    題庫畫面
    """
    user = User(useruid)
    session = get_session(useruid)

    closed = {}
    opened = {}

    for number, question in session.get_question().items():
        question['title'] = "未命名"
        question['description'] = "沒有敘述"
        question['tag'] = []
        question['results'] = session.list_results(number, user.userid)

        if len(question['results']) == 0:
            # 題目燈號為未繳交
            question['light'] = 2
        else:
            results = []
            for result in question['results']:
                results += [result[1] == '通過測試']
            # 題目燈號為已／未通過
            question['light'] = 0 if False in results else 1

        # 判斷題目是否關閉
        if question['expired']:
            closed[number] = question
        else:
            opened[number] = question

    return render_template(
        'question.j2',
        title="KCOJ - " + user.course + " 題庫",
        userid=user.userid,
        profile_image=Gravatar(user.email).set_size(30).image,
        course=user.course,
        opened_questions=opened,
        closed_questions=closed)
