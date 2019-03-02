import os
import sys
from os.path import isdir, isfile
from base64 import b64encode


def main():
    # 產生 instance 的 key
    if not isdir(sys.path[0] + '/instance'):
        os.mkdir(sys.path[0] + '/instance')
    if not isfile(sys.path[0] + '/instance/config.py'):
        with open(sys.path[0] + '/instance/config.py', 'w') as f:
            f.write('SECRET_KEY = \'{SECRET_KEY}\''.format(
                SECRET_KEY=b64encode(os.urandom(8)).decode('utf-8')))

    # 開啟伺服器
    from KCOJ import app
    app.run(port=11711, threaded=True)


if __name__ == '__main__':
    main()
