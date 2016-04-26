import random
import time
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By

from web import WebElement, Button, Iframe, ImageWebElement, DriverFeed
from konkursy_base.captcha import DeathByCaptchaClient
from konkursy_base.utils import config


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

        if config.getint('selenium', 'minimal_browser'):
            profile.set_preference('permissions.default.image', 2)
            profile.set_preference('permissions.default.stylesheet', 2)
            profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
            profile.set_preference("network.http.pipelining", True)
            profile.set_preference("network.http.proxy.pipelining", True)
            profile.set_preference("network.http.pipelining.maxrequests", 8)
            profile.set_preference("content.notify.interval", 500000)
            profile.set_preference("content.notify.ontimer", True)
            profile.set_preference("content.switch.threshold", 250000)
            profile.set_preference("browser.cache.memory.capacity", 65536) # Increase the cache capacity.
            profile.set_preference("browser.startup.homepage", "about:blank")
            profile.set_preference("reader.parse-on-load.enabled", False) # Disable reader, we won't need that.
            profile.set_preference("browser.pocket.enabled", False) # Duck pocket too!
            profile.set_preference("loop.enabled", False)
            profile.set_preference("browser.chrome.toolbar_style", 1) # Text on Toolbar instead of icons
            profile.set_preference("browser.display.show_image_placeholders", False) # Don't show thumbnails on not loaded images.
            profile.set_preference("browser.display.use_document_colors", False) # Don't show document colors.
            profile.set_preference("browser.display.use_document_fonts", 0) # Don't load document fonts.
            profile.set_preference("browser.display.use_system_colors", True) # Use system colors.
            profile.set_preference("browser.formfill.enable", False) # Autofill on forms disabled.
            profile.set_preference("browser.helperApps.deleteTempFileOnExit", True) # Delete temprorary files.
            profile.set_preference("browser.shell.checkDefaultBrowser", False)
            profile.set_preference("browser.startup.homepage", "about:blank")
            profile.set_preference("browser.startup.page", 0) # blank
            profile.set_preference("browser.tabs.forceHide", True) # Disable tabs, We won't need that.
            profile.set_preference("browser.urlbar.autoFill", False) # Disable autofill on URL bar.
            profile.set_preference("browser.urlbar.autocomplete.enabled", False) # Disable autocomplete on URL bar.
            profile.set_preference("browser.urlbar.showPopup", False) # Disable list of URLs when typing on URL bar.
            profile.set_preference("browser.urlbar.showSearch", False) # Disable search bar.
            profile.set_preference("extensions.checkCompatibility", False) # Addon update disabled
            profile.set_preference("extensions.checkUpdateSecurity", False)
            profile.set_preference("extensions.update.autoUpdateEnabled", False)
            profile.set_preference("extensions.update.enabled", False)
            profile.set_preference("general.startup.browser", False)
            profile.set_preference("plugin.default_plugin_disabled", False)
            profile.set_preference("permissions.default.image", 2) # Image load disabled again
        profile.update_preferences()
        return webdriver.Firefox(firefox_profile=profile)


class GoogleCaptcha(DriverFeed):
    iframe_selector = WebElement("//iframe[@title='recaptcha widget']", by=By.XPATH)
    active_button = Button('recaptcha-anchor', by=By.ID)

    iframe_captcha = WebElement("//iframe[@style]", by=By.XPATH)
    banner = WebElement("rc-imageselect", by=By.ID)

    verify_button = Button('recaptcha-verify-button', by=By.ID)

    captcha_result = None

    def __init__(self, captcha_resolver=DeathByCaptchaClient):
        self.captcha_resolver = captcha_resolver()

    def solve(self):
        errors = 0
        while 1:
            try:
                self._solve()
                break
            except:
                errors +=1
                print "captcha error %s" % errors
                if errors >= 3:
                    raise
                time.sleep(5)

    def _solve(self):
        last_captcha_result = None
        self._activate()
        while 1:
            captcha_image, image_elements = self._get_images()
            captcha_result = self._get_selections(captcha_image)
            print "captcha result %s"%captcha_result
            if last_captcha_result and captcha_result['text'] == last_captcha_result['text']:
                print "Ponowne bledne rozwiazanie, zaznaczam 3 losowe"
                self._random_select(image_elements)
            else:
                self._select_boxes(image_elements, captcha_result['text'])
            with Iframe(self.driver, self.iframe_captcha):
                self.verify_button.element.click()
            time.sleep(5)
            if self._verify():
                print "captcha poprawna"
                return
            self._unselect_all()
            print "captcha bledna"
            self.captcha_resolver.report(captcha_result["captcha"])
            last_captcha_result = captcha_result

    def _get_selections(self, image):
        return self.captcha_resolver.resolve(image)

    def _select_boxes(self, image_elements, result):
        with Iframe(self.driver, self.iframe_captcha):
            for to_click in eval(result):
                matched = self._match_box(to_click, image_elements)
                if matched:
                    matched.web_element.click()
                else:
                    print "{} not matched".format(to_click)

    def _random_select(self, image_elements):
        with Iframe(self.driver, self.iframe_captcha):
            for x in range(3):
                random.choice(image_elements).web_element.click()

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
            while 1:
                a = [x for x in self.driver.find_elements(By.CLASS_NAME, "rc-imageselect-tileselected")]
                if not a:
                    break
                for element in a:
                    element.find_element(By.CLASS_NAME, "rc-image-tile-wrapper").click()
                print "Unselected %s elements" % len(a)

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




