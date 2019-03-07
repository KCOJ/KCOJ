from KCOJ_api import KCOJ

from ..config import CONFIG

sessions = {}


def get_empty_session():
    return KCOJ(CONFIG['TARGET']['URL'])


def get_session(useruid: str):
    if not useruid in sessions:
        sessions[useruid] = KCOJ(CONFIG['TARGET']['URL'])

    return sessions[useruid]
