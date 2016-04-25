import inspect
import re
from functools import partial

from base import OpenUrlWrapper
from exception import MissingMethod, UnknownResponse

ALL_ACTION_METHODS = ('send', 'pre_request', 'pre_send', 'clean', 'after_requests')


class ResponseSignals:
    SUCCESS = 1
    RESEND = 2
    CAPTCHA = RESEND
    FULLRESEND = 3


def resend(signal=ResponseSignals.RESEND):
    def pre_wrapper(method):
        def wrapper(*args, **kwargs):
            while 1:
                response = method(*args, **kwargs)
                if response == signal:
                    continue
                return response
        return wrapper
    return pre_wrapper


class BaseSender(object):
    _log = None
    request = None
    current_bill = None
    _browser_cls = OpenUrlWrapper

    def __init__(self):
        self._browser = self._browser_cls()

    def new_request(self, **kwargs):
        self._pre_request()
        bills = kwargs.pop('paragony')
        no_rebuild = kwargs.pop('product1', None)

        self.request = kwargs
        for bill in bills:
            self._log("Sending bill %s" % bill)
            self.current_bill = bill
            self._send_request(paragon=bill, **kwargs)
            self._clean()
        self._after_requests()
        if not no_rebuild:
            self._browser.rebuild()

    @classmethod
    def change_browser(self, new_browser):
        # TODO: wirte unittest
        self._browser_cls = new_browser

    @resend(ResponseSignals.FULLRESEND)
    def _send_request(self, *args, **kwargs):
        self._pre_send()
        return self._send(*args, **kwargs)

    @property
    def p(self):
        """
        Hack to provide backward compatibility
        """
        return self._browser

    @resend()
    def _pre_request(self):
        return self.pre_request()

    def pre_request(self):
        pass

    @resend()
    def _pre_send(self):
        return self.pre_send()

    def pre_send(self):
        pass

    @resend()
    def _send(self, *args, **kwargs):
        return self.send(*args, **kwargs)

    def send(self, *args, **kwargs):
        raise NotImplementedError()

    @resend()
    def _clean(self):
        return self.clean()

    def clean(self):
        pass

    @resend()
    def _after_requests(self):
        return self.after_requests()

    def after_requests(self):
        pass


def responsable(method):
    method.responsable = True
    return method


class ResponseMatchSender(BaseSender):

    def __new__(cls, *args, **kwargs):
        self = super(ResponseMatchSender,
                     cls).__new__(cls, *args, **kwargs)
        cls._init_methods(self)
        return self

    def __init__(self):
        self._verify_callbacks()
        super(ResponseMatchSender, self).__init__()

    @classmethod
    def _init_methods(cls, self):
        for method in ALL_ACTION_METHODS:
            callable_method = resend()(partial(self._process_response,
                                               getattr(self, method)))
            setattr(self, method, callable_method)

    def _get_method(self, name):
        method_format = 'RESULT_{0}'
        return getattr(self, method_format.format(name))

    def _verify_callbacks(self):
        for pattern in self._get_all_patterns():
            try:
                self._get_method(pattern['method'])
            except AttributeError:
                raise MissingMethod("Missing method {0}".format(pattern))

    def _get_all_patterns(self):
        pattern_suffix = "^PATTERN_(.*)$"

        matches = filter(None, [re.match(pattern_suffix, attr)
                                for attr in dir(self)])
        patterns = [{'method': match.group(1),
                 'pattern': getattr(self, match.group(0))} for match in matches if getattr(self, match.group(0))]

        unknow = [pattern for pattern in patterns if pattern['method'] == 'unknown'][0]
        patterns.remove(unknow)
        patterns.append(unknow)

        return patterns

    def _match_response(self, response):
        for pattern in self._get_all_patterns():
            if re.match(pattern['pattern'], response):
                return self._get_method(pattern['method'])

    def _process_response(self, method, *args, **kwargs):
        response = method(*args, **kwargs)
        if not hasattr(method, 'responsable') or not method.responsable:
            return response
        response_method = self._match_response(response)
        if not response_method:
            raise UnknownResponse(method)
        return response_method()

    @responsable
    def send(self, *args, **kwargs):
        return super(ResponseMatchSender, self).send(*args, **kwargs)


class ResponseSender(ResponseMatchSender):
    PATTERN_wrong_captcha = None
    PATTERN_duplicate = None
    PATTERN_success = None
    PATTERN_unknown = r".*"

    def RESULT_wrong_captcha(self):
        pass

    def RESULT_duplicate(self):
        self._log("Duplicated bill")

    def RESULT_success(self):
        self._log("Successful registered")

    def RESULT_unknown(self):
        pass

    def _process_response(self, method, *args, **kwargs):
        try:
            return super(ResponseSender,
                         self)._process_response(method, *args, **kwargs)
        except UnknownResponse:
            return self.RESULT_unknown()

    def send(self, *args, **kwargs):
        raise NotImplementedError


def send_args(func):
    args = inspect.getargspec(func)
    if args.defaults:
        raise TypeError("wrapped function {0}() can't have keyword arguments".format(func.__name__))

    def wrapper(self, **kwargs):
        kwargs.update({"self": self})
        test_args = list(args.args)
        map(test_args.remove, [arg for arg in kwargs.keys() if arg in test_args])
        if test_args:
            raise TypeError("Function {0}() require arguments: {1}".format(func.__name__, ", ".join(test_args)))

        arguments = (kwargs[arg] for arg in args.args)
        return func(*arguments)

    return wrapper
