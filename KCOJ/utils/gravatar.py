import hashlib


class Gravatar:
    def __init__(self, email: str):
        if email:
            self.__email = email
        else:
            self.__email = "example@example.com"
        self.__size = 30

    def set_size(self, size: int):
        self.__size = size
        return self

    @property
    def image(self) -> str:
        """
        取得特定用戶 Gravatar 上的大頭貼網址
        """
        url = 'https://s.gravatar.com/avatar/{PROFILE}?size={SIZE}'.format(
            PROFILE=hashlib.md5(bytes(self.__email, 'utf-8')).hexdigest(),
            SIZE=str(self.__size))
        return url
