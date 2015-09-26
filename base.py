try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup

from utils import config
from exception import UnrecognizedIpchangeType

from dodatki.test import ip, ipchange
from dodatki.ekstra import send, log, openurl, saving
from dodatki.telnettt import zmiana


class Control(object):
    def __init__(self, sender):
        self._sender = sender()
        self._sender._log = self._log
        self.ip = ip()

    def loop(self):
        while 1:
            self.ip.stop()
            self.new()
            self.ip.start()
            self._change_ip()

    def _change_ip(self):
        change_type = config.get('main', 'IP_CHANGE')
        if change_type == 'neo':
            zmiana()
        elif change_type == 'play':
            ipchange()
        raise UnrecognizedIpchangeType("Invalid IP_CHANGE value in configuration file.")

    def new(self):
        action_info = self._get_action()
        if not self._verify_action(action_info):
            return
        self._log_new_action(action_info)
        self._sender.new_request(paragony=action_info['paragony'], **action_info['dane'])

    def _verify_action(self, action_info):
        if action_info['status']:
            return True
        elif not action_info['ip']:
            self._log(action_info['ip_msg'])
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
            self._log("Answer from server not in json format\n"
                      "----------\n{0}\n----------\n".format(repr(raw_action)))
            raise
        return action

    def _log(self, message):
        log(self._project_name + ".log", message)

    def _log_new_action(self, action_info):
        dane_string = " ".join("{0}:{1}; ".format(key, value) for key, value in action_info['dane'].items())
        paragon_count = len(action_info['paragony'])
        self._log("New action dane: {0}, applications sent: {1}".format(dane_string, paragon_count))


class OpenUrlWrapper(object):
    def __init__(self, _openurl):
        self.openurl = _openurl()

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
            soup = BeautifulSoup(self._response)
        except:
            # TODO: we should catch error here, when it occure we can debug and handle it.
            # soup = BeautifulSoup(self.response, "lxml")
            raise
        return soup

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
        saving(self.save_path.format(name), self.soup_response.prettify())


class BaseSender(object):
    _log = None

    def __init__(self):
        self._browser = OpenUrlWrapper(openurl)

    def new_request(self, **kwargs):
        self._browser.rebuild()
        paragony = kwargs.pop('paragony')
        for paragon in paragony:
            self.send(paragon=paragon, **kwargs)

    @property
    def p(self):
        """
        Hack to provide backward compatibility
        """
        return self._browser

    def send(self, *args, **kwargs):
        raise NotImplemented()

    def _get_cases(self):
        pass


# TODO: add decorator changing args to keyword args, preserve args order
# TODO: implement json discovery response somehow, with custom response parsing/handling
# TODO: use normal logging system based on logging module
# TODO: need smart, smooth download, resolve captcha system
# TODO: add configurable sleep between requests
# TODO: auto response event parsing
# TODO: class with default events
