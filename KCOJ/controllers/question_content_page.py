from flask import render_template
from ..models.user import User
from ..utils.sessions import get_session
from ..utils.gravatar import Gravatar


def main(useruid: str, number: str):
    """
    題目內容畫面
    """
    user = User(useruid)
    session = get_session(useruid)

    question = session.get_question()[number]

    question['title'] = "未命名"
    question['description'] = question['deadline']  # TODO: Correct name in template
    question['tag'] = [question['language']]        # TODO: Correct name in template
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

    test_cases = []
    for result in question['results']:
        test_cases.append([int(result[1] == '通過測試'), result[0], result[1]])

    content = session.get_question_content(number)

    return render_template(
        'question_content.j2',
        title=("KCOJ - " + user.course + " " + number),
        userid=user.userid,
        profile_image=Gravatar(user.email).set_size(30).image,
        question_number=number,
        question_title=question['title'],
        question_content=content,
        question_cases=test_cases,
        question_light=question['light'])
