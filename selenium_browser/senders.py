import time
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By

from web import WebElement, Button, Iframe, ImageWebElement, DriverFeed
from konkursy_base.captcha import DeathByCaptchaClient


class SeleniumOpener(object):
    _driver = None
    save_path = "html/{0}.html"

    def rebuild(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    def open(self, url):
        self.driver.get(url)

    @property
    def driver(self):
        if not self._driver:
            self._driver = self._get_driver()
        return self._driver

    def save(self, name):
        self.driver.save_screenshot(self.save_path.format(name))

    def __getattr__(self, item):
        return getattr(self.driver, item)

    def _get_driver(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference("intl.accept_languages", "en-us")
        profile.update_preferences()
        return webdriver.Firefox(firefox_profile=profile)


class GoogleCaptcha(DriverFeed):
    iframe_selector = WebElement("//div[@id='recaptcha1']//iframe", by=By.XPATH)
    active_button = Button('recaptcha-anchor', by=By.ID)

    iframe_captcha = WebElement("//iframe[@style]", by=By.XPATH)
    banner = WebElement("rc-imageselect", by=By.ID)

    verify_button = Button('recaptcha-verify-button', by=By.ID)

    def __init__(self, captcha_resolver=DeathByCaptchaClient):
        super(GoogleCaptcha, self).__init__()
        self.captcha_resolver = captcha_resolver()

    def solve(self):
        self._activate()
        while 1:
            captcha_image, image_elements = self._get_images()
            self._unselect_all()
            result = self.captcha_resolver.resolve(captcha_image)
            with Iframe(self.driver, self.iframe_captcha):
                for to_click in eval(result['text']):
                    matched = self._match_box(to_click, image_elements)
                    if matched:
                        matched.web_element.click()
                    else:
                        print "{} not matched".format(to_click)
                self.verify_button.element.click()
            time.sleep(5)
            if self._verify():
                print "captcha poprawna"
                return
            print "captcha bledna"
            self.captcha_resolver.report(result["captcha"])

    def _verify(self):
        with Iframe(self.driver, self.iframe_selector):
            if self.driver.find_elements(By.XPATH, '//span[@aria-checked="true"]'):
                return True
        return False

    def _match_box(self, cord, boxes):
        for box in boxes:
            if box.inside(cord):
                return box
        return None

    def _activate(self):
        with Iframe(self.driver, self.iframe_selector):
            self.active_button.submit()

    def _unselect_all(self):
        with Iframe(self.driver, self.iframe_captcha):
            [x.click() for x in self.driver.find_elements(By.CLASS_NAME, "rc-imageselect-tileselected")]

    def _get_images(self):
        self.driver.save_screenshot('screenshot.png')
        iframe_pos = (self.iframe_captcha.element.location['x'],
                      self.iframe_captcha.element.location['y'])
        with Iframe(self.driver, self.iframe_captcha):
            captcha_boxes = self.driver.find_elements(By.CLASS_NAME, "rc-image-tile-wrapper")
            image_elements = [ImageWebElement(image, None) for image in captcha_boxes]
            self.driver.save_screenshot('screenshot.png')
            image = Image.open('screenshot.png')
            banner = ImageWebElement(self.banner.element, image, iframe_pos)
            banner.save("captcha.jpeg")
            return "captcha.jpeg", image_elements


if __name__ == '__main__':
    driver = SeleniumOpener()
    driver.open("https://www.zakreckubkiem.pl/")
    g = GoogleCaptcha(driver=driver)
    g.solve()
