from exception import UnrecognizedIpchangeType
from utils import config
from dodatki.test import ip, ipchange
from dodatki.ekstra import send, log, openurl
from dodatki.telnettt import zmiana

class Control(object):

    def __init__(self, sender):
        self._sender = sender()
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
        raw_action = send(['nowa_sesja', self._project_name])
        try:
            action = eval(raw_action)
        except SyntaxError:
            self._log("Answer from serwer not in json format\n"
                      "----------\n{0}\n----------\n".format(repr(raw_action)))
            raise
        return action

    def _log(self, message):
        log(self._project_name, message)

    def _log_new_action(self, action_info):
        dane_string = " ".join("{0}:{1}; ".format(key, value) for key, value in action_info['dane'].items())
        paragon_count = len(action_info['paragony'])
        self._log("New action dane: {0}, ilosc zgloszen: {1}".format(dane_string, paragon_count))


class BaseSender(object):

    def __init__(self):
        self.p = openurl()

    def new_request(self, **kwargs):
        self.p.rebuild()
        paragony = kwargs.pop('paragony')
        for paragon in paragony:
            self.send(paragon=paragon, **kwargs)

    def send(self, *args, **kwargs):
        raise NotImplemented()

    def _get_cases(self):
        pass












