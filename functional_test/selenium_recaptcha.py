from mock import Mock

from selenium_browser.senders import GoogleCaptcha, SeleniumOpener
from selenium_browser.web import DriverFeed


captcha = Mock()
captcha().resolve.return_value = {u'status': 0, u'captcha': 893468, u'text': u'[[48,194],[365,194],[57,439],[360,468]]', u'is_correct': True}


class FunctionalTest(DriverFeed):
    g = GoogleCaptcha(captcha)

    def start(self):
        self.g.solve()


if __name__ == '__main__':
    driver = SeleniumOpener()
    driver.open("http://www.carex-loteria.pl/")
    t = FunctionalTest(driver=driver)
    t.start()
