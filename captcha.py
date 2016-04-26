import re
import time

import deathbycaptcha
from utils import config

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

    def resolve(self, path, solve_type=2):
        for x in range(TRIES):
            try:
                if solve_type:
                    result = self._client.decode(path, type=solve_type)
                else:
                    result = self._client.decode(path, 60)
                if result:
                    print "result form deathbycaptcha {}".format(result)
                    return result
                else:
                    print "None response from deathbycaptcha"
            except deathbycaptcha.AccessDeniedException:
                print "deathbycaptcha.AccessDeniedException"
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


class Recaptcha(object):
    _path = 'html/recaptcha.png'

    def __init__(self, response, p, client):
        self.response = response
        self.p = p
        self.client = client()
        self.result = None

    def solve(self):
        image_data = self.p.open(self._image_url, None, "lastnot")
        image_data.binary_save(self._path)

        self.result = self.client.resolve(self._path)

    def inputs(self):
        return {"recaptcha_challenge_field": self._challenge,
                "recaptcha_response_field": self.result["text"]}

    def report(self):
        self.client.report(self.result['captcha'])

    @property
    def _image_url(self):
        base = "http://www.google.com/recaptcha/api/image?c={0}"
        self._challenge = self._get_challenge()
        return base.format(self._challenge)

    def _get_challenge(self):
        url = self._api_url()
        response = self.p.open(url, None, "lastnot").text
        return re.search("\s+challenge\s+: '(.*?)'", response).group(1)

    def _api_url(self):
        all_src = [result['src'] for result in self.response.soup_response.findAll("script") if result.has_attr('src')]
        google_src = [src for src in all_src if "challenge" in src][0]
        return "http:" + google_src
