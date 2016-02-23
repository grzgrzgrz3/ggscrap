import time

import deathbycaptcha
from .utils import config

TRIES = 60
INTERVAL = 1


class CaptchaClient(object):

    def resolve(self, path):
        raise NotImplementedError()

    def report(self, captcha_id):
        raise NotImplementedError()


class DeathByCaptchaClient(CaptchaClient):
    _deathbycaptcha_client = None

    def __init__(self):
        self._username = config.get('captcha', 'username')
        self._password = config.get('captcha', 'password')

    def resolve(self, path):
        for x in range(TRIES):
            try:
                result = self._client.decode(path, type=2)
                if result:
                    print "result form deathbycaptcha {}".format(result)
                    return result
                else:
                    print "None response from deathbycaptcha"
            except deathbycaptcha.AccessDeniedException:
                self._deathbycaptcha_client = None
            except Exception as e:
                print "Error from deathbycaptcha ({0})".format(e)
            time.sleep(INTERVAL)

    def report(self, captcha_id):
        try:
            self._client.report(captcha_id)
        except Exception as e:
                print "Error from deathbycaptcha when reporting wrong result ({0})".format(e)

    @property
    def _client(self):
        if not self._deathbycaptcha_client:
            self._deathbycaptcha_client = deathbycaptcha.SocketClient(self._username, self._password)
        return self._deathbycaptcha_client
