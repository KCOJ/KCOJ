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

    questions = {}

    api_question = session.get_question()
    for number in api_question:
        questions[number] = {
            'title': '未命名',
            'description': '沒有敘述',
            'tag': '',
            'deadline': api_question[number]['deadline'],
            'expired': api_question[number]['expired'],
            'status': '已繳' if api_question[number]['status'] else '未繳',
            'language': api_question[number]['language'],
            'results': session.list_results(number, user.userid),
        }

    closed = {}
    opened = {}

    for num in questions:
        # 判斷題目是否關閉
        if questions[num]['expired']:
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
        userid=user.userid,
        profile_image=Gravatar(user.email).set_size(30).image,
        course=user.course,
        opened_questions=opened,
        closed_questions=closed)
