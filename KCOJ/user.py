from flask_login import UserMixin
from pymongo import MongoClient

# 連結 MongoDB
db = MongoClient().kcoj


class User(UserMixin):
    def __init__(self, useruid: str):
        super()
        self.id = useruid

    @staticmethod
    def is_exist(userid: str):
        return db.users.find_one({'uid': userid})

    @property
    def userid(self) -> str:
        obj = db.users.find_one({'uid': self.id})
        return obj and obj['userid']

    @userid.setter
    def userid(self, userid):
        db.users.update({'uid': self.id}, {
                        "$set": {"userid": userid}}, upsert=True)

    @property
    def passwd(self) -> str:
        obj = db.users.find_one({'uid': self.id})
        return obj and obj['passwd']

    @passwd.setter
    def passwd(self, passwd):
        db.users.update({'uid': self.id}, {
                        "$set": {"passwd": passwd}}, upsert=True)

    @property
    def course(self) -> str:
        obj = db.users.find_one({'uid': self.id})
        return obj and obj['course']

    @course.setter
    def course(self, course):
        db.users.update({'uid': self.id}, {
                        "$set": {"course": course}}, upsert=True)

    @property
    def email(self) -> str:
        obj = db.users.find_one({'uid': self.id})
        return obj and obj['email']

    @email.setter
    def email(self, email):
        db.users.update({'uid': self.id}, {
                        "$set": {"email": email}}, upsert=True)
