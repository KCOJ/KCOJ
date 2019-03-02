import sys
import sqlite3
from flask_login import UserMixin

db_file = sys.path[0] + '/KCOJ/db/KCOJ.db'


class User(UserMixin):
    def __init__(self, useruid: str):
        super().__init__()

        self.__db = sqlite3.connect(db_file)

        if not self.is_exist(useruid):
            cursor = self.__db.cursor()
            cursor.execute('INSERT INTO users (useruid) VALUES (?)',
                           [useruid])
            self.__db.commit()

        self.id = useruid
        self.api = None

    @staticmethod
    def create_table():
        db = sqlite3.connect(db_file)
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            useruid TEXT NOT NULL,
            userid TEXT,
            passwd TEXT,
            course TEXT,
            email TEXT,
            PRIMARY KEY (useruid)
            )''')

    @staticmethod
    def is_exist(useruid: str):
        db = sqlite3.connect(db_file)
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE useruid = ?',
                       [useruid])

        return cursor.fetchone()[0] != 0

    @property
    def useruid(self) -> str:
        cursor = self.__db.cursor()
        cursor.execute('SELECT useruid FROM users WHERE useruid = ?',
                       [self.id])

        return cursor.fetchone()[0]

    @property
    def userid(self) -> str:
        cursor = self.__db.cursor()
        cursor.execute('SELECT userid FROM users WHERE useruid = ?',
                       [self.id])

        return cursor.fetchone()[0]

    @userid.setter
    def userid(self, userid):
        cursor = self.__db.cursor()
        cursor.execute('UPDATE users SET userid = ? WHERE useruid = ?',
                       [userid, self.id])
        self.__db.commit()

    @property
    def passwd(self) -> str:
        cursor = self.__db.cursor()
        cursor.execute('SELECT passwd FROM users WHERE useruid = ?',
                       [self.id])

        return cursor.fetchone()[0]

    @passwd.setter
    def passwd(self, passwd):
        cursor = self.__db.cursor()
        cursor.execute('UPDATE users SET passwd = ? WHERE useruid = ?',
                       [passwd, self.id])
        self.__db.commit()

    @property
    def course(self) -> str:
        cursor = self.__db.cursor()
        cursor.execute('SELECT course FROM users WHERE useruid = ?',
                       [self.id])

        return cursor.fetchone()[0]

    @course.setter
    def course(self, course):
        cursor = self.__db.cursor()
        cursor.execute('UPDATE users SET course = ? WHERE useruid = ?',
                       [course, self.id])
        self.__db.commit()

    @property
    def email(self) -> str:
        cursor = self.__db.cursor()
        cursor.execute('SELECT email FROM users WHERE useruid = ?',
                       [self.id])

        return cursor.fetchone()[0]

    @email.setter
    def email(self, email):
        cursor = self.__db.cursor()
        cursor.execute('UPDATE users SET email = ? WHERE useruid = ?',
                       [email, self.id])
        self.__db.commit()
