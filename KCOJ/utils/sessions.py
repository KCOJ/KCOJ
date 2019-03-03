from KCOJ_api import KCOJ

from ..config import CONFIG

sessions = {}


def getSession(useruid: str):
    if not useruid in sessions:
        sessions[useruid] = KCOJ(CONFIG['TARGET']['URL'])

    return sessions[useruid]

def revokeSession(useruid: str):
    sessions.pop(useruid)