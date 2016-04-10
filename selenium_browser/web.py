import base64
import cStringIO

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By


def locate_element(driver, locator, by):
    return WebDriverWait(driver, 30).until(
            expected_conditions.presence_of_element_located((by, locator)))


class DriverFeed(object):
    driver = None

    def __new__(cls, *args, **kwargs):
        driver = kwargs.pop('driver', None)
        if driver:

            cls.init_webs(driver)
        self = super(DriverFeed, cls).__new__(cls, *args, **kwargs)
        self.driver = driver
        return self

    @classmethod
    def init_webs(cls, driver):
        __dict__ = {}
        __dict__.update(cls.__dict__)
        for key, value in __dict__.items():
            if isinstance(value, DriverFeed):
                value.setup_driver(driver)
                value.init_webs(driver)

    def setup_driver(self, driver):
        self.driver = driver


class WebElement(DriverFeed):
    _locator = None

    def __init__(self, locator, by=By.XPATH):
        self._locator = locator
        self._by = by

    @property
    def element(self):
        answer = locate_element(self.driver, self._locator, self._by)
        return answer

    def __getattr__(self, item):
        return self.element.get_attribute(item)


class CheckBoxElement(WebElement):

    def __set__(self, instance, value):
        self.driver = instance.driver
        if bool(value) != self.checked:
            try:
                self.element.click()
            except WebDriverException as e:
                if 'Element is not clickable at point' in e.msg:
                    self.driver.execute_script('$("#{sel}").click()'.format(sel=self._locator))
                else:
                    raise

    def __get__(self, instance, owner):
        self.driver = instance.driver
        return self.checked

    @property
    def checked(self):
        return self.element.is_selected()


class InputBox(WebElement):

    def __set__(self, instance, value):
        self._driver = instance.driver
        self.element.send_keys(str(value))

    def __get__(self, instance, owner):
        self._driver = instance.driver
        return self.value

    @property
    def element(self):
        answer = locate_element(self._driver, self._locator, self._by)
        return answer


class Iframe(object):

    def __init__(self, driver, iframe):
        self.driver = driver
        self.iframe = iframe

    def __enter__(self):
        self.driver.switch_to.frame(self.iframe.element)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.switch_to.parent_frame()


class Button(WebElement):
    def submit(self, scroll=False):
        if scroll:
            position = self.element.location['y']
            widow_size = self.driver.get_window_size()['height']
            center = position - (widow_size/2)
            print "widow_size: %s, postion: %s"% (widow_size, position)
            print "Scrolling to %s" % center
            self.driver.execute_script("scroll(0,%s)" % center)
        self.element.click()


class Option(WebElement):
    def select_by_index(self, index):
        select = Select(self.element)
        select.select_by_index(index)


class Text(WebElement):

    @property
    def text(self):
        return self.element.text

class ImageWebElement(object):
    # TODO: Seperate ImageWeb and BoxWeb

    def __init__(self, web_element, full_screenshot, iframe=(0, 0)):
        self.web_element = web_element
        self.full_screenshot = full_screenshot
        self.iframe = iframe

    def base64(self):
        image_buffer = cStringIO.StringIO()
        image = self._crop_image()
        image.save(image_buffer, 'PNG')
        return base64.b64encode(image_buffer.getvalue())

    def save(self, name):
        image = self._crop_image()
        image.save(name, 'JPEG')

    def _crop_image(self):
        position = (self.x_position, self.y_position,
                    self.x_position+self.width, self.y_position+self.height)
        return self.full_screenshot.crop(position)

    @property
    def width(self):
        return self.web_element.size['width']

    @property
    def height(self):
        return self.web_element.size['height']

    def inside(self, cords):
        x = cords[0]
        y = cords[1]
        return x in self.x_cords and y in self.y_cords

    @property
    def x_cords(self):
        x_relativ_pos = int(self.web_element.location['x'])
        return range(x_relativ_pos, x_relativ_pos+self.width)

    @property
    def y_cords(self):
        y_relativ_pos = int(self.web_element.location['y'])
        return range(y_relativ_pos, y_relativ_pos+self.height)

    @property
    def x_position(self):
        return self.iframe[0] + int(self.web_element.location['x'])

    @property
    def y_position(self):
        return self.iframe[1] + int(self.web_element.location['y'])
