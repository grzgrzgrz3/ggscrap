try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup

from utils import config
from exception import UnrecognizedIpchangeType

from dodatki.test import ip, ipchange
from dodatki.ekstra import send, log, openurl, saving
from dodatki.telnettt import zmiana
from log import logger


class Control(object):
    def __init__(self, sender):
        self._sender = sender()
        self._sender._control = self
        self.ip = ip()

    def loop(self):
        try:
            self._loop()
        except:
            logger.exception("Exception on top")
            raise

    def _loop(self):
        while 1:
            self.new_request()

    def new_request(self):
        self.ip.stop()
        self._get_request()
        self.ip.start()
        self._change_ip()

    def _change_ip(self):
        change_type = config.get('main', 'IP_CHANGE')
        if change_type == 'neo':
            zmiana()
        elif change_type == 'play':
            ipchange()
        else:
            raise UnrecognizedIpchangeType("Invalid IP_CHANGE value in configuration file.")

    def _get_request(self):
        action_info = self._get_action()
        if not self._verify_action(action_info):
            return
        self._log_new_action(action_info)
        self._sender.new_request(paragony=action_info['paragony'], **action_info['dane'])

    def _verify_action(self, action_info):
        if action_info['status']:
            return True
        elif not action_info['ip']:
            logger.debug("Ip message: %s", action_info['ip_msg'])
            return False
        else:
            # TODO: Need to implement sleep. Problem is that we need to free lock on ipchange during sleep
            pass

    @property
    def _project_name(self):
        return self._sender.__class__.__name__.lower()

    def _get_action(self):
        raw_action = send([self._project_name, 'nowa_sesja'])
        try:
            action = eval(raw_action)
        except SyntaxError:
            logger.exception("Answer from server not in json format: %s", repr(raw_action))
            raise
        return action

    def _log_new_action(self, action_info):
        dane_string = u" ".join(u"{0}:{1}; ".format(key, value) for key, value in action_info['dane'].items())
        paragon_count = len(action_info['paragony'])
        logger.info("New action dane: %s, applications sent: %s", dane_string, paragon_count)


class OpenUrlWrapper(object):
    def __init__(self, wrapped_object=openurl):
        self.openurl = wrapped_object()

    @property
    def otworz(self):
        """
        Backward compatibility
        """
        return self.open

    def open(self, *args, **kwargs):
        return Response(self.openurl.otworz(*args, **kwargs))

    def __getattr__(self, item):
        return getattr(self.openurl, item)


class Response(object):
    save_path = "html/{0}.html"

    def __init__(self, response):
        self._response = response

    @property
    def soup_response(self):
        try:
            return BeautifulSoup(self._response)
        except:
            # TODO: we should catch error here, when it occure we can debug and handle it.
            # soup = BeautifulSoup(self.response, "lxml")
            raise

    @property
    def text(self):
        return self._response

    @property
    def dict_response(self):
        return eval(self._response)

    def inputs(self, **kwargs):
        debug = kwargs.pop('debug', False)
        form = self.soup_response.find('form', kwargs)
        inputs = form.findAll('input')
        inputs_json = {}
        for x in inputs:
            if x:
                if x.has_attr('name'):
                    inputs_json.update({x["name"]: x.get("value", "").encode('utf-8')})
                    if debug:
                        print {x["name"]: x.get("value", "")}
                else:
                    if debug:
                        print "no_name_input:", x
            else:
                # TODO: not sure if this can happen, remove it if we do not caught it for some time.
                print x
                raise Exception("Weird we found empty? input!")
        return inputs_json

    def save(self, name):
        saving(self.save_path.format(name), self.soup_response.prettify().encode('utf8'))

    def binary_save(self, path):
        saving(path, self._response)

# TODO: implement json discovery response somehow, with custom response parsing/handling
# TODO: need smart, smooth download, resolve captcha system
# TODO: add configurable sleep between requests
# TODO: auto response event parsing
# TODO: class with default events
