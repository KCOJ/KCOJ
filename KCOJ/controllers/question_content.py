import os
import sys
from flask import render_template
from ..models.user import User
from ..utils.sessions import get_session
from .question_content_page import main as question_content_page


def main(useruid: str, number: str, code: str):
    """
    上傳程式碼
    """
    user = User(useruid)
    session = get_session(useruid)

    question = session.get_question()[number]

    def file_type(language: str) -> str:
        if language == 'C':
            return 'c'
        if language == 'C#':
            return 'cs'
        if language == 'Java':
            return 'java'
        if language == 'Python':
            return 'py'
        return 'txt'

    # 定義檔名
    file_path = "{directory}/{file_name}.{file_type}".format(
        directory=sys.path[0] + '/KCOJ/db',
        file_name=user.userid + number,
        file_type=file_type(question['language']))

    # 把程式碼儲存成文字檔
    with open(file_path, 'w') as f:
        f.write(code)

    # 刪除原本的程式碼
    session.delete_question_answer(number)

    # 上傳程式碼
    session.post_question_answer(number, "Send from KCOJ", file_path)

    # 移除已上傳的程式碼
    os.remove(file_path)

    return question_content_page(useruid, number, alert="上傳成功！")
